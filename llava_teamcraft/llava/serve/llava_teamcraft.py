import torch
import os
import io
import numpy as np

from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
from llava.conversation import conv_templates, SeparatorStyle
from llava.model.builder import load_pretrained_model
from llava.utils import disable_torch_init
from llava.mm_utils import process_images, tokenizer_image_token, get_model_name_from_path

from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import requests
from PIL import Image
from io import BytesIO
from transformers import TextStreamer


class ModelRunner:
    def __init__(
        self,
        model_path,
        model_base=None,
        device="cuda",
        conv_mode=None,
        temperature=0.2,
        max_new_tokens=512,
        load_8bit=False,
        load_4bit=False,
    ):
        # Model setup
        disable_torch_init()

        self.model_path = model_path
        self.model_base = model_base
        self.device = device
        self.conv_mode = conv_mode
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.load_8bit = load_8bit
        self.load_4bit = load_4bit

        # Hard code model name here. @TeamCraft
        self.model_name = "llava-v1.6-vicuna-7b"
        # self.model_name = get_model_name_from_path(self.model_path)
        self.tokenizer, self.model, self.image_processor, self.context_len = load_pretrained_model(
            self.model_path, self.model_base, self.model_name, self.load_8bit, self.load_4bit, device=self.device
        )

        # Determine conversation mode based on the model name
        if "llama-2" in self.model_name.lower():
            inferred_conv_mode = "llava_llama_2"
        elif "mistral" in self.model_name.lower():
            inferred_conv_mode = "mistral_instruct"
        elif "v1.6-34b" in self.model_name.lower():
            inferred_conv_mode = "chatml_direct"
        elif "v1" in self.model_name.lower():
            inferred_conv_mode = "llava_v1"
        elif "mpt" in self.model_name.lower():
            inferred_conv_mode = "mpt"
        else:
            inferred_conv_mode = "llava_v0"

        if self.conv_mode is not None and inferred_conv_mode != self.conv_mode:
            # print(
            #     '[WARNING] the auto-inferred conversation mode is {}, while `conv_mode` is {}, using {}'.format(
            #         inferred_conv_mode, self.conv_mode, self.conv_mode
            #     )
            # )
            pass
        else:
            self.conv_mode = inferred_conv_mode

        self.conv = conv_templates[self.conv_mode].copy()
        self.roles = ('user', 'assistant') if "mpt" in self.model_name.lower() else self.conv.roles

    def run_once(self, inp, images=None):
        if not inp:
            raise ValueError("No input provided")

        self.conv = conv_templates[self.conv_mode].copy()
        self.roles = ('user', 'assistant') if "mpt" in self.model_name.lower() else self.conv.roles

        if images is not None and images!=[]:
            # If images are numpy arrays, convert them to PIL Images    
            if isinstance(images, np.ndarray):
                images = [Image.fromarray(images)]
            elif isinstance(images, list) and isinstance(images[0], np.ndarray):
                images = [Image.fromarray(img_array) for img_array in images]
            elif isinstance(images, bytes):
                # If images are bytes, load them using BytesIO
                images = [Image.open(io.BytesIO(images)).convert('RGB')]
            elif isinstance(images, list) and isinstance(images[0], bytes):
                images = [Image.open(io.BytesIO(img_data)).convert('RGB') for img_data in images]
            else:
                raise ValueError("Images must be either ndarray or bytes stream")
            
            image_size = images[0].size
            # print(f"Image size: {image_size}")
            image_tensor = process_images(images, self.image_processor, self.model.config)
            if isinstance(image_tensor, list):
                image_tensor = [image.to(self.model.device, dtype=torch.float16) for image in image_tensor]
            else:
                image_tensor = image_tensor.to(self.model.device, dtype=torch.float16)
        else:
            images = None
            image_size = None
            image_tensor = None

        # print(f"{self.roles[1]}: ", end="")

        if images is not None:
            # Handle image input
            if self.model.config.mm_use_im_start_end:
                new_inp = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN + '\n' + inp[0]
            else:
                new_inp = DEFAULT_IMAGE_TOKEN + '\n' + inp[0]
            self.conv.append_message(self.conv.roles[0], new_inp)
        else:
            self.conv.append_message(self.conv.roles[0], inp[0])

        for i in range(1, len(inp)):
            self.conv.append_message(self.conv.roles[i % 2], inp[i])

        self.conv.append_message(self.conv.roles[1], None)
        # print(self.conv, 'conv')

        prompt = self.conv.get_prompt()

        input_ids = tokenizer_image_token(
            prompt, self.tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt'
        ).unsqueeze(0).to(self.model.device)
        stop_str = self.conv.sep if self.conv.sep_style != SeparatorStyle.TWO else self.conv.sep2

        with torch.inference_mode():
            output_ids = self.model.generate(
                input_ids,
                images=image_tensor,
                image_sizes=[image_size] if image_size else None,
                do_sample=True if self.temperature > 0 else False,
                temperature=self.temperature,
                max_new_tokens=self.max_new_tokens
            )

        outputs = self.tokenizer.decode(output_ids[0]).strip()
        self.conv.messages[-1][-1] = outputs

        return outputs

import argparse
import torch
import os

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

from flask import Flask, request, jsonify
app = Flask(__name__)

# Globals to maintain state across requests
model = None
tokenizer = None
image_processor = None
context_len = None
roles = None
conv = None
conv_mode = None
model_name = None

def load_image(image_file):
    if image_file.startswith('http://') or image_file.startswith('https://'):
        response = requests.get(image_file)
        image = Image.open(BytesIO(response.content)).convert('RGB')
    else:
        image = Image.open(image_file).convert('RGB')
    return image


def setup(args):
    global model, tokenizer, image_processor, context_len, roles, conv, conv_mode, model_name

    # Model setup
    disable_torch_init()

    model_name = get_model_name_from_path(args.model_path)
    tokenizer, model, image_processor, context_len = load_pretrained_model(args.model_path, args.model_base, model_name, args.load_8bit, args.load_4bit, device=args.device)

    # Determine conversation mode based on the model name
    if "llama-2" in model_name.lower():
        conv_mode = "llava_llama_2"
    elif "mistral" in model_name.lower():
        conv_mode = "mistral_instruct"
    elif "v1.6-34b" in model_name.lower():
        conv_mode = "chatml_direct"
    elif "v1" in model_name.lower():
        conv_mode = "llava_v1"
    elif "mpt" in model_name.lower():
        conv_mode = "mpt"
    else:
        conv_mode = "llava_v0"

    if args.conv_mode is not None and conv_mode != args.conv_mode:
        print('[WARNING] the auto inferred conversation mode is {}, while `--conv-mode` is {}, using {}'.format(conv_mode, args.conv_mode, args.conv_mode))
    else:
        args.conv_mode = conv_mode

    
    

@app.route('/run', methods=['POST'])
def run_once():
    global conv, roles
    conv = conv_templates[args.conv_mode].copy()
    roles = ('user', 'assistant') if "mpt" in model_name.lower() else conv.roles
    inp = request.form.getlist('input')
    print(inp,'inp')
    # image_file = request.json.get('image')
    if not inp:
        return jsonify({"error": "No input provided"}), 400
    
    if 'images' in request.files:
        
        files = request.files.getlist('images')

        # List to store the file paths of saved images
        file_paths = []
        
        for file in files:
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400

            if file:
                filename = file.filename
                file_path = os.path.join('./server_data', filename)
                file.save(file_path)
                file_paths.append(file_path)
            else:
                return jsonify({"error": "No file error"}), 400

        images = [load_image(file_path) for file_path in file_paths]
        
        ####### TODO: Add your handle of images here @乾隆 #############
        image_size = images[0].size
        print(image_size)
        image_tensor = process_images(images, image_processor, model.config)
        image_tensor = [image.to(model.device, dtype=torch.float16) for image in image_tensor] if type(image_tensor) is list else image_tensor.to(model.device, dtype=torch.float16)
    else:
        images = None
        image_size = None
        image_tensor = None
        # image_tensor = process_images(images, image_processor, model.config)
        # image_tensor = [image.to(model.device, dtype=torch.float16) for image in image_tensor] if type(image_tensor) is list else image_tensor.to(model.device, dtype=torch.float16)
        
    print(f"{roles[1]}: ", end="")

    if images is not None:
        # Handle image input
        if model.config.mm_use_im_start_end:
            new_inp = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN + '\n' + inp[0]
        else:
            new_inp = DEFAULT_IMAGE_TOKEN + '\n' + inp[0]
        conv.append_message(conv.roles[0], new_inp)
        image = None
    else:
        conv.append_message(conv.roles[0], inp[0])
        
    for i in range(1,len(inp)):
        conv.append_message(conv.roles[i%2], inp[i])
    conv.append_message(conv.roles[1], None)
    print(conv,'conv')

    prompt = conv.get_prompt()

    input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).to(model.device)
    stop_str = conv.sep if conv.sep_style != SeparatorStyle.TWO else conv.sep2

    with torch.inference_mode():
        output_ids = model.generate(
            input_ids,
            images=image_tensor,
            image_sizes=[image_size],
            do_sample=True if args.temperature > 0 else False,
            temperature=args.temperature,
            max_new_tokens=args.max_new_tokens)

    outputs = tokenizer.decode(output_ids[0]).strip()
    conv.messages[-1][-1] = outputs

    return jsonify({"response": outputs})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, default="facebook/opt-350m")
    parser.add_argument("--model-base", type=str, default=None)
    parser.add_argument("--image-file", type=str)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--conv-mode", type=str, default=None)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--load-8bit", action="store_true")
    parser.add_argument("--load-4bit", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    setup(args)
    app.run(debug=args.debug, port=8001)
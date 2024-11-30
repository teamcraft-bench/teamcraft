import os.path
import time
import warnings
from typing import SupportsFloat, Any, Tuple, Dict

import requests
import json

import gymnasium as gym
from gymnasium.core import ObsType

from PIL import Image
import numpy as np
import io
import base64


import teamcraft.utils as U

from .minecraft_launcher import MinecraftInstance
from .process_monitor import SubprocessMonitor


class teamCraftEnv(gym.Env):
    def __init__(
        self,
        agent_count=None,
        mc_port=None,
        server_host="http://127.0.0.1",
        server_port=3000,
        request_timeout=600,
        log_path="./logs",
    ):
        if agent_count is None:
            raise ValueError("Agent count must be provided")
        if agent_count > 4:
            raise ValueError("Agent count > 4 is currently not supported")
        if not mc_port:
            raise ValueError("mc_port must be specified")
        self.agent_count = agent_count
        self.mc_port = mc_port
        self.server = f"{server_host}:{server_port}"
        self.server_port = server_port
        self.request_timeout = request_timeout
        self.log_path = log_path
        self.mineflayer = self.get_mineflayer_process(server_port)
        self.mc_instance = None
        self.has_reset = False
        self.reset_options = None
        self.connected = False
        self.server_paused = False

    def get_mineflayer_process(self, server_port):
        U.f_mkdir(self.log_path, "mineflayer")
        file_path = os.path.abspath(os.path.dirname(__file__))
        print("server port debug: ", server_port)
        mineflayer_index = "index.js" if self.agent_count <= 3 else "index_4agents.js"
        print("mineflayer index file: ", mineflayer_index, "is used")
        return SubprocessMonitor(
            commands=[
                "node",
                U.f_join(file_path, f"mineflayer/{mineflayer_index}"),
                str(server_port),
            ],
            name="mineflayer",
            ready_match=r"Server started on port (\d+)",
            log_path=U.f_join(self.log_path, "mineflayer"),
        )
        

    def check_process(self):
        if self.mc_instance and not self.mc_instance.is_running:
            # if self.mc_instance:
            #     self.mc_instance.check_process()
            #     if not self.mc_instance.is_running:
            print("Starting Minecraft server")
            self.mc_instance.run()
            self.mc_port = self.mc_instance.port
            self.reset_options["port"] = self.mc_instance.port
            print(f"Server started on port {self.reset_options['port']}")
        retry = 0
        while not self.mineflayer.is_running:
            # print("Mineflayer process has exited, restarting")
            self.mineflayer.run()
            if not self.mineflayer.is_running:
                if retry > 3:
                    raise RuntimeError("Mineflayer process failed to start")
                else:
                    continue
            print(self.mineflayer.ready_line)
            res = requests.post(
                f"{self.server}/start",
                json=self.reset_options,
                timeout=self.request_timeout,
            )
            if res.status_code != 200:
                self.mineflayer.stop()
                raise RuntimeError(
                    f"Minecraft server reply with code {res.status_code}"
                )
            return res.json()

    def step(
        self,
        code: str,
        programs: str = "",
    ) -> Tuple[ObsType, SupportsFloat, bool, bool, Dict[str, Any]]:
        if not self.has_reset:
            raise RuntimeError("Environment has not been reset yet")
        self.check_process()
        # self.unpause()
        data = {
            "code": code,
            "programs": programs,
        }
        res = requests.post(
            f"{self.server}/step", json=data, timeout=self.request_timeout
        )
        if res.status_code != 200:
            raise RuntimeError("Failed to step Minecraft server")
        returned_data = res.json()
        # self.pause()
        returned = {}
        for key, value in returned_data.items():
            returned[key] = json.loads(value)
        return returned

    def render(self):
        try:
            res = requests.post(
                f"{self.server}/render", json={}, timeout=self.request_timeout
            )
            res.raise_for_status()
            
            data = res.json()
            images_base64 = data.get('images', {})

            image_arrays = {}
            for bot_id, img_base64 in images_base64.items():
                img_data = base64.b64decode(img_base64)
                image = Image.open(io.BytesIO(img_data)).convert('RGB')
                image_array = np.array(image)
                image_arrays[bot_id] = image_array

            return image_arrays
        
        except requests.exceptions.RequestException as e:
            print(f"HTTP Request failed: {e}")
            return None
        except IOError as e:
            print(f"Image processing failed: {e}")
            return None
            
            
    def reset(
        self,
        *,
        seed=None,
        options=None,
    ) -> Tuple[ObsType, Dict[str, Any]]:
        if options is None:
            options = {}

        if options.get("inventory", {}) and options.get("mode", "hard") != "hard":
            raise RuntimeError("inventory can only be set when options is hard")
        print('position: ', options.get("position", None))
        self.reset_options = {
            "port": self.mc_port,
            "reset": options.get("mode", "hard"),
            "inventory": options.get("inventory", {}),
            "equipment": options.get("equipment", []),
            "spread": options.get("spread", False),
            "waitTicks": options.get("wait_ticks", 5),
            "position": options.get("position", None),
        }

        # self.unpause()
        self.mineflayer.stop()
        time.sleep(1)  # wait for mineflayer to exit

        returned_data = self.check_process()
        self.has_reset = True
        self.connected = True
        # All the reset in step will be soft
        self.reset_options["reset"] = "soft"
        # self.pause()
        returned = {}
        for key, value in returned_data.items():
            returned[key] = json.loads(value)
        return returned

    def close(self):
        # self.unpause()
        if self.connected:
            res = requests.post(f"{self.server}/stop")
            if res.status_code == 200:
                self.connected = False
        if self.mc_instance:
            self.mc_instance.stop()
        self.mineflayer.stop()
        return not self.connected

    def pause(self):
        if self.mineflayer.is_running and not self.server_paused:
            res = requests.post(f"{self.server}/pause")
            if res.status_code == 200:
                self.server_paused = True
        return self.server_paused

    def unpause(self):
        if self.mineflayer.is_running and self.server_paused:
            res = requests.post(f"{self.server}/pause")
            if res.status_code == 200:
                self.server_paused = False
            else:
                print(res.json())
        return self.server_paused
    def set_server_state(self, server_paused):
        self.server_paused = server_paused

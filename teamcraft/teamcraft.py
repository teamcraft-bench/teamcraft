import copy
from typing import Dict
from .env import teamCraftEnv
from .actions import load_atomic_actions
from .utils import construct_action_str, extract_obs

class teamCraft:
    def __init__(
        self,
        mc_port: int = None,
        server_port: int = 3000,
        env_wait_ticks: int = 20,
        env_request_timeout: int = 600,
        max_iterations: int = 160,
        resume: bool = False,
        agent_count: int = 3,
        log_path: str = "./logs",
    ):
        # init env
        self.env = teamCraftEnv(
            agent_count = agent_count,
            mc_port=mc_port,
            server_port=server_port,
            request_timeout=env_request_timeout,
            log_path = log_path,
        )
        self.env_wait_ticks = env_wait_ticks
        self.max_iterations = max_iterations
        self.resume = resume
        self.atomic_actions = load_atomic_actions()
        self.programs = ""
        for atomic_action in self.atomic_actions:
            self.programs += f"{atomic_action}\n\n"
        self.last_events = None
        self.time_step = 0
        self.obversation = None
        

    def reset(self, task, context="", reset_env=True):
        if reset_env:
            self.env.reset(
                options={
                    "mode": "soft",
                    "wait_ticks": self.env_wait_ticks,
                }
            )
    
    def reset_agent(self, bot_list=['bot1', 'bot2', 'bot3', 'bot4']):
        self.time_step = 0
        self.last_events = None
        self.obversation = None
        
        code = ""
        for bot in bot_list:
            code += f"""
                        await {bot}.chat('/clear @p');
                        await {bot}.chat('/effect give @p instant_health 1 255');
                        await {bot}.chat('/effect give @p saturation 1 255');
                        await {bot}.chat('/effect clear @p');
                        await {bot}.chat('/experience set @p 0 points');
                    """
        self.step_manuual(code)
        print('agent reset done')
        return self.obversation
    

    def close(self):
        self.env.close()

    def step_manuual(self, code):
        events = self.env.step(
            code=code,
            programs=self.programs,
        )
        self.last_events = copy.deepcopy(events)
        self.obversation = extract_obs(self.last_events)
        return self.obversation

    def step(self, code):      
        action_str = construct_action_str(code)
        self.step_manuual(code = action_str)
        self.time_step += 1
        return self.obversation

    def render(self):
        return self.env.render()

    def start(self, position=None, reset_env=True):
        if self.resume:
            # keep the inventory
            self.env.reset(
                options={
                    "mode": "soft",
                    "wait_ticks": self.env_wait_ticks,
                    "position": position,
                }
            )
        else:
            # clear the inventory
            self.env.reset(
                options={
                    "mode": "hard",
                    "wait_ticks": self.env_wait_ticks,
                    "position": position,
                }
            )
            self.resume = True

        self.last_events = None
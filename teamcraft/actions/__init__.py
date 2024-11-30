import pkg_resources
import os
import teamcraft.utils as U


def load_atomic_actions(atomic_action_names=None):
    package_path = pkg_resources.resource_filename("teamcraft", "")
    if atomic_action_names is None:
        atomic_action_names = [
            actions[:-3]
            for actions in os.listdir(f"{package_path}/actions")
            if actions.endswith(".js")
        ]
    actions = [
        U.load_text(f"{package_path}/actions/{atomic_action_name}.js")
        for atomic_action_name in atomic_action_names
    ]
    return actions

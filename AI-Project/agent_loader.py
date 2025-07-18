import importlib.util
import sys
import os
from typing import Callable

    #modified code to solve loading issue
def load_agent(agent_path: str) -> Callable:
    """
    Dynamically load a Python file at `agent_path` which defines:
       def agent_move():
       ...
    Returns a reference to that function.
    """

    module_name = os.path.basename(agent_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, agent_path)
    if spec is None:
        raise ImportError(f"Cannot create spec for {agent_path}")

    agent_module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = agent_module  # Make module picklable
    spec.loader.exec_module(agent_module)  # type: ignore

    if not hasattr(agent_module, 'agent_move'):
        raise ValueError(f"Agent file '{agent_path}' does not define 'agent_move' function")

    return getattr(agent_module, 'agent_move')


    #original code
# def load_agent(agent_path: str) -> Callable:
#     """
#     Dynamically load a Python file at `agent_path` which defines:
#        def agent_move():
#        ...
#     Returns a reference to that function.
#     """
#     spec = importlib.util.spec_from_file_location(os.path.basename(agent_path).replace(".py", ""), agent_path)
#     agent_module = importlib.util.module_from_spec(spec) # type: ignore
#     spec.loader.exec_module(agent_module) # type: ignore

#     if not hasattr(agent_module, 'agent_move'):
#         raise ValueError(f"Agent file '{agent_path}' does not define 'agent_move' function.")

#     return getattr(agent_module, 'agent_move')

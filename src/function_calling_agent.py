from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from typing import Callable
from llama_index.llms.ollama import Ollama

def get_agent(tools:list[Callable], model:str="llama3.2:3b-instruct-q8_0")->ReActAgent:
    llm = Ollama(model=model, request_timeout=120.0, n_gpu_layers = -1)
    agent = ReActAgent.from_tools([FunctionTool.from_defaults(fn=tool) for tool in tools], llm=llm, verbose=True, max_iterations=15)
    return agent


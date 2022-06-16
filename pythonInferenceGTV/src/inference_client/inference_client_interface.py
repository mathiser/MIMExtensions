from abc import abstractmethod
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from task_input.task_input import TaskInput
from task_output.task_output import TaskOutput


class InferenceClientInterface:
    @abstractmethod
    def post_task(self, task: TaskInput) -> str:
        pass
    
    @abstractmethod        
    def get_task(self, uid: str) -> TaskOutput:
        pass
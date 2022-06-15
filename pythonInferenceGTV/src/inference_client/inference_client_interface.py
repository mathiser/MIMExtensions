import json
import time
import traceback

from task_input.task_input import TaskInput
from task_output.task_output import TaskOutput

from abc import abstractmethod

class InferenceClientInterface:    
    @abstractmethod
    def post_task(self, task: TaskInput) -> str:
        pass
    
    @abstractmethod        
    def get_task(self, uid: str) -> TaskOutput:
        pass
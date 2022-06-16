from abc import abstractmethod
from typing import Dict


class ClientBackendInterface:
    @abstractmethod
    def get(self, endpoint: str):
        pass
    
    @abstractmethod
    def post(self, endpoint: str, params: Dict, files: Dict):
        pass
    

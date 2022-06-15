import os
from typing import Dict

import requests
from urllib.parse import urljoin
from abc import abstractmethod


class ClientBackendInterface:
    @abstractmethod
    def get(self, endpoint: str):
        pass
    
    @abstractmethod
    def post(self, endpoint: str, params: Dict, files: Dict):
        pass
    

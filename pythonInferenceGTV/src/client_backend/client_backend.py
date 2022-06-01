import os
from typing import Dict

import requests
from urllib.parse import urljoin

from client_backend.client_backend_interface import ClientBackendInterface


class ClientBackend(ClientBackendInterface):
    def __init__(self, base_url: str, cert_path=None):
        self.base_url = base_url
        self.cert_path = cert_path
        if not self.cert_path:
            self.cert_path = self.__get_cert_file_path()

    def get(self, endpoint: str):
        return requests.get(url=urljoin(self.base_url, endpoint), verify=self.cert_path)
    
    def post(self, endpoint: str, params: Dict, files: Dict):
        return requests.post(url=urljoin(self.base_url, endpoint),
                             params=params,
                             files=files,
                             verify=self.cert_path)

    def __get_cert_file_path(self):
        absolutepath = os.path.abspath(__file__)
        fileDirectory = os.path.dirname(absolutepath)
        return os.path.join(fileDirectory, "../certs/omen.onerm.dk.pem")
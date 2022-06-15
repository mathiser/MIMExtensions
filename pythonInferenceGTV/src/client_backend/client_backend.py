import os
from typing import Dict

import requests
from urllib.parse import urljoin
from .client_backend_interface import ClientBackendInterface

class ClientBackend(ClientBackendInterface):
    def __init__(self, base_url: str, verify=None):
        self.base_url = base_url
        if not verify:
            self.verify = self.__get_cert_file_path()
        else:
            self.verify = verify
        
    def get(self, endpoint: str):
        return requests.get(url=urljoin(self.base_url, endpoint),
                            verify=self.verify)
    
    def post(self, endpoint: str, params: Dict, files: Dict):
        return requests.post(url=urljoin(self.base_url, endpoint),
                             params=params,
                             files=files,
                             verify=self.verify)

    def __get_cert_file_path(self):
        absolutepath = os.path.abspath(__file__)
        fileDirectory = os.path.dirname(absolutepath)
        cert_path = os.path.join(fileDirectory, "certs/certs.pem")
        if not os.path.isfile(cert_path):
            raise Exception("Cert file not found")
        return os.path.join(fileDirectory, "certs/certs.pem")
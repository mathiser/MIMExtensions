import os
from typing import Dict

import requests
from urllib.parse import urljoin


class ClientBackend:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.cert_path = self.__get_cert_file_path()
        
    def get(self, endpoint: str):
        return requests.get(url=urljoin(self.base_url, endpoint),
                            verify=self.cert_path)
    
    def post(self, endpoint: str, params: Dict, files: Dict):
        return requests.post(url=urljoin(self.base_url, endpoint),
                             params=params,
                             files=files,
                             verify=self.cert_path)

    def __get_cert_file_path(self):
        absolutepath = os.path.abspath(__file__)
        fileDirectory = os.path.dirname(absolutepath)
        cert_path = os.path.join(fileDirectory, "certs/certs.pem")
        if not os.path.isfile(cert_path):
            raise Exception("Cert file not found")
        return os.path.join(fileDirectory, "certs/certs.pem")
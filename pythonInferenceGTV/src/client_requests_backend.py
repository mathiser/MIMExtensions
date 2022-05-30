import requests
from urllib.parse import urljoin

class ClientRequestsBackend:
    def __init__(self, base_url: str, cert: str):
        self.base_url = base_url
        self.cert = cert
    
    def get(self, endpoint):
        return requests.get(url=urljoin(self.base_url, endpoint), verify=self.cert)
    
    def post(self, endpoint, params, files):
        return requests.post(url=urljoin(self.base_url, endpoint),
                             params=params,
                             files=files,
                             verify=self.cert)
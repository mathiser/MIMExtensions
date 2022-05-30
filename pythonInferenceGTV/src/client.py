from client_requests_backend import ClientRequestsBackend

class Client:
    def __init__(self, client_backend: ClientRequestsBackend):
        self.client_backend = client_backend
        
    def post_task(self):
        pass
    
    def get_task(self):
        pass
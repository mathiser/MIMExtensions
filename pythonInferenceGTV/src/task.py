class Task:
    def __init__(self, image_container: ImageContainer, model_human_readable_id: str, client: HttpsClient):
        self.image_container = image_container
        self.model_human_readable_id = model_human_readable_id
        self.client = client
        self.uid = None
        
        
    def post_task(self):
        with self.image_container.zip() as zip:
            res = self.client.post("/api/tasks/",
                              params={"model_human_readable_id": self.model_human_readable_id},
                              files={"zip_file": zip},
                              )
            if res.ok:
                self.uid = json.loads(res.content)["uid"]
            else:
                return res
                
    def get_task(self):
        if self.uid:
            
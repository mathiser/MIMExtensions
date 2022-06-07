import json
import time
import traceback

from .task_input import TaskInput
from .task_output import TaskOutput
from .exceptions import LastPostFailed, InferenceServerError


class InferenceClient:
    def __init__(self,
                 logger,
                 client_backend,
                 polling_interval_sec: int,
                 timeout_sec: int,
                 ):
        self.logger = logger
        self.task_endpoint = "/api/tasks/"
        self.client_backend = client_backend
        self.polling_interval_sec = polling_interval_sec
        self.timeout_sec = timeout_sec
        self.last_post_uid = None

    def post_task(self, task: TaskInput) -> str:
        try:
            with task.get_input_zip() as zip:
                params= {"model_human_readable_id": task.model_human_readable_id}
                files = {"zip_file": zip}
                res = self.client_backend.post(endpoint=self.task_endpoint,
                                               params=params,
                                               files=files)
                self.logger.info(res)
                self.logger.info(str(res.content))
                if res.ok:
                    self.last_post_uid = json.loads(res.content)
                else:
                    self.last_post_uid = None
                    raise LastPostFailed
        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise e
            
    def get_last_post_uid(self):
        if self.last_post_uid:
            return self.last_post_uid
        else:
            raise LastPostFailed

    def get_task(self, uid: str) -> TaskOutput:
        counter = 0
        while counter < self.timeout_sec:
            res = self.client_backend.get(endpoint=self.task_endpoint + uid)
            if res.ok:
                return TaskOutput(res.content)

            elif res.status_code == 500:
                raise InferenceServerError

            else:
                time.sleep(self.polling_interval_sec)
                counter += self.polling_interval_sec
                self.logger.info("Waiting ... Waited for {} seconds".format(counter))
        else:
            raise TimeoutError

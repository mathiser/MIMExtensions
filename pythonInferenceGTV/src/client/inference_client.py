import json
import time

from task_input.task_input import TaskInput

from task_output.task_output import TaskOutput


from client_backend.exceptions import LastPostFailed, InferenceServerError


class InferenceClient:
    def __init__(self,
                 client_backend,
                 polling_interval_sec: int,
                 timeout_sec: int):

        self.client_backend = client_backend
        self.polling_interval_sec = polling_interval_sec
        self.timeout_sec = timeout_sec
        self.last_post_uid = None

    def post_task(self, task: TaskInput) -> str:
        with task.get_input_zip() as zip:
            res = self.client_backend.post(endpoint="/api/tasks/",
                                           params={"model_human_readable_id": task.model_human_readable_id},
                                           files={"zip_file": zip})
            if res.ok:
                parsed_res = json.loads(res.content)
                self.last_post_uid = parsed_res["uid"]
                return parsed_res
            else:
                self.last_post_uid = None
                raise LastPostFailed

    def get_last_post_uid(self):
        if self.last_post_uid:
            return self.last_post_uid
        else:
            raise LastPostFailed

    def get_task(self, uid: str) -> TaskOutput:
        counter = 0
        while counter < self.timeout_sec:
            res = self.client_backend.get(endpoint="/api/tasks/{}".format(uid))

            if res.ok:
                return TaskOutput(res.content)

            elif res.status_code == 500:
                raise InferenceServerError

            else:
                time.sleep(self.polling_interval_sec)
                counter += self.polling_interval_sec
                print("Waiting ... Waited for {} seconds".format(counter))
        else:
            raise TimeoutError

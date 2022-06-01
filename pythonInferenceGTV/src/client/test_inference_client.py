import json
import os
import secrets
import shutil
import tempfile
import unittest
import zipfile

import SimpleITK
import numpy as np
import requests

from client.inference_client import InferenceClient
from task_input.test_task_input import TestTaskInput

from task_input.task_input import TaskInput
from task_output.task_output import TaskOutput

from client_backend.client_backend_interface import ClientBackendInterface

from client_backend.exceptions import LastPostFailed


class MockClientBackend(ClientBackendInterface):
    def __init__(self):
        self.tasks = []
        self.output_zip = tempfile.TemporaryFile(suffix=".zip")
        with tempfile.TemporaryDirectory() as output_dir:
            # Make a mock labels.json
            with open(os.path.join(output_dir, "labels.json"), "w") as f:
                f.write(json.dumps({"1": "GTVt", "2": "GTVn"}))

            # Make a mock predictions.nii.gz
            arr = np.random.randint(0, 2, (256, 256, 50))
            img = SimpleITK.GetImageFromArray(arr)
            SimpleITK.WriteImage(img, os.path.join(output_dir, "predictions.nii.gz"))

            # Zip to self.output_zip tempfile
            with zipfile.ZipFile(self.output_zip, "w", zipfile.ZIP_DEFLATED) as zip:
                for file in os.listdir(output_dir):
                    path = os.path.join(output_dir, file)
                    zip.write(path, arcname=file)
        self.output_zip.seek(0)

    def __del__(self):
        for t in self.tasks:
            try:
                t["zip_file"].close()
            except Exception as e:
                print(e)

        self.output_zip.close()

    def __get_output_zip(self):
        self.output_zip.seek(0)
        return self.output_zip

    def get(self, endpoint: str) -> requests.Response:
        endpoint, uid = endpoint.rsplit("/", maxsplit=1)

        for task in self.tasks:
            if uid == task["uid"]:
                res = requests.Response()
                res.status_code = 200
                res._content = self.__get_output_zip().read()
                return res
        else:
            res = requests.Response()
            res.status_code = 404
            res._content = b"Task not found"
            return res

    def post(self, endpoint, params=None, files=None):
        if not params or not files:
            raise Exception("missing file or params")
        tmp_file = tempfile.TemporaryFile()
        tmp_file.write(files["zip_file"].read())
        tmp_file.seek(0)

        task = {
            "uid": secrets.token_urlsafe(32),
            "model_human_readable_id": params["model_human_readable_id"],
            "zip_file": tmp_file
        }
        self.tasks.append(task)

        res = requests.Response()
        res.status_code = 200
        res_task = task.copy()
        del res_task["zip_file"]
        res._content = json.dumps(res_task)
        return res

class TestInferenceClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client_backend = MockClientBackend()
        self.client = InferenceClient(client_backend=self.client_backend,
                                      polling_interval_sec=1, timeout_sec=3)

    def test_post_task_intended(self):
        test_task_input = TestTaskInput()
        test_task_input.setUp()
        task_input = test_task_input.test_task_input_instantiation()

        res = self.client.post_task(task_input)
        print(res)

        self.assertEqual(res["uid"], self.client.get_last_post_uid())
        return task_input

    def test_get_task_intended(self):
        task_input = self.test_post_task_intended()
        self.assertIsInstance(task_input, TaskInput)
        self.assertIsNotNone(task_input)

        post_uid = self.client.get_last_post_uid()
        self.assertIsNotNone(post_uid)

        task_output = self.client.get_task(uid=post_uid)
        self.assertIsInstance(task_output, TaskOutput)

    def test_get_task_TimeoutError(self):
        self.assertRaises(TimeoutError, self.client.get_task, uid="This task does not exist")

    def test_get_last_post_uid_LastPostFailed(self):
        self.assertRaises(LastPostFailed, self.client.get_last_post_uid)


if __name__ == '__main__':
    unittest.main()

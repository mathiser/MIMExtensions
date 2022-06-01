import unittest
import zipfile

import numpy as np

from task_input.task_input import TaskInput


class TestTaskInput(unittest.TestCase):
    def setUp(self) -> None:
        self.model_human_readable_id = "TestCase"
        self.ct_arr = np.random.randint(low=-1000, high=1200, size=[64, 128, 128])
        self.pet_arr = np.random.randint(low=0, high=12000, size=[64, 128, 128])
        self.t1_arr = np.random.randint(low=0, high=256, size=[64, 128, 128])
        self.t2_arr = np.random.randint(low=0, high=256, size=[64, 128, 128])
        self.spacing = [1.117, 1.117, 3.000]

    def test_task_input_instantiation(self):
        task_input = TaskInput(
            ct=self.ct_arr,
            pet=self.pet_arr,
            t1=self.t1_arr,
            t2=self.t2_arr,
            spacing=self.spacing,
            model_human_readable_id=self.model_human_readable_id)

        self.assertIsNotNone(task_input)
        return task_input

    def test_get_input_zip(self):
        task_input = self.test_task_input_instantiation()
        with task_input.get_input_zip() as tmp_file:
            with zipfile.ZipFile(tmp_file, "r", zipfile.ZIP_DEFLATED) as zip:
                expected_names = [f"tmp_000{i}.nii.gz" for i in range(4)]
                for zipinfo in zip.filelist:
                    self.assertIn(zipinfo.filename, expected_names)
                    self.assertGreater(zipinfo.file_size, 0)


if __name__ == '__main__':
    unittest.main()

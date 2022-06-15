import unittest
import zipfile

import numpy as np
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from .task_input import TaskInput


class TestTaskInput(unittest.TestCase):
    def setUp(self) -> None:
        self.model_human_readable_id = "TestCase"
        self.img_zero = np.random.randint(low=-1000, high=1200, size=[64, 128, 128])
        self.img_one = np.random.randint(low=0, high=12000, size=[64, 128, 128])
        self.img_two = np.random.randint(low=0, high=256, size=[64, 128, 128])
        self.img_three = np.random.randint(low=0, high=256, size=[64, 128, 128])
        self.spacing = [1.117, 1.117, 3.000]
        self.scaling_factor = [2, 2, 1]

    def test_task_input_no_dicom_info(self):
        task_input = TaskInput(meta_information={"spacing": self.spacing,
                                                 "scaling_factor":self.scaling_factor},
                               model_human_readable_id=self.model_human_readable_id)
        
        task_input.add_array(self.img_zero)
        task_input.add_array(self.img_one)
        task_input.add_array(self.img_two)
        task_input.add_array(self.img_three) 
        
        self.assertIsNotNone(task_input)
        
        return task_input
    def test_task_input_with_dicom_info(self):
        task_input = TaskInput(meta_information={"spacing": self.spacing,
                                                 "scaling_factor":self.scaling_factor},
                               model_human_readable_id=self.model_human_readable_id)
        
        task_input.add_array(self.img_zero)
        task_input.add_array(self.img_one)
        task_input.add_array(self.img_two)
        task_input.add_array(self.img_three)
        
        export_dicom_info_0_or_1 = 1
        assert export_dicom_info_0_or_1 in [0, 1]
        if export_dicom_info_0_or_1:
            task_input.add_dicom_info({"Dummy dicom": "variable"})
            task_input.add_dicom_info({"Dummy dicom": "variable"})
            task_input.add_dicom_info({"Dummy dicom": "variable"})
            task_input.add_dicom_info({"Dummy dicom": "variable"})

        self.assertIsNotNone(task_input)
        return task_input

    def test_get_input_zip_no_dicom(self):
        task_input = self.test_task_input_no_dicom_info()
        with task_input.get_input_zip() as tmp_file:
            with zipfile.ZipFile(tmp_file, "r", zipfile.ZIP_DEFLATED) as zip:
                expected_names = [f"tmp_000{i}.nii.gz" for i in range(4)]
                expected_names.append("meta.json")
                for zipinfo in zip.filelist:
                    self.assertIn(zipinfo.filename, expected_names)
                    self.assertGreater(zipinfo.file_size, 0)
    
    def test_get_input_zip_with_dicom(self):
        task_input = self.test_task_input_with_dicom_info()
        with task_input.get_input_zip() as tmp_file:
            with zipfile.ZipFile(tmp_file, "r", zipfile.ZIP_DEFLATED) as zip:
                expected_names = [f"tmp_000{i}.nii.gz" for i in range(4)]
                expected_names.append("meta.json")
                for i in range(4):
                    expected_names.append(f"tmp_000{i}.dicom_info.json")

                for zipinfo in zip.filelist:
                    self.assertIn(zipinfo.filename, expected_names)
                    self.assertGreater(zipinfo.file_size, 0)


if __name__ == '__main__':
    unittest.main()

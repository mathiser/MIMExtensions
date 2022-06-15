import json
import os
import tempfile
import unittest
import zipfile

import numpy as np
import SimpleITK as sitk
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from task_output.task_output import TaskOutput
from testing.mock_classes import XMimContour

class TestTaskOutput(unittest.TestCase):
    def setUp(self) -> None:
        self.output_zip = tempfile.TemporaryFile(suffix=".zip")
        with tempfile.TemporaryDirectory() as output_dir:
            # Make a mock labels.json
            with open(os.path.join(output_dir, "predictions.json"), "w") as f:
                f.write(json.dumps({"1": "GTVt", "2": "GTVn"}))

            # Make a mock predictions.nii.gz
            gtvt = XMimContour("GTVt")
            gtvn = XMimContour("GTVn") 
            tmp_arr = np.zeros_like(gtvt.getData().copyToNPArray())
            tmp_arr[gtvt.getData().copyToNPArray() == True] = 1
            tmp_arr[gtvn.getData().copyToNPArray() == True] = 2
            
            print(np.unique(gtvt.getData().copyToNPArray()))
            img = sitk.GetImageFromArray(tmp_arr)
            
            sitk.WriteImage(img, os.path.join(output_dir, "predictions.nii.gz"))

            # Zip to self.output_zip tempfile
            with zipfile.ZipFile(self.output_zip, "w", zipfile.ZIP_DEFLATED) as zip:
                for file in os.listdir(output_dir):
                    path = os.path.join(output_dir, file)
                    zip.write(path, arcname=file)
        self.output_zip.seek(0)

    def tearDown(self) -> None:
        self.output_zip.close()

    def test_task_output_initialization(self):
        task_output = TaskOutput(output_zip_bytes=self.output_zip.read())
        self.assertIsNotNone(task_output) 
        
        return task_output
    
    def test_get_output_as_label_array_dict(self):
        task_output = self.test_task_output_initialization()

        label_array_dict = task_output.get_output_as_label_array_dict()
        for label, array in label_array_dict.items():
            self.assertIn(label, ["GTVt", "GTVn"])
            self.assertEqual(array.dtype, bool)

        self.assertFalse(np.array_equal(label_array_dict["GTVt"], label_array_dict["GTVn"]))

if __name__ == '__main__':
    unittest.main()

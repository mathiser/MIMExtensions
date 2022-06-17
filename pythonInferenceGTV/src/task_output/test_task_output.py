import json
import os
import sys
import tempfile
import unittest
import zipfile

import SimpleITK as sitk
import numpy as np

from task_output.exceptions import NiftiNamingError, PredictionLoadError

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from task_output.task_output import TaskOutput
from testing.mock_classes import XMimContour


class TestTaskOutput(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_task_output_initialization_intended(self):
        with tempfile.TemporaryFile(suffix=".zip") as output_zip:
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

                img = sitk.GetImageFromArray(tmp_arr)

                sitk.WriteImage(img, os.path.join(output_dir, "predictions.nii.gz"))

                # Zip to self.output_zip tempfile
                with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zip:
                    for file in os.listdir(output_dir):
                        path = os.path.join(output_dir, file)
                        zip.write(path, arcname=file)
            output_zip.seek(0)

            task_output = TaskOutput(output_zip_bytes=output_zip.read())
            self.assertIsNotNone(task_output)

        return task_output

    def test_task_output_initialization_wrong_naming(self):
        with tempfile.TemporaryFile(suffix=".zip") as output_zip:
            with tempfile.TemporaryDirectory() as output_dir:
                # Make a mock labels.json
                with open(os.path.join(output_dir, "wrong_name.json"), "w") as f:
                    f.write(json.dumps({"1": "GTVt", "2": "GTVn"}))

                # Make a mock predictions.nii.gz
                gtvt = XMimContour("GTVt")
                gtvn = XMimContour("GTVn")
                tmp_arr = np.zeros_like(gtvt.getData().copyToNPArray())
                tmp_arr[gtvt.getData().copyToNPArray() == True] = 1
                tmp_arr[gtvn.getData().copyToNPArray() == True] = 2

                img = sitk.GetImageFromArray(tmp_arr)

                sitk.WriteImage(img, os.path.join(output_dir, "another_wrong_name.nii.gz"))

                # Zip to self.output_zip tempfile
                with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zip:
                    for file in os.listdir(output_dir):
                        path = os.path.join(output_dir, file)
                        zip.write(path, arcname=file)
            output_zip.seek(0)

            self.assertRaises(NiftiNamingError, TaskOutput, output_zip_bytes=output_zip.read())

    def test_task_output_initialization_wrong_nii_format(self):
        with tempfile.TemporaryFile(suffix=".zip") as output_zip:
            with tempfile.TemporaryDirectory() as output_dir:
                # Make a mock labels.json
                with open(os.path.join(output_dir, "wrong_name.json"), "w") as f:
                    f.write(json.dumps({"1": "GTVt", "2": "GTVn"}))

                    with open(os.path.join(output_dir, "wrong_name.nii.gz"), "w") as f:
                        f.write(json.dumps({"1": "GTVt", "2": "GTVn"}))

                # Zip to self.output_zip tempfile
                with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zip:
                    for file in os.listdir(output_dir):
                        path = os.path.join(output_dir, file)
                        zip.write(path, arcname=file)
            output_zip.seek(0)

            self.assertRaises(PredictionLoadError, TaskOutput, output_zip_bytes=output_zip.read())

if __name__ == '__main__':
    unittest.main()

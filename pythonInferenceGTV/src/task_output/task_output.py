import json
import os
import tempfile
import zipfile
from typing import Dict

import SimpleITK as sitk
import numpy as np


class TaskOutput:
    def __init__(self, output_zip_bytes: bytes):
        # Load output zip bytes to a TemporaryFile
        with tempfile.TemporaryFile(suffix=".zip") as output_zip:
            output_zip.write(output_zip_bytes)
            output_zip.seek(0)

            with tempfile.TemporaryDirectory() as output_dir:
                # Make a temporary directory to load output nifti and label_json
                with zipfile.ZipFile(output_zip) as zip:
                    zip.extractall(output_dir)

                # Set label json
                self.label_json_path = self.__find_label_json_path_in_dir(output_dir)
                assert self.label_json_path
                with open(self.label_json_path) as r:
                    self.label_json = json.loads(r.read())

                # Set prediction image and array
                self.prediction_nii_path = self.__find_prediction_nii_path_in_dir(output_dir)
                assert self.prediction_nii_path
                self.prediction_nii_img = sitk.ReadImage(self.prediction_nii_path)
                self.prediction_nii_arr = sitk.GetArrayFromImage(self.prediction_nii_img)

    def __find_label_json_path_in_dir(self, directory):
        for fol, subs, files in os.walk(directory):
            for file in files:
                if file == "labels.json":
                    return os.path.join(fol, file)

    def __find_prediction_nii_path_in_dir(self, directory):
        for fol, subs, files in os.walk(directory):
            for file in files:
                if file == "predictions.nii.gz":
                    return os.path.join(fol, file)

    def get_output_as_label_array_dict(self) -> Dict[str, np.ndarray]:
        # Generate label_array_dict to return. Represented like {"GTVn_AI": nd.array with dtype bool}
        label_array_dict = {}
        for i, label in self.label_json.items():
            i = int(i)
            tmp_array = np.zeros_like(self.prediction_nii_arr, dtype=bool)
            tmp_array[self.prediction_nii_arr == i] = True
            label_array_dict[label] = tmp_array

        return label_array_dict

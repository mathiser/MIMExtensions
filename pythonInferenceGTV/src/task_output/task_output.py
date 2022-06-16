import json
import os
import tempfile
import zipfile
from typing import Dict, Tuple, List

import SimpleITK as sitk
import numpy as np


class TaskOutput:
    """
    Makes an object which represents the returned bytes of inference_client.py:get_task
    The retrieved zip must contain "{prefix}.nii.gz"s with predictions and "{prefix}.json"s with the same prefix for the nifti and the json.
    """
    def __init__(self, output_zip_bytes: bytes) -> None:
        self.json_nii_list: List[Tuple[Dict, np.ndarray]] = []  # path to json in [0] and path to pred in [1]

        # Load output zip bytes to a TemporaryFile
        with tempfile.TemporaryFile(suffix=".zip") as output_zip:
            output_zip.write(output_zip_bytes)
            output_zip.seek(0)

            # Make a temporary directory to load output nifti and label_json
            with tempfile.TemporaryDirectory() as output_dir:
                with zipfile.ZipFile(output_zip) as zip:
                    zip.extractall(output_dir)

                # Set self.json_nii_list
                self.__find_label_json_and_nii_paths_in_dir(output_dir)

        # <-- output_zip is closed here -->

    def __load_json(self, path: str) -> Dict:
        with open(path) as r:
            return json.loads(r.read())

    def __find_label_json_and_nii_paths_in_dir(self, directory: str) -> None:

        for fol, subs, files in os.walk(directory):
            for file in files:
                path = os.path.join(fol, file)
                if path.endswith(".json"):
                    label_dict = self.__load_json(path)
                    img = sitk.ReadImage(path.replace(".json", ".nii.gz"))
                    arr = sitk.GetArrayFromImage(img)

                    self.json_nii_list.append((label_dict, arr))

    def get_output_as_label_array_dict(self) -> Dict[str, np.ndarray]:
        # Generate label_array_dict to return. Represented like {"GTVn_AI": nd.array with dtype bool}
        label_array_dict = {}
        for label_dict_arr in self.json_nii_list:
            label_dict, arr = label_dict_arr

            # Generate the actual label_array_dict
            for i, label in label_dict.items():
                i = int(i)  # For conformity
                tmp_array = np.zeros_like(arr, dtype=bool)
                tmp_array[arr == i] = True  # Set the appropriate voxels to true for a given structure.
                label_array_dict[label] = tmp_array  # Insert the binary array to label_array_dict

        return label_array_dict

import os
import shutil
import tempfile
import traceback
import zipfile
from typing import List

import SimpleITK as sitk
import numpy as np


class TaskInput:
    def __init__(self,
                 ct: np.ndarray,
                 pet: np.ndarray,
                 t1: np.ndarray,
                 t2: np.ndarray,
                 spacing: List[float],
                 model_human_readable_id: str):

        self.ct = ct
        self.pet = pet
        self.t1 = t1
        self.t2 = t2
        self.spacing = spacing
        self.model_human_readable_id = model_human_readable_id

        self.uid = None
        self.dirs_to_delete = []

    def __del__(self):
        for d in self.dirs_to_delete:
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except Exception as e:
                    traceback.print_exc()
                    raise e

    def get_input_zip(self) -> tempfile.TemporaryFile:
        with tempfile.TemporaryDirectory() as tmp_dir:
            for i, arr in enumerate((self.ct, self.pet, self.t1, self.t2)):
                img = sitk.GetImageFromArray(arr)
                img.SetSpacing(self.spacing)
                path = os.path.join(tmp_dir, "tmp_{}.nii.gz".format(str(10000 + i)[1:]))
                sitk.WriteImage(img, path, useCompression=True)

            tmp_file = tempfile.TemporaryFile()
            with zipfile.ZipFile(tmp_file, "w", zipfile.ZIP_DEFLATED) as z:
                for file in os.listdir(tmp_dir):
                    z.write(os.path.join(tmp_dir, file), arcname=file)

            tmp_file.seek(0)
            return tmp_file

import os
import shutil
import tempfile
import traceback
import zipfile
from typing import List, Dict

import SimpleITK as sitk
import numpy as np
import json

class TaskInput:
    def __init__(self,
                 meta_information,
                 model_human_readable_id: str):
        
        self.meta = meta_information
        self.images = []
        self.model_human_readable_id = model_human_readable_id

        self.uid = None
        self.dirs_to_delete = []

    def add_array(self, array: np.ndarray):
        self.images.append(array)
        
    def __del__(self):
        for d in self.dirs_to_delete:
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except Exception as e:
                    traceback.print_exc()
                    raise e

    def get_input_zip(self) -> tempfile.TemporaryFile:
        tmp_file = tempfile.TemporaryFile()
        with tempfile.TemporaryDirectory() as tmp_dir:
            
            with open(os.path.join(tmp_dir, "meta.json"), "w") as f:
                f.write(json.dumps(self.meta))
                
            for i, arr in enumerate(self.images):
                img = sitk.GetImageFromArray(arr)
                img.SetSpacing(self.meta["spacing"])
                path = os.path.join(tmp_dir, "tmp_{}.nii.gz".format(str(10000 + i)[1:]))
                sitk.WriteImage(img, path, useCompression=True)

            with zipfile.ZipFile(tmp_file, "w") as z:
                for file in os.listdir(tmp_dir):
                    z.write(os.path.join(tmp_dir, file), arcname=file)
    
        tmp_file.seek(0)
        return tmp_file

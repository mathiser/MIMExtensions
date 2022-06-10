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
                 meta_information: Dict,
                 model_human_readable_id: str):
        
        self.meta = meta_information
     
        self.images: List[np.ndarray] = [] #container for np arrays of images. Are added through add_array
        self.dicom_info: List[Dict] = []
        
        self.model_human_readable_id = model_human_readable_id # the human_readable_id of the model

    def add_array(self, array: np.ndarray):
        self.images.append(array)
    
    def add_dicom_info(self, dicom_info: Dict):
        self.dicom_info.append(dicom_info)
        
    def get_input_zip(self) -> tempfile.TemporaryFile:
        """ 
        Serves images as a temporary zip file that must be closed manually
        Images are in order written as tmp_0000.nii.gz, tmp_0001.nii.gz etc.
        Meta informations is dumped as json in 'meta.json'
        """
        
        tmp_file = tempfile.TemporaryFile()
        with tempfile.TemporaryDirectory() as tmp_dir:
            
            with open(os.path.join(tmp_dir, "meta.json"), "w") as f:
                f.write(json.dumps(self.meta))
                
                
            for i, arr in enumerate(self.images):
                scan_id = str(10000 + i)[1:]
                img = sitk.GetImageFromArray(arr)
                img.SetSpacing(self.meta["spacing"])
                path = os.path.join(tmp_dir, "tmp_{}.nii.gz".format(scan_id))
                sitk.WriteImage(img, path, useCompression=True)
                
                if len(self.dicom_info) != 0:
                    with open(os.path.join(tmp_dir, "tmp_{}.dicom_info.json".format(scan_id)), "w") as f:
                        f.write(json.dumps(self.dicom_info[i]))
                

            with zipfile.ZipFile(tmp_file, "w") as z:
                for file in os.listdir(tmp_dir):
                    z.write(os.path.join(tmp_dir, file), arcname=file)
            
    
        tmp_file.seek(0)
        return tmp_file

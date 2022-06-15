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
                 model_human_readable_id: str) -> None:
        
        self.meta = meta_information # Generate in ext.py:generate_image_meta_information. Contains spacing and scaling factor of img_zero
     
        self.images: List[np.ndarray] = [] # Container for np arrays of images. Added through self.add_array
        self.dicom_info: List[Dict] = [] # Container for dicom info dictionaries. Added through self.add_dicom_info 
        
        self.model_human_readable_id = model_human_readable_id # the human_readable_id of the model

    def add_array(self, array: np.ndarray) -> None:
        self.images.append(array)
    
    def add_dicom_info(self, dicom_info: Dict) -> None:
        self.dicom_info.append(dicom_info)
        
    def get_input_zip(self) -> tempfile.TemporaryFile:
        """ 
        Serves images as a temporary zip file that must be closed manually
        Images are in order written as tmp_0000.nii.gz, tmp_0001.nii.gz etc.
        Meta informations is dumped as json in 'meta.json'
        """
        
        # Tmp file for the zip_object
        tmp_file = tempfile.TemporaryFile() ## This is returned and MUST BE CLOSE MANUALLY!
        
        # Tmp dir to save the task elements - is eventually zipped
        with tempfile.TemporaryDirectory() as tmp_dir:
            
            # Dump meta information as json to tmp_dir
            with open(os.path.join(tmp_dir, "meta.json"), "w") as f:
                f.write(json.dumps(self.meta))
                
            # Dump arrays as .nii.gz to tmp_array
            for i, arr in enumerate(self.images):
                scan_id = str(10000 + i)[1:] # To follow nnUNet convention of id_0000.nii.gz, id_0001.nii.gz, etc.
                img = sitk.GetImageFromArray(arr)
                img.SetSpacing(self.meta["spacing"]) # Sets spacing from reference image img_zero
                path = os.path.join(tmp_dir, "tmp_{}.nii.gz".format(scan_id)) # Make the full path
                sitk.WriteImage(img, path, useCompression=True) # Dumps to tmp_dir 
                
                # If dicom info is added, it should be dumped to tmp_dir as jsons.
                if len(self.dicom_info) != 0:
                    with open(os.path.join(tmp_dir, "tmp_{}.dicom_info.json".format(scan_id)), "w") as f:
                        f.write(json.dumps(self.dicom_info[i]))
                
            # tmp_file is used to make a ZipFile to return
            with zipfile.ZipFile(tmp_file, "w") as z:
                for file in os.listdir(tmp_dir):
                    z.write(os.path.join(tmp_dir, file), arcname=file)
        
        # Here tmp_dir is deleted.
    
        tmp_file.seek(0) # Reset tmp_file pointer to allow read anew
        return tmp_file

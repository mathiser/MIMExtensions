import os
import shutil
import tempfile
import traceback
import zipfile
from typing import List, Dict

import SimpleITK as sitk
import numpy as np
import json
from numpy import full

patientID = 1048608
dateID = 524320

class TaskInput:
    def __init__(self,
                 meta_information: Dict):        
        
        self.meta = meta_information
        self.images: List[np.ndarray] = [] #container for np arrays of images. Are added through add_array
        self.dicom_info: List[Dict] = []
        self.contours: Dict[str, np.ndarray] = {} #container for np arrays of contours
        
    def add_array(self, array: np.ndarray):
        self.images.append(array)
    
    def add_dicom_info(self, dicom_info: Dict):
        self.dicom_info.append(dicom_info)
        
    def set_contours(self, contours : List):
        self.contours = contours
        
    def save(self, export_dir):
        """ 
        Serves images as a temporary zip file that must be closed manually
        Images are in order written as tmp_0000.nii.gz, tmp_0001.nii.gz etc.
        Meta informations is dumped as json in 'meta.json'
        """
        full_path = os.path.join(export_dir, self.dicom_info[0][patientID], self.dicom_info[0][dateID])
        os.makedirs(full_path, exist_ok=True)
        
        # Dump meta.json
        with open(os.path.join(full_path, "meta.json"), "w") as f:
            f.write(json.dumps(self.meta))
 
        # Dump contours
        for contour in self.contours:
            meta = self.generate_meta_for_contour(contour)
            arr = contour.getData().copyToNPArray()
            img = sitk.GetImageFromArray(arr)
            path = os.path.join(full_path, "{}.nii.gz".format(meta["name"].replace("/", "-")))
            sitk.WriteImage(img, path, useCompression=True)
           
            with open(path + ".json", "w") as f:
                f.write(json.dumps(self.generate_meta_for_contour(contour)))
            
        # Dump Images
        for i, arr in enumerate(self.images):
            scan_id = str(10000 + i)[1:]
            img = sitk.GetImageFromArray(arr)
            img.SetSpacing(self.meta["spacing"])
            path = os.path.join(full_path, "tmp_{}.nii.gz".format(scan_id))
            sitk.WriteImage(img, path, useCompression=True)
            
            if len(self.dicom_info) != 0:
                with open(os.path.join(full_path, "tmp_{}.dicom_info.json".format(scan_id)), "w") as f:
                    f.write(json.dumps(self.dicom_info[i]))

    def generate_meta_for_contour(self, contour):
        d = {}
        d["name"] = contour.getInfo().getName()
        d["dimensions"] = contour.getDims()
        d["spacing"] = contour.getNoxelSizeInMm()
        d["multiplier"] = contour.getMultiplier()
        
        return d
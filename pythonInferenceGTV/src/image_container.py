import tempfile
import os
import numpy as np

class ImageContainer:
    def __init__(self,
                 ct: XMimImage, 
                 pet: XMimImage, 
                 t1: XMimImage, 
                 t2: XMimImage) -> None:
    
        self.ct = ct
        self.pet = pet
        self.t1 = t1
        self.t2 = t2

        self.tmp_dir = tempfile.TemporaryDirectory()
        self.images_to_temp_dir()
        
        self.tmp_file = tempfile.TemporaryFile()

    def __del__(self):
        if os.path.exists(self.tmp_dir):
            os.rmdir(self.tmp_dir)
        
        if self.tmp_file:
            self.tmp_file.close()
        
    def get_spacing(scan: XMimImage):
        return scan.getNoxelSizeInMm()
    
    def to_np_array(self, scan: XMimImage) -> np.ndarray:
        return scan.getRawData().copyToNPArray()
    
    def images_to_temp_dir(self):
        for i, scan in enumerate((self.ct, self.pet, self.t1, self.t2)):
                array = self.get_np_array(scan)
                img = sitk.GetImageFromArray(array)
                img.SetSpacing(self.get_spacing(scan))
            
                path =  os.path.join(self.tmp_dir, "tmp_{}.nii.gz".format(str(10000+i)[1:]))
            
                sitk.WriteImage(img, path, useCompression=True)
                yield path
                
    def zip(self):
        ## ... zip the folder
        with zipfile.ZipFile(self.tmp_file, "w", zipfile.ZIP_DEFLATED) as z:
            for file in os.listdir(self.tmp_dir):
                z.write(os.path.join(tmp_dir, file), arcname=file)
        
        self.tmp_file.seek(0)
        
        return self.tmp_file
            
        
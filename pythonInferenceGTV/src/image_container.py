from typing import Dict
import logging
import numpy as np
from MIMPython.SupportedIOTypes import XMimImage, XMimContour


class ImageContainer:
    def __init__(self,
                 ct: XMimImage,
                 pet: XMimImage,
                 t1: XMimImage,
                 t2: XMimImage) -> None:
        
        assert ct.getNoxelSizeInMm() == pet.getNoxelSizeInMm() == t1.getNoxelSizeInMm() == t2.getNoxelSizeInMm()
        
        self.ct = ct
        self.pet = pet
        self.t1 = t1
        self.t2 = t2

    def get_spacing(self):
        return self.ct.getNoxelSizeInMm()

    def get_ct_array(self):
        return self.ct.getRawData().copyToNPArray()

    def get_pet_array(self):
        return self.pet.getRawData().copyToNPArray()

    def get_t1_array(self):
        return self.t1.getRawData().copyToNPArray()

    def get_t2_array(self):
        return self.t2.getRawData().copyToNPArray()
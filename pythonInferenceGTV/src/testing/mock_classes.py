from builtins import staticmethod
import numpy as np
import os
import json
import logging

class XMimSession:
    def createLogger(self):
        return logging.getLogger(__file__)

image_dim = np.array([64, 128, 128])
noxelsize = np.array([3, 1.17, 1.17])
multiplier = np.array([1, 2, 2])

class XMimImage:
    def __init__(self):
        self.contours = []
        self.noxelsize = noxelsize
        self.dimensions = image_dim
       
        self.data = XMimImageData()
        self.info = XMimImageInfo()
        
    def getRawData(self):
        return self.data
    
    def getNoxelSizeInMm(self):
        return self.noxelsize
    
    def createNewContour(self, name):
        contour = XMimContour(name)
        self.contours.append(contour)
        return contour
    
    def getInfo(self):
        return self.info
    
    def getContours(self):
        return self.contours

class XMimImageData:
    def __init__(self):
        self.arr = np.random.randint(low=-1000, high=1200, size=image_dim)
    
    def copyToNPArray():
        return self.arr
    
        
class XMimImageInfo:
    def __init__(self):
        self.dicom_info = XMimImageInfoDicomInfo() 
        
    def getDicomInfo(self):
        return self.dicom_info
    
    def getName(self):
        return self.name
    
class XMimImageInfoDicomInfo():
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), "mock_dicom_info.json")) as r:
            self.dicom_info = {int(k): v for k, v in json.loads(r.read()).items()}
        
    def getTags(self):
        return self.dicom_info.keys()
    
    def getValue(self, tag):
        return self.dicom_info[tag]
    
#########################

class XMimContour:
    def __init__(self, name):
        self.name = name
        self.multiplier = multiplier
        self.data = XMimContourData()
        self.info = XMimContourInfo(self.name)

    def getMultiplier(self):
        return self.multiplier
    
    def redrawCompletely(self):
        print("vorking veri haard")
    
    def getDims(self):
        return self.getData().copyToNPArray().shape
    
    def getData(self):
        return self.data

    def getInfo(self):
        return self.info

    def delete(self):
        del self
        
class XMimContourInfo:
    def __init__(self, name):
        self.name = name
        
    def getName(self):
        return self.name

class XMimContourData:
    def __init__(self):
        self.arr = np.random.randint(0, 2, image_dim*multiplier)

    def setFromNPArray(self, new_arr = np.ndarray):
        assert self.arr.shape == new_arr.shape
        self.arr = new_arr
        
    def copyToNPArray(self):
        return self.arr


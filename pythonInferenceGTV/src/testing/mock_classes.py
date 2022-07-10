import json
import logging
import os

import numpy as np

"""
This file contains mock classes of internal MIM classes. Only used for testing
"""

class XMimSession:
    def createLogger(self):
        return logging.getLogger(__file__)


image_dim = [64, 128, 128]
noxel_size = [3, 1.17, 1.17]
multiplier = [1, 2, 2]
iop = [1, 0, 0, 0, 1, 0, 0, 0, 1]
origin = [-120.000000, 120.000000, 55.000000]


class XMimImage:
    def __init__(self):
        self.contours = []
        self.noxel_size = noxel_size
        self.dimensions = image_dim

        self.data = XMimNDArray()
        self.info = XMimImageInfo()
        self.space = XMimImageSpace()

    def getSpace(self):
        return self.space

    def getRawData(self):
        return self.data

    def getNoxelSizeInMm(self):
        return self.noxel_size

    def createNewContour(self, name):
        contour = XMimContour(name)
        self.contours.append(contour)
        return contour

    def getScaledData(self):
        return self.data

    def getInfo(self):
        return self.info

    def getContours(self):
        return self.contours

class XMimImageSpace:
    def __init__(self):
        self.iop = iop
        self.nox_sixe = noxel_size
        self.origin = origin

    def getNoxSize(self):
        return self.nox_sixe

    def getDicomCenter(self):
        return self.origin

    def getIop(self):
        return self.iop


class XMimNDArray:
    def __init__(self):
        self.arr = np.random.randint(low=-1000, high=1200, size=image_dim)

    def copyToNPArray(self):
        return self.arr


class XMimImageInfo:
    def __init__(self):
        self.dicom_info = XMimImageInfoDicomInfo()

    def getDicomInfo(self):
        return self.dicom_info

class XMimImageInfoDicomInfo:
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
        self.space = XMimImageSpace()

    def getSpace(self):
        return self.space

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
        self.dim = np.array(image_dim) * np.array(multiplier)
        self.arr = np.random.randint(0, 2, self.dim)

    def setFromNPArray(self, new_arr: np.ndarray):
        assert self.arr.shape == new_arr.shape

        self.arr = new_arr

    def copyToNPArray(self):
        return self.arr

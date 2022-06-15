import json
import os
import tempfile
import unittest
import zipfile

import numpy as np
import SimpleITK as sitk
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from task_output.task_output import TaskOutput
from testing.mock_classes import XMimContour, XMimImage
from ext_functions.ext_functions import parse_contour_names, inferenceServerPost, inferenceServerGet

class TestExtFunctions(unittest.TestCase):
    def setUp(self) -> None:
        pass
    
    def test_parse_contour_names_list(self):
        contour_names = ""
        contour_list = parse_variables(contour_names=contour_names)
        self.assertIsNone(contour_list)
    
    def test_parse_variables_1_1_GTV_OAR(self):
        contour_names = "GTV OAR"
        contour_list = parse_contour_names(contour_names=contour_names)
        self.assertEqual(contour_names, ["GTV", "OAR"])
        
    def test_inferenceServerPost_4_images(self):
        pass
    
    def test_inferenceServerPost_3_images(self):
        pass
    
    def test_inferenceServerPost_2_images(self):
        pass
    
    def test_inferenceServerPost_1_images(self):
        pass
    
    def test_inferenceServerGet(self):
        pass
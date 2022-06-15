import traceback
import os
import sys
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from task_input.info_generators import generate_image_meta_information, generate_dicom_meta
from testing.mock_classes import XMimImage, XMimSession

class TestInfoGenerators(unittest.TestCase):
    def setUp(self) -> None:
        self.img_zero = XMimImage()
        
    def test_generate_image_meta_information(self):
        meta = generate_image_meta_information(self.img_zero)
        self.assertIsInstance(meta, dict)
        self.assertIn("spacing",meta.keys())
        self.assertIn("scaling_factor", meta.keys())
    
    def test_generate_dicom_meta(self):
        dicom = generate_dicom_meta(self.img_zero)
        self.assertIsInstance(dicom, dict)
        for k, v in dicom.items():
            self.assertIsInstance(k, int)
            self.assertIsInstance(v, str)
        
    
if __name__ == '__main__':
    unittest.main()
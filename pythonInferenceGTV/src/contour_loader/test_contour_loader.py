
import unittest

import numpy as np
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from testing.mock_classes import XMimImage, XMimSession
from task_output.test_task_output import TestTaskOutput
from contour_loader.contour_loader import ContourLoader

class TestContourLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.model_human_readable_id = "TestCase"

        # Mock classes
        self.session = XMimSession()
        self.reference_img = XMimImage()

    def test_contour_loader_init(self):
        """
        Checks if contour_loader can be initiated
        """
        contour_loader = ContourLoader(self.reference_img, self.session.createLogger())
        self.assertIsNotNone(contour_loader)
        return contour_loader
        
    def test_set_contours_from_label_array_dict(self):
        """
        Checks if contours from task_out can be set via contour_loader
        """
        contour_loader = self.test_contour_loader_init()

        output_test = TestTaskOutput()
        output_test.setUp()
        self.task_output = output_test.test_task_output_initialization()
        output_test.tearDown()
        
        label_array_dict0 = self.task_output.get_output_as_label_array_dict()
        contour_loader.set_contours_from_label_array_dict(label_array_dict0)
        self.assertEqual(len(contour_loader.ref_image.contours), 2)

        # Try with new contours
        output_test = TestTaskOutput()
        output_test.setUp()
        self.task_output = output_test.test_task_output_initialization()
        output_test.tearDown()
        
        label_array_dict1 = self.task_output.get_output_as_label_array_dict()
        contour_loader.set_contours_from_label_array_dict(label_array_dict0)
        self.assertEqual(len(contour_loader.ref_image.contours), 2)
        
        for k, v in label_array_dict0.items():
            self.assertFalse(np.array_equal(v, label_array_dict1[k]))     
    
if __name__ == '__main__':
    unittest.main()

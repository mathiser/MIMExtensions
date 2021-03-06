import json
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from task_input.info_generators import generate_image_meta_information, generate_dicom_meta
from testing.mock_classes import XMimImage


class TestInfoGenerators(unittest.TestCase):
    def setUp(self) -> None:
        self.img_zero = XMimImage()

    def test_generate_image_meta_information(self):
        meta = generate_image_meta_information(self.img_zero)
        self.assertIsInstance(meta, dict)
        self.assertIn("spacing", meta.keys())
        self.assertIn("scaling_factor", meta.keys())
        self.assertIn("origin", meta.keys())
        self.assertIn("direction", meta.keys())

        for k, v in meta.items():
            self.assertTrue(self.is_serializable(k))
            self.assertTrue(self.is_serializable(v))

    def test_generate_dicom_meta(self):
        dicom = generate_dicom_meta(self.img_zero)
        self.assertIsInstance(dicom, dict)
        for k, v in dicom.items():
            self.assertIsInstance(k, int)
            self.assertIsInstance(v, str)

            self.assertTrue(self.is_serializable(k))
            self.assertTrue(self.is_serializable(v))

    def test_generate_image_meta_information_deleted_test_contour(self):
        pre_contours = self.img_zero.getContours()
        meta = generate_image_meta_information(self.img_zero)
        
        for k, v in meta.items():
            self.assertTrue(self.is_serializable(k))
            self.assertTrue(self.is_serializable(v))

        post_contours = self.img_zero.getContours()
        self.assertEqual(pre_contours, post_contours)

    @staticmethod
    def is_serializable(obj):
        try:
            json.dumps(obj)
            return True
        except Exception as e:
            print(e, obj)
            return False


if __name__ == '__main__':
    unittest.main()

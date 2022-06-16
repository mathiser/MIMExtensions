import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from inference_client.test_inference_client import MockClientBackend
from ext_functions.ext_functions import parse_contour_names, inference_server_post, inference_server_get
from testing.mock_classes import XMimImage, XMimSession


class TestExtFunctions(unittest.TestCase):
    def setUp(self) -> None:
        self.client_backend = MockClientBackend("https://test-hest.org")

    def test_parse_contour_names_none(self):
        contour_names = ""
        contour_list = parse_contour_names(contour_names=contour_names)
        self.assertIsNone(contour_list)

    def test_parse_variables_spaces(self):
        contour_names = "GTV OAR"
        contour_list = parse_contour_names(contour_names=contour_names)
        self.assertEqual(contour_list, ["GTV", "OAR"])

    def test_parse_variables_comma(self):
        contour_names = "GTV,OAR"
        contour_list = parse_contour_names(contour_names=contour_names)
        self.assertEqual(contour_list, ["GTV", "OAR"])

    def test_parse_variables_semicolon(self):
        contour_names = "GTV;OAR"
        contour_list = parse_contour_names(contour_names=contour_names)
        self.assertEqual(contour_list, ["GTV", "OAR"])

    def test_parse_variables_comma_semicolon_space(self):
        contour_names = "   GTVt,GTVn;Parotid_L OAR "
        contour_list = parse_contour_names(contour_names=contour_names)
        self.assertEqual(contour_list, ["GTVt", "GTVn", "Parotid_L", "OAR"])

    def test_inferenceServerPost_1_images(self):
        images = [XMimImage()]

        uid = inference_server_post(session=XMimSession(),
                                    images=images,
                                    model_human_readable_id="model_human_readable_id",
                                    export_dicom_info=0,
                                    contour_names="",
                                    export_contours=0,
                                    client_backend=self.client_backend)
        self.assertIsInstance(uid, str)
        return uid

    def test_inferenceServerPost_4_images(self):
        images = [XMimImage(), XMimImage(), XMimImage(), XMimImage()]

        uid = inference_server_post(session=XMimSession(),
                                    images=images,
                                    model_human_readable_id="model_human_readable_id",
                                    export_dicom_info=0,
                                    contour_names="",
                                    export_contours=0,
                                    client_backend=self.client_backend)
        self.assertIsInstance(uid, str)
        return uid

    def test_inferenceServerPost_export_contours_non_exist(self):
        images = [XMimImage()]

        uid = inference_server_post(session=XMimSession(),
                                    images=images,
                                    model_human_readable_id="model_human_readable_id",
                                    export_dicom_info=0,
                                    contour_names="",
                                    export_contours=1,
                                    client_backend=self.client_backend)
        self.assertIsInstance(uid, str)
        return uid

    def test_inferenceServerPost_export_all_contours(self):
        images = [XMimImage()]
        images[0].createNewContour("GTVt")
        images[0].createNewContour("GTVn")

        uid = inference_server_post(session=XMimSession(),
                                    images=images,
                                    model_human_readable_id="model_human_readable_id",
                                    export_dicom_info=0,
                                    contour_names="",
                                    export_contours=1,
                                    client_backend=self.client_backend)
        self.assertIsInstance(uid, str)
        return uid

    def test_inferenceServerPost_export_all_contours_typo(self):
        images = [XMimImage()]
        images[0].createNewContour("GTVt")
        images[0].createNewContour("GTVn")

        uid = inference_server_post(session=XMimSession(),
                                    images=images,
                                    model_human_readable_id="model_human_readable_id",
                                    export_dicom_info=0,
                                    contour_names="GTVt,GTvn",
                                    export_contours=1,
                                    client_backend=self.client_backend)
        self.assertIsInstance(uid, str)
        return uid

    def test_inferenceServerPost_export_export_dicom(self):
        images = [XMimImage()]
        images[0].createNewContour("GTVt")
        images[0].createNewContour("GTVn")

        uid = inference_server_post(session=XMimSession(),
                                    images=images,
                                    model_human_readable_id="model_human_readable_id",
                                    export_dicom_info=1,
                                    contour_names="",
                                    export_contours=1,
                                    client_backend=self.client_backend)
        self.assertIsInstance(uid, str)
        return uid

    def test_inferenceServerGet(self):
        uid = self.test_inferenceServerPost_1_images()
        ref_img = XMimImage()
        inference_server_get(session=XMimSession(),
                             polling_interval_sec=1,
                             timeout_sec=5,
                             reference_image=ref_img,
                             client_backend=self.client_backend,
                             uid=uid)

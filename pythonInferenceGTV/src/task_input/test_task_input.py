import os
import sys
import unittest
import zipfile

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from .task_input import TaskInput
from testing.mock_classes import XMimImage


class TestTaskInput(unittest.TestCase):
    def setUp(self) -> None:
        self.model_human_readable_id = "TestCase"

    def test_task_input_no_dicom_info(self):
        task_input = TaskInput(model_human_readable_id=self.model_human_readable_id,
                               export_dicom_info=False)

        task_input.add_image(XMimImage())
        task_input.add_image(XMimImage())
        task_input.add_image(XMimImage())
        task_input.add_image(XMimImage())

        self.assertIsNotNone(task_input)

        return task_input

    def test_task_input_with_dicom_info(self):
        task_input = TaskInput(model_human_readable_id=self.model_human_readable_id,
                               export_dicom_info=True)

        task_input.add_image(XMimImage())
        task_input.add_image(XMimImage())
        task_input.add_image(XMimImage())
        task_input.add_image(XMimImage())

        self.assertIsNotNone(task_input)
        return task_input

    def test_get_input_zip_no_dicom(self):
        task_input = self.test_task_input_no_dicom_info()
        with task_input.get_input_zip() as tmp_file:
            with zipfile.ZipFile(tmp_file, "r", zipfile.ZIP_DEFLATED) as zip:
                expected_names = generate_expected_files(4, False)
                for zipinfo in zip.filelist:
                    self.assertIn(zipinfo.filename, expected_names)
                    self.assertGreater(zipinfo.file_size, 0)

    def test_get_input_zip_with_dicom(self):
        task_input = self.test_task_input_with_dicom_info()
        with task_input.get_input_zip() as tmp_file:
            with zipfile.ZipFile(tmp_file, "r", zipfile.ZIP_DEFLATED) as zip:
                expected_names = generate_expected_files(4, True)

                for zipinfo in zip.filelist:
                    self.assertIn(zipinfo.filename, expected_names)
                    self.assertGreater(zipinfo.file_size, 0)

    def test_get_input_zip_with_dicom_contours_all(self):
        task_input = TaskInput(model_human_readable_id=self.model_human_readable_id,
                               export_dicom_info=True)
        img = XMimImage()
        contour_names = ["GTVt", "GTVn"]
        img.createNewContour(contour_names[0])
        img.createNewContour(contour_names[1])

        task_input.add_image(img)
        task_input.set_contours_to_export_from_img(img, contour_names=contour_names)

        with task_input.get_input_zip() as tmp_file:
            with zipfile.ZipFile(tmp_file, "r", zipfile.ZIP_DEFLATED) as zip:
                expected_names = generate_expected_files(1, True)
                for label in ["GTVt", "GTVn"]:
                    expected_names.append(f"{label}.nii.gz")
                    expected_names.append(f"{label}.json")

                for zipinfo in zip.filelist:
                    self.assertIn(zipinfo.filename, expected_names)
                    self.assertGreater(zipinfo.file_size, 0)

    def test_get_input_zip_with_dicom_contours_selected_contours(self):
        task_input = TaskInput(model_human_readable_id=self.model_human_readable_id,
                               export_dicom_info=True)
        img = XMimImage()
        contour_names = ["GTVt", "GTVn"]
        img.createNewContour(contour_names[0])
        img.createNewContour(contour_names[1])

        task_input.add_image(img)
        task_input.set_contours_to_export_from_img(img, contour_names=contour_names)

        with task_input.get_input_zip() as tmp_file:
            with zipfile.ZipFile(tmp_file, "r", zipfile.ZIP_DEFLATED) as zip:
                expected_names = generate_expected_files(1, True)

                for label in ["GTVt", "GTVn"]:
                    expected_names.append(f"{label}.nii.gz")
                    expected_names.append(f"{label}.json")

                for zipinfo in zip.filelist:
                    self.assertIn(zipinfo.filename, expected_names)
                    self.assertGreater(zipinfo.file_size, 0)

    def test_get_input_zip_with_dicom_contours_illegal_chars(self):
        task_input = TaskInput(model_human_readable_id=self.model_human_readable_id,
                               export_dicom_info=True)
        img = XMimImage()
        contour_names = ["GTVt\hest/ko", "GTVn:orwhat\sd"]
        img.createNewContour(contour_names[0])
        img.createNewContour(contour_names[1])

        task_input.add_image(img)
        task_input.set_contours_to_export_from_img(img, contour_names=contour_names)

        with task_input.get_input_zip() as tmp_file:
            with zipfile.ZipFile(tmp_file, "r", zipfile.ZIP_DEFLATED) as zip:
                expected_names = generate_expected_files(1, True)

                for label in ["GTVt.hest.ko", "GTVn.orwhat.sd"]:
                    expected_names.append(f"{label}.nii.gz")
                    expected_names.append(f"{label}.json")

                for zipinfo in zip.filelist:
                    self.assertIn(zipinfo.filename, expected_names)
                    self.assertGreater(zipinfo.file_size, 0)

def generate_expected_files(number_of_images: int, dicom: bool):
    expected_names = []
    for i in range(number_of_images):
        expected_names.append(f"tmp_000{i}.nii.gz")
        expected_names.append(f"tmp_000{i}.meta.json")
        if dicom:
            expected_names.append(f"tmp_000{i}.dicom_info.json")
    return expected_names

if __name__ == '__main__':
    unittest.main()

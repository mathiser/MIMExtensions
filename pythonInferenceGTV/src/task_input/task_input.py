import json
import os
import re
import sys
import tempfile
import zipfile
from typing import List

import SimpleITK as sitk

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:  # For production
    from MIMPython.SupportedIOTypes import XMimImage, XMimContour
except ModuleNotFoundError:  # For Testing
    from testing.mock_classes import XMimImage, XMimContour

from .info_generators import generate_image_meta_information, generate_dicom_meta, generate_meta_for_contour


class TaskInput:
    def __init__(self, model_human_readable_id: str, export_dicom_info: bool = False) -> None:
        self.model_human_readable_id = model_human_readable_id  # the human_readable_id of the model
        self.export_dicom_info = export_dicom_info  # Bool if dicom should be exported
        self.images: List[XMimImage] = []  # Container for np arrays of images. Added through self.add_array
        self.contours: List[XMimContour] = []  # Container for contours to export
        self.meta_information = None  # Meta information on img_zero. Generated when first image is added with add_image()


    def add_image(self, image: XMimImage) -> None:
        if len(self.images) == 0:
            self.meta_information = generate_image_meta_information(image)
        self.images.append(image)

    def set_contours_to_export_from_img(self, image: XMimImage, contour_names: List[str] = None):
        if not contour_names:
            self.contours = image.getContours()
        elif contour_names:
            for name in contour_names:
                for existing_contour in image.getContours():
                    if name == existing_contour.getInfo().getName():
                        self.contours.append(existing_contour)
                        break

    def __dump_contour(self, contour: XMimContour, out_dir):
        # Dump contours
        meta = generate_meta_for_contour(contour)
        arr = contour.getData().copyToNPArray()
        img = sitk.GetImageFromArray(arr)
        filename = "{}.nii.gz".format(meta["name"])
        filename = re.sub(r'[<>:"/\\?*]', '.', filename)
        path = os.path.join(out_dir, filename)
        sitk.WriteImage(img, path, useCompression=True)

        with open(path + ".json", "w") as f:
            f.write(json.dumps(meta))

    def __dump_image(self, image: XMimImage, index: int, out_dir):
        assert self.meta_information  # should be set when first image is added

        # To follow nnUNet convention of id_0000.nii.gz, id_0001.nii.gz, etc.
        scan_id = str(10000 + index)[1:]

        # Get np array
        arr = image.getRawData().copyToNPArray()
        img = sitk.GetImageFromArray(arr)
        img.SetSpacing(self.meta_information["spacing"])  # Sets spacing from reference image img_zero

        # Make the full path
        path = os.path.join(out_dir, "tmp_{}.nii.gz".format(scan_id))

        # Write image
        sitk.WriteImage(img, path, useCompression=True)  # Dumps to tmp_dir

        # If export dicom_info is set, dump dicom info
        if self.export_dicom_info:
            dicom_info = generate_dicom_meta(image)
            with open(os.path.join(out_dir, "tmp_{}.dicom_info.json".format(scan_id)), "w") as f:
                f.write(json.dumps(dicom_info))

    def __dump_meta(self, out_dir):
        assert self.meta_information
        with open(os.path.join(out_dir, "meta.json"), "w") as f:
            f.write(json.dumps(self.meta_information))

    def get_input_zip(self) -> tempfile.TemporaryFile:
        """ 
        Serves images as a temporary zip file that must be closed manually
        Images are in order written as tmp_0000.nii.gz, tmp_0001.nii.gz etc.
        Meta informations is dumped as json in 'meta.json'
        """

        # Tmp dir to save the task elements - is eventually zipped
        with tempfile.TemporaryDirectory() as tmp_dir:

            # Dump meta information as json to tmp_dir
            self.__dump_meta(tmp_dir)

            # Dump images as .nii.gz to tmp_array
            for i, image in enumerate(self.images):
                self.__dump_image(image, i, tmp_dir)

            # Export contours if any added
            for contour in self.contours:
                self.__dump_contour(contour, tmp_dir)

            # tmp_file is used to make a ZipFile to return
            tmp_file = tempfile.TemporaryFile()  # This is returned and should be closed manually!
            with zipfile.ZipFile(tmp_file, "w") as z:
                for file in os.listdir(tmp_dir):
                    z.write(os.path.join(tmp_dir, file), arcname=file)

        # Here tmp_dir is deleted.

        tmp_file.seek(0)  # Reset tmp_file pointer to allow read anew
        return tmp_file

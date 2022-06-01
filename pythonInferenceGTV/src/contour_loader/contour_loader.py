from typing import Dict

import numpy as np

from MIMPython.SupportedIOTypes import XMimImage, XMimContour


class ContourLoader:
    def __init__(self, ref_image: XMimImage):
        self.ref_image = ref_image
        self.updated_contours = []

    def __get_or_create_contour(self, label: str) -> XMimContour:
        for contour in self.ref_image.getContours():
            if contour.getInfo().getName() == label:
                return contour
        else:
            contour = self.ref_image.createNewContour(label)
            return contour

    def set_contours_from_label_array_dict(self, label_array_dict: Dict[str, np.ndarray]):
        for label, array in label_array_dict.items():
            assert array.dtype == bool

            # Create or get contour
            contour = self.__get_or_create_contour(label)

            # Set the actual contour from a bool array
            contour.getData().setFromNPArray(array)
            contour.redrawCompletely()
            self.updated_contours.append(contour)

    def get_updated_contours(self):
        return self.updated_contours

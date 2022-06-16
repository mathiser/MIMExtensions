from typing import Dict

import numpy as np

try:
    from MIMPython.SupportedIOTypes import XMimImage, XMimContour
except ModuleNotFoundError:
    from testing.mock_classes import XMimImage, XMimContour


class ContourLoader:
    def __init__(self, reference_image: XMimImage, logger):
        self.ref_image = reference_image
        self.logger = logger

    def __get_or_create_contour(self, label: str) -> XMimContour:
        """
        Checks through existing contours and find matches with label. If it does not exist, a new contour is created.
        """
        for contour in self.ref_image.getContours():
            if contour.getInfo().getName() == label:
                return contour
        else:
            contour = self.ref_image.createNewContour(label)
            return contour

    def set_contours_from_label_array_dict(self, label_array_dict: Dict[str, np.ndarray]):
        """
        Sets all contours from a label_array_dict which is served by a TaskOutput
        """
        for label, array in label_array_dict.items():
            assert array.dtype == bool

            # Create or get contour
            contour = self.__get_or_create_contour(label)

            # Set the actual contour from a bool array
            contour.getData().setFromNPArray(array)
            self.logger.info(str(label))
            self.logger.info(str(contour.getDims()))
            contour.redrawCompletely()

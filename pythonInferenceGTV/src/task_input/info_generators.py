from typing import Dict
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:  # For production
    from MIMPython.SupportedIOTypes import XMimImage, XMimContour

except ModuleNotFoundError:  # For Testing
    from testing.mock_classes import XMimImage, XMimContour


def generate_image_meta_information(reference_image: XMimImage) -> Dict:
    """
    Generates a dict with scaling_factor between contours and reference_image along with spacing
    """
    meta = {}

    # Scaling factor from image
    contour = reference_image.createNewContour('scaling_factor_getter')
    meta["scaling_factor"] = list(contour.getMultiplier())
    contour.delete()

    space = reference_image.getSpace()
    meta["spacing"] = list(space.getNoxSize())
    meta["origin"] = list(space.getDicomCenter())
    meta["direction"] = list(space.getIop())

    return meta

def generate_dicom_meta(reference_image: XMimImage) -> Dict:
    """
    Generates a dict with all dicom tags and values
    """
    tags = reference_image.getInfo().getDicomInfo().getTags()
    tag_dict = {tag: str(reference_image.getInfo().getDicomInfo().getValue(tag)) for tag in tags}
    return tag_dict


def generate_meta_for_contour(contour: XMimContour) -> Dict:
    """
    Generates a dict with meta information on a contour. Used when contours are exported
    """
    d = {}
    d["name"] = contour.getInfo().getName()
    d["dimensions"] = contour.getDims()
    d["multiplier"] = contour.getMultiplier()

    space = contour.getSpace()
    d["spacing"] = list(space.getNoxSize())
    d["origin"] = list(space.getDicomCenter())
    d["direction"] = list(space.getIop())

    return d

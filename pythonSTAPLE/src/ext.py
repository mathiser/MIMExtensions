import os
import sys
import traceback
from typing import Dict, List

import SimpleITK as sitk
import numpy as np

sys.path.append(os.path.dirname(__file__))

try:  # For production
    from MIMPython.EntryPoint import mim_extension_entrypoint
    from MIMPython.SupportedIOTypes import String, Integer, XMimImage, XMimSession, Float

except ModuleNotFoundError:  # For Testing
    from testing.mock_classes import XMimImage, XMimSession
    from builtins import str as String
    from builtins import int as Integer


def staple_list_of_images(list_of_images: List[sitk.Image], threshold: float) -> (str, sitk.Image):
    fil = sitk.STAPLEImageFilter()

    # Find foreground integer
    test_arr = sitk.GetArrayFromImage(list_of_images[0])
    uniques = np.unique(test_arr)
    fil.SetForegroundValue(int(uniques[-1]))

    # STAPLE
    staple_img = fil.Execute(sitk.VectorOfImage(list_of_images))
    bin_staple = binarize_image(staple_img, threshold=threshold)

    return bin_staple


def binarize_image(image: sitk.Image, threshold) -> sitk.Image:
    bin_img = image > threshold

    return bin_img

@mim_extension_entrypoint(name="STAPLE",
                          author="Mathis Rasmussen",
                          description="STAPLEs all loaded contours with the exact same name and creates a new",
                          category="Inference server model",
                          institution="DCPT",
                          version=1.1)
def staple_entrypoint(session: XMimSession,
                      img_zero: XMimImage,
                      staple_threshold: String):
    logger = session.createLogger()
    logger.info("Starting extension pythonSTAPLE")
    try:
        if staple_threshold == "":
            staple_threshold = 0.8
        else:
            staple_threshold = float(staple_threshold)

        # ARRANGE CONTOURS IN Dict[labelstring, image]
        logger.info(f"1/2 - Loading contours")
        label_image_dict = {}
        for contour in img_zero.getContours():
            label = contour.getInfo().getName()
            logger.info(f"[ ] Loading {label}")

            if label in label_image_dict.keys():
                label_image_dict[label].append(contour)
            else:
                label_image_dict[label] = [contour]
            logger.info(f"[X] Loading {label}")

        # STAPLE
        logger.info(f"2/2 - STAPLE")
        for label, list_of_images in label_image_dict.items():
            logger.info(f"[ ] STAPLEing {label}")

            # Load Contours
            img_list = []
            for contour in list_of_images:
                arr = contour.getData().copyToNPArray()
                img_list.append(sitk.GetImageFromArray(arr))

            # STAPLE
            staple_raw = staple_list_of_images(list_of_images=img_list, threshold=staple_threshold)
            logger.info(f"[X] STAPLEing {label}")

            # Write to MIM
            array = sitk.GetArrayFromImage(staple_raw)
            array = array.astype(bool)

            # Create contour
            contour = img_zero.createNewContour(f"{label}_STAPLE_{staple_threshold}")

            # Set the actual contour from a bool array
            contour.getData().setFromNPArray(array)
            contour.redrawCompletely()
            logger.info(f"[X] Creating contour for {label}")

    except:
        logger.error(traceback.format_exc())

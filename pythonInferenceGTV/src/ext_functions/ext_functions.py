import os
import re
import sys
import traceback
from typing import List, Union

from client_backend.client_backend_interface import ClientBackendInterface

sys.path.append(os.path.dirname(__file__))

try:  # For production
    from MIMPython.SupportedIOTypes import String, Integer, XMimImage, XMimSession
except ModuleNotFoundError:  # For Testing
    from testing.mock_classes import XMimImage, XMimSession
    from builtins import str as String
    from builtins import int as Integer

from task_input.task_input import TaskInput
from inference_client.inference_client import InferenceClient
from contour_loader.contour_loader import ContourLoader


def parse_contour_names(contour_names: str) -> Union[List[str], None]:
    if contour_names == "":
        return None  # Will export all contours if export_contours is true
    else:
        # Split on space
        return re.split(',', contour_names.strip(" "))


def inference_server_post(session: XMimSession,
                          images: List[XMimImage],
                          model_human_readable_id: str,
                          export_dicom_info: int,
                          export_contours: int,
                          contour_names: str,
                          client_backend: ClientBackendInterface) -> String:  # Funky construct. Think of a better way.

    logger = session.createLogger()
    logger.info("Starting extension InferenceServerPost")

    try:
        # Assert allow values only
        assert export_contours in [0, 1]
        assert export_dicom_info in [0, 1]

        # Cast as bool
        export_dicom_info = bool(export_dicom_info)
        export_contours = bool(export_contours)

        # Make list none if no string given
        contour_names = parse_contour_names(contour_names)

        # Instantiate task_input
        task_input = TaskInput(model_human_readable_id=model_human_readable_id,
                               export_dicom_info=export_dicom_info)

        # set images to task_input
        for img in images:
            task_input.add_image(img)

        # Set contours to export.
        # contour_names=None -> export all contours else export only exact names
        if export_contours:
            task_input.set_contours_to_export_from_img(images[0], contour_names=contour_names)

        # Init Clients
        inference_client = InferenceClient(client_backend=client_backend,
                                           logger=logger)
        # Post task
        logger.info(f"Posting task_input on: {inference_client.task_endpoint}")
        uid = inference_client.post_task(task_input)

        logger.info(uid)
        return uid

    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())


def inference_server_get(session: XMimSession,
                         uid: String,
                         reference_image: XMimImage,
                         polling_interval_sec: Integer,
                         timeout_sec: Integer,
                         client_backend: ClientBackendInterface):   # Funky construct. Think of a better way.

    logger = session.createLogger()
    logger.info("Starting extension inferenceServerGet")

    try:
        # Instantiate clients
        inference_client = InferenceClient(client_backend=client_backend,
                                           polling_interval_sec=polling_interval_sec,
                                           timeout_sec=timeout_sec,
                                           logger=logger)

        # Polling for output zip
        task_output = inference_client.get_task(uid)

        # Get label array_dict from task_output ...
        label_array_dict = task_output.get_output_as_label_array_dict()

        # ... and load it into ContourLoader, which sets the contours to MIM
        contour_loader = ContourLoader(reference_image=reference_image, logger=logger)
        contour_loader.set_contours_from_label_array_dict(label_array_dict=label_array_dict)

    except Exception as e:
        logger.error("exit")
        logger.error(e)
        logger.error(traceback.format_exc())

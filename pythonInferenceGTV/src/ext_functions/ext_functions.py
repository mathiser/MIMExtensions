import traceback
import os
from typing import List
import sys
sys.path.append(os.path.dirname(__file__))

try: # For production
    from MIMPython.SupportedIOTypes import String, Integer, XMimImage, XMimSession
except ModuleNotFoundError: ## For Testing
    from testing.mock_classes import XMimImage, XMimSession
    from builtins import str as String
    from builtins import int as Integer

from task_input.task_input import TaskInput
from inference_client.inference_client import InferenceClient
from client_backend.client_backend import ClientBackend
from contour_loader.contour_loader import ContourLoader
from task_output.task_output import TaskOutput
from task_input.info_generators import generate_image_meta_information, generate_dicom_meta

def parse_contour_names(contour_names: str):
    if contour_names.lower() == "":
        contour_names = None
    else:
        contour_names = contour_names.split(" ")
    return contour_names
       

def inferenceServerPost(session: XMimSession,
               images: List[XMimImage],
               model_human_readable_id: str,
               export_dicom_info: bool,
               export_contours: bool, 
               contour_names: List[str],
               server_url: str) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServerX")

        assert export_contours in [0, 1]
        assert export_dicom_info in [0, 1]

        # Cast as bool
        export_dicom_info = bool(export_dicom_info)
        export_contours = bool(export_contours)
                
        # Make list none if no string given
        if contour_names.lower() == "":
            contour_names = None
        else:
            # Split on space 
            contour_names = contour_names.split(" ")
        
        task_input = TaskInput(model_human_readable_id=model_human_readable_id,
                               export_dicom_info=export_dicom_info)
        
        for img in images:
            task_input.add_image(img)
        
        # Set contours to export if exort if export
        if export_contours:
            task_input.set_contours_to_export_from_img(images[0], contour_names=contour_names)
        
        # Init Clients
        client_backend = ClientBackend(base_url=server_url)
        inference_client = InferenceClient(client_backend=client_backend,
                                           logger=logger)
        # Post task
        logger.info(f"Posting task_input: url = {client_backend.base_url}{inference_client.task_endpoint}")
        uid = inference_client.post_task(task_input)
        
        logger.info(uid)
        return uid
    
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())
        

def inferenceServerGet(session: XMimSession,
                              uid: String,
                              reference_image: XMimImage,
                              server_url: String,
                              polling_interval_sec: Integer,
                              timeout_sec: Integer): 
    
    try:
        logger = session.createLogger()
        client_backend = ClientBackend(base_url=server_url)
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
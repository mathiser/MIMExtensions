import traceback
import os
import sys
sys.path.append(os.path.dirname(__file__))

try: # For production
    from MIMPython.EntryPoint import mim_extension_entrypoint
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
    

@mim_extension_entrypoint(name="InferenceServer4images",
                          author="Mathis Rasmussen",
                          description="Wraps and ships off four images to the inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def inferenceServer4images(session: XMimSession,
               img_zero: XMimImage,
               img_one: XMimImage,
               img_two: XMimImage,
               img_three: XMimImage,
               export_dicom_info_0_or_1: Integer,
               model_human_readable_id: String,
               server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer4images")

        task_input = TaskInput(meta_information=generate_image_meta_information(img_zero),
                               model_human_readable_id=model_human_readable_id)
        
        task_input.add_array(img_zero.getRawData().copyToNPArray())
        task_input.add_array(img_one.getRawData().copyToNPArray())
        task_input.add_array(img_two.getRawData().copyToNPArray())
        task_input.add_array(img_three.getRawData().copyToNPArray())
        
        assert export_dicom_info_0_or_1 in [0, 1]
        if export_dicom_info_0_or_1:
            task_input.add_dicom_info(generate_dicom_meta(img_zero))
            task_input.add_dicom_info(generate_dicom_meta(img_one))
            task_input.add_dicom_info(generate_dicom_meta(img_two))
            task_input.add_dicom_info(generate_dicom_meta(img_three))
        
        uid = post(task_input=task_input,
                   server_url=server_url,
                   logger=logger)
        
        logger.info(uid)
        return uid
    
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())
        

@mim_extension_entrypoint(name="InferenceServer3images",
                          author="Mathis Rasmussen",
                          description="Wraps and ships off four images to the inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def inferenceServer3images(session: XMimSession,
               img_zero: XMimImage,
               img_one: XMimImage,
               img_two: XMimImage,
               export_dicom_info_0_or_1: Integer,
               model_human_readable_id: String,
               server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer3images")

        task_input = TaskInput(meta_information=generate_image_meta_information(img_zero),
                               model_human_readable_id=model_human_readable_id)
        
        task_input.add_array(img_zero.getRawData().copyToNPArray())
        task_input.add_array(img_one.getRawData().copyToNPArray())
        task_input.add_array(img_two.getRawData().copyToNPArray())

        assert export_dicom_info_0_or_1 in [0, 1]
        if export_dicom_info_0_or_1:
            task_input.add_dicom_info(generate_dicom_meta(img_zero))
            task_input.add_dicom_info(generate_dicom_meta(img_one))
            task_input.add_dicom_info(generate_dicom_meta(img_two))
            
        
        uid = post(task_input=task_input,
                   server_url=server_url,
                   logger=logger)
        
        logger.info(uid)
        return uid
    
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())


@mim_extension_entrypoint(name="InferenceServer2images",
                          author="Mathis Rasmussen",
                          description="Wraps and ships off four images to the inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def inferenceServer2images(session: XMimSession,
               img_zero: XMimImage,
               img_one: XMimImage,
               export_dicom_info_0_or_1: Integer,
               model_human_readable_id: String,
               server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer2images")

        task_input = TaskInput(meta_information=generate_image_meta_information(img_zero),
                               model_human_readable_id=model_human_readable_id)
        
        task_input.add_array(img_zero.getRawData().copyToNPArray())
        task_input.add_array(img_one.getRawData().copyToNPArray())
        
        assert export_dicom_info_0_or_1 in [0, 1]
        if export_dicom_info_0_or_1:
            task_input.add_dicom_info(generate_dicom_meta(img_zero))
            task_input.add_dicom_info(generate_dicom_meta(img_one))

            
        uid = post(task_input=task_input,
                   server_url=server_url,
                   logger=logger)
        
        logger.info(uid)
        return uid
    
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())


@mim_extension_entrypoint(name="InferenceServer1images",
                          author="Mathis Rasmussen",
                          description="Ships off to inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def inferenceServer1images(session: XMimSession,
                           img_zero: XMimImage,
                           export_dicom_info_0_or_1: Integer,
                           model_human_readable_id: String,
                           server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer1images")
       
        try:
            logger.info(str(generate_dicom_meta(img_zero)))
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            
        task_input = TaskInput(meta_information=generate_image_meta_information(img_zero),
                               model_human_readable_id=model_human_readable_id)
        
        task_input.add_array(img_zero.getRawData().copyToNPArray())

        assert export_dicom_info_0_or_1 in [0, 1]
        if export_dicom_info_0_or_1:
            task_input.add_dicom_info(generate_dicom_meta(img_zero))

        uid = post(task_input=task_input,
                   server_url=server_url,
                   logger=logger)
        
        return uid
        
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())
        
def post(task_input, server_url, logger):
    
    
    # Instantiate client
    logger.info("Instantiating client ...")
    client_backend = ClientBackend(base_url=server_url)
    inference_client = InferenceClient(client_backend=client_backend,
                                       logger=logger)
    # Post task
    logger.info(f"Posting task_input: url = {client_backend.base_url}{inference_client.task_endpoint}")
    uid = inference_client.post_task(task_input)
    
    logger.info(f"Task UID: {uid}")
    
    return uid


@mim_extension_entrypoint(name="InferenceServerGetFromUid",
                          author="Mathis Rasmussen",
                          description="Get output from InferenceServer by a UID. The UID of a task is returned then it is posted",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def inferenceServerGetFromUid(session: XMimSession,
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
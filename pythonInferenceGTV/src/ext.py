import traceback
from MIMPython.EntryPoint import *
from MIMPython.SupportedIOTypes import *
import os

"""
Welcome to the MIMExtension to serve the inference server (https://github.com/mathiser/inference_server)
This extension is build up as follows:

ext.py
Is the main file containing entrypoints to run from MIM.
There are four posting methods, which zips images and ships them off to an instance of the inference server. Each of the four (func InferenceServerXimages)
generates an object task_input of type TaskInput, and parse it on to the function "post". "Post" takes care of everything that is necessary to post
the TaskInput to the server, and it returns a UID of the task, which is needed to retrieve the task output again.
 
The function "InferenceServerGetFromUid" takes the UID from a posted task and polls the inference server with a specified interval unil the task is retrieved or timeout.
The retrieved task is loaded as a TaskOutput and loaded into MIM as contours to the reference_image (always img_zero) through ContourLoader.

inference_client.py
Contains the InferenceClient, which contains a function post_task to post a TaskInput and a function get_task to get the task output from a UID
Actual http-methods are abstracted away to ClientBackend in client_backend.py

client_backend.py
Contains ClientBackend which takes care of the actual http post and get.

task_input.py
A container for images as numpy arrays. Can serve them as a temporary zip file for posting

task_output.py
A container for the output of the InferenceServer. Can serve predictions as a dictionary of {segmentation name: np.ndarray dtype==bool}

contour_loader.py
Contains ContourLoader, which can set contours to a reference image the dictionary of TaskOutput.get_output_as_label_array_dict
  
"""


def generate_image_meta_information(reference_image):
        meta = {}
        
        # Scaling factor from image
        contour = reference_image.createNewContour('scaling_factor_getter')
        meta["scaling_factor"] = contour.getMultiplier()
        contour.delete()
        
        # Spacing if images
        meta["spacing"] = reference_image.getNoxelSizeInMm()
        return meta

def generate_dicom_meta(reference_image):
    tags = reference_image.getInfo().getDicomInfo().getTags()
    tag_dict = {tag: str(reference_image.getInfo().getDicomInfo().getValue(tag)) for tag in tags}
    return tag_dict    

@mim_extension_entrypoint(name="InferenceServer_4_images",
                          author="Mathis Rasmussen",
                          description="Wraps and ships off four images to the inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def InferenceServer4images(session: XMimSession,
               img_zero: XMimImage,
               img_one: XMimImage,
               img_two: XMimImage,
               img_three: XMimImage,
               export_dicom_info_0_or_1: Integer,
               model_human_readable_id: String,
               server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer_4_images")
        
        
        from .task_input import TaskInput

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
                   reference_image=img_zero,
                   server_url=server_url,
                   logger=logger)
        
        logger.info(uid)
        return uid
    
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())
        

@mim_extension_entrypoint(name="InferenceServer_3_images",
                          author="Mathis Rasmussen",
                          description="Wraps and ships off four images to the inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def InferenceServer3images(session: XMimSession,
               img_zero: XMimImage,
               img_one: XMimImage,
               img_two: XMimImage,
               export_dicom_info_0_or_1: Integer,
               model_human_readable_id: String,
               server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer_3_images")

        from .task_input import TaskInput
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
                   reference_image=img_zero,
                   server_url=server_url,
                   logger=logger)
        
        logger.info(uid)
        return uid
    
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())


@mim_extension_entrypoint(name="InferenceServer_2_images",
                          author="Mathis Rasmussen",
                          description="Wraps and ships off four images to the inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def InferenceServer2images(session: XMimSession,
               img_zero: XMimImage,
               img_one: XMimImage,
               export_dicom_info_0_or_1: Integer,
               model_human_readable_id: String,
               server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer_2_images")

        from .task_input import TaskInput

        task_input = TaskInput(meta_information=generate_image_meta_information(img_zero),
                               model_human_readable_id=model_human_readable_id)
        
        task_input.add_array(img_zero.getRawData().copyToNPArray())
        task_input.add_array(img_one.getRawData().copyToNPArray())
        
        assert export_dicom_info_0_or_1 in [0, 1]
        if export_dicom_info_0_or_1:
            task_input.add_dicom_info(generate_dicom_meta(img_zero))
            task_input.add_dicom_info(generate_dicom_meta(img_one))

            
        uid = post(task_input=task_input,
                   reference_image=img_zero,
                   server_url=server_url,
                   logger=logger)
        
        logger.info(uid)
        return uid
    
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())


@mim_extension_entrypoint(name="InferenceServer_1_images",
                          author="Mathis Rasmussen",
                          description="Ships off to inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def InferenceServer1images(session: XMimSession,
                           img_zero: XMimImage,
                           export_dicom_info_0_or_1: Integer,
                           model_human_readable_id: String,
                           server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer1images")
       
        from .task_input import TaskInput
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
                   reference_image=img_zero,
                   server_url=server_url,
                   logger=logger)
        
        logger.info(uid)
        return uid
        
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())
        
def post(task_input, reference_image: XMimImage, server_url, logger):
    from .inference_client import InferenceClient
    from .client_backend import ClientBackend
    from .contour_loader import ContourLoader
    from .task_output import TaskOutput

    client_backend = ClientBackend(base_url=server_url)
    inference_client = InferenceClient(client_backend=client_backend,
                                       logger=logger)
    # Post task
    logger.info(f"Posting task_input: url = {client_backend.base_url}{inference_client.task_endpoint}")
    uid = inference_client.post_task(task_input)
    
    return uid


@mim_extension_entrypoint(name="InferenceServer_get_from_uid",
                          author="Mathis Rasmussen",
                          description="Get output from InferenceServer by a UID. The UID of a task is returned then it is posted",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def InferenceServerGetFromUid(session: XMimSession,
                              uid: String,
                              reference_image: XMimImage,
                              server_url: String,
                              polling_interval_sec: Integer,
                              timeout_sec: Integer): 
    
    try:
        from .inference_client import InferenceClient
        from .client_backend import ClientBackend
        from .contour_loader import ContourLoader
        from .task_output import TaskOutput
    
        logger = session.createLogger()
        client_backend = ClientBackend(base_url=server_url)
        inference_client = InferenceClient(client_backend=client_backend,
                                           polling_interval_sec=polling_interval_sec,
                                           timeout_sec=timeout_sec,
                                           logger=logger)
        
        # Polling for output zip
        task_output = inference_client.get_task(uid)
    
        # Load contours to MIM
        label_array_dict = task_output.get_output_as_label_array_dict()
    
        contour_loader = ContourLoader(reference_image=reference_image, logger=logger)
        contour_loader.set_contours_from_label_array_dict(label_array_dict=label_array_dict)
    
    except Exception as e:
        logger.error("exit")
        logger.error(e)
        logger.error(traceback.format_exc())
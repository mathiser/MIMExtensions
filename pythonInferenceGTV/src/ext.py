import traceback
from MIMPython.EntryPoint import *
from MIMPython.SupportedIOTypes import *
import os

def generate_image_meta_information(reference_image):
        meta = {}
        
        # Scaling factor
        contour = reference_image.createNewContour('scaling_factor_getter')
        meta["scaling_factor"] = contour.getMultiplier()
        contour.delete()
        
        # Spacing
        meta["spacing"] = reference_image.getNoxelSizeInMm()
        return meta
    

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
                           model_human_readable_id: String,
                           server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer1images")
       
        from .task_input import TaskInput

        task_input = TaskInput(meta_information=generate_image_meta_information(img_zero),
                               model_human_readable_id=model_human_readable_id)
        
        task_input.add_array(img_zero.getRawData().copyToNPArray())

        
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
    inference_client.post_task(task_input)
    
    return inference_client.get_last_post_uid()


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
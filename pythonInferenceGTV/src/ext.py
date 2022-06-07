import traceback
from MIMPython.EntryPoint import *
from MIMPython.SupportedIOTypes import *
import os

@mim_extension_entrypoint(name="InferenceServer4images",
                          author="Mathis Rasmussen",
                          description="Wraps registered and aligned CT, PET, T1 and T2 "
                                      "and ships off to inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def InferenceServer4images(session: XMimSession,
               img_zero: XMimImage,
               img_one: XMimImage,
               img_two: XMimImage,
               img_three: XMimImage):
               #model_human_readable_id: String,
               #server_url: String,
               #polling_interval_sec: Integer,
               #timeout_sec: Integer):

    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer4images")
        logger.info(__file__)
        model_human_readable_id = "gtvtn_slim2"
        server_url = "https://omen.onerm.dk"
        polling_interval_sec = 5
        timeout_sec = 500

        from .inference_client import InferenceClient
        from .client_backend import ClientBackend
        from .contour_loader import ContourLoader
        from .image_container import ImageContainer
        from .task_input import TaskInput
        from .task_output import TaskOutput

        task_input = TaskInput(spacing=img_zero.getNoxelSizeInMm(),
                               model_human_readable_id=model_human_readable_id)
        
        task_input.add_array(img_zero.getRawData().copyToNPArray())
        task_input.add_array(img_one.getRawData().copyToNPArray())
        task_input.add_array(img_two.getRawData().copyToNPArray())
        task_input.add_array(img_three.getRawData().copyToNPArray())
        
        run(task_input=task_input,
            reference_image=img_zero,
            server_url=server_url,
            polling_interval_sec=polling_interval_sec,
            timeout_sec=timeout_sec,
            logger=logger)

    except Exception as e:
        logger.error("exit")
        logger.error(e)
        logger.error(traceback.format_exc())
        

@mim_extension_entrypoint(name="InferenceServer1images",
                          author="Mathis Rasmussen",
                          description="Ships off to inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def InferenceServer1images(session: XMimSession,
               img_one: XMimImage):
               #model_human_readable_id: String,
               #server_url: String,
               #polling_interval_sec: Integer,
               #timeout_sec: Integer):
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension InferenceServer1images")
        logger.info(__file__)
        model_human_readable_id = "cns_t1_oars"
        server_url = "https://omen.onerm.dk"
        polling_interval_sec = 5
        timeout_sec = 500
       
        from .task_input import TaskInput
        

    
        meta = {
            "spacing": img_one.getNoxelSizeInMm(),
            "scaling_factor": get_scaling_factor(img_one)
            }
        
        task_input = TaskInput(meta_information=meta,
                               model_human_readable_id=model_human_readable_id)
        
        task_input.add_array(img_one.getRawData().copyToNPArray())

        
        run(task_input=task_input,
            reference_image=img_one,
            server_url=server_url,
            polling_interval_sec=polling_interval_sec,
            timeout_sec=timeout_sec,
            logger=logger)
        
        
    except Exception as e:
        logger.error("exit")
        logger.error(e)
        logger.error(traceback.format_exc())
        
def run(task_input, reference_image: XMimImage, server_url, polling_interval_sec, timeout_sec, logger):
    from .inference_client import InferenceClient
    from .client_backend import ClientBackend
    from .contour_loader import ContourLoader
    from .task_output import TaskOutput
    
    client_backend = ClientBackend(base_url=server_url)
    res = client_backend.get("/")
    logger.info(str(res.status_code))
    logger.info(str(res.content))


    client_backend = ClientBackend(base_url=server_url)
    inference_client = InferenceClient(client_backend=client_backend,
                                       polling_interval_sec=polling_interval_sec,
                                       timeout_sec=timeout_sec,
                                       logger=logger)
    # Post task
    logger.info(f"Posting task_input: base_url = {client_backend.base_url}")
    logger.info(f"Posting task_input: endpoint = {inference_client.task_endpoint}")
    inference_client.post_task(task_input)

    # Polling for output zip
    task_output = inference_client.get_task(inference_client.get_last_post_uid())
    #task_output = inference_client.get_task("4C4VZBAe2Yal7Pgxc1GJcTLYpvVyXR0xc8UKM-r5UH8")

    # Load contours to MIM
    label_array_dict = task_output.get_output_as_label_array_dict()

    contour_loader = ContourLoader(reference_image=reference_image, logger=logger)
    contour_loader.set_contours_from_label_array_dict(label_array_dict=label_array_dict)
    
def get_scaling_factor(reference_image):
        contour = reference_image.createNewContour('test')
        scaling_factor = contour.getMultiplier()
        contour.delete()
        return scaling_factor

    
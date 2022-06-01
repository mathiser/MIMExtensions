import traceback

from MIMPython.EntryPoint import *
from MIMPython.SupportedIOTypes import *

from pythonInferenceGTV.src.client.inference_client import InferenceClient
from .client_backend import ClientBackend
from .contour_loader.contour_loader import ContourLoader
from .image_container import ImageContainer
from .task_input import TaskInput

EXTENSION_NAME = "00_GTVt_and_GTVn"


@mim_extension_entrypoint(name=EXTENSION_NAME,
                          author="Mathis Rasmussen",
                          description="Wraps registered and aligned CT, PET, T1 and T2 "
                                      "and ships off to inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.1)
def entrypoint(session: XMimSession,
               CT: XMimImage,
               PET: XMimImage,
               T1: XMimImage,
               T2: XMimImage,
               model_human_readable_id: String,
               server_url: String,
               polling_interval_sec: Integer,
               timeout_sec: Integer) -> List[XMimContour]:
    logger = session.createLogger()
    logger.info(f"Starting extension {EXTENSION_NAME}")
    try:
        image_container = ImageContainer(ct=CT, pet=PET, t1=T1, t2=T2)
        client_backend = ClientBackend(base_url=server_url)
        inference_client = InferenceClient(client_backend=client_backend,
                                           polling_interval_sec=polling_interval_sec,
                                           timeout_sec=timeout_sec)

        with image_container.get_zip() as input_zip:
            task_input = TaskInput(ct=image_container.get_ct_array(),
                                   pet=image_container.get_pet_array(),
                                   t1=image_container.get_t1_array(),
                                   t2=image_container.get_t2_array(),
                                   spacing=image_container.get_spacing(),
                                   model_human_readable_id=model_human_readable_id)

        # Post task
        inference_client.post_task(task_input)

        # Polling for output zip
        task_output = inference_client.get_task(inference_client.get_last_post_uid())

        # Load contours to MIM
        label_array_dict = task_output.get_output_as_label_array_dict()

        contour_loader = ContourLoader(ref_image=CT)
        contour_loader.set_contours_from_label_array_dict(label_array_dict=label_array_dict)

        return image_container.updated_contours

    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

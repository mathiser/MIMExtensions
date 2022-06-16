import os
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

try:  # For production
    from MIMPython.EntryPoint import mim_extension_entrypoint
    from MIMPython.SupportedIOTypes import String, Integer, XMimImage, XMimSession

except ModuleNotFoundError:  # For Testing
    from testing.mock_classes import XMimImage, XMimSession
    from builtins import str as String
    from builtins import int as Integer

from client_backend.client_backend import ClientBackend
from ext_functions.ext_functions import inference_server_post, inference_server_get


@mim_extension_entrypoint(name="InferenceServer4images",
                          author="Mathis Rasmussen",
                          description="See https://github.com/mathiser/MIMExtensions/blob/main/pythonInferenceGTV/src/readme.md",
                          category="Inference server model",
                          institution="DCPT",
                          version=1.0)
def inferenceServer4images(session: XMimSession,
                           img_zero: XMimImage,
                           img_one: XMimImage,
                           img_two: XMimImage,
                           img_three: XMimImage,
                           model_human_readable_id: String,
                           export_dicom_info: Integer,
                           export_contours: Integer,
                           contour_names: String,
                           server_url: String) -> String:
    logger = session.createLogger()
    logger.info("Starting extension InferenceServer4images")
    try:
        client_backend = ClientBackend(base_url=server_url)
        images = [img_zero, img_one, img_two, img_three]
        uid = inference_server_post(session=session,
                                    images=images,
                                    model_human_readable_id=model_human_readable_id,
                                    export_dicom_info=export_dicom_info,
                                    contour_names=contour_names,
                                    export_contours=export_contours,
                                    client_backend=client_backend)
        logger.info(f"UID: {uid}")
        return uid
    except:
        logger.error(traceback.format_exc())


@mim_extension_entrypoint(name="InferenceServer3images",
                          author="Mathis Rasmussen",
                          description="See https://github.com/mathiser/MIMExtensions/blob/main/pythonInferenceGTV/src/readme.md",
                          category="Inference server model",
                          institution="DCPT",
                          version=1.0)
def inference_server_3_images(session: XMimSession,
                              img_zero: XMimImage,
                              img_one: XMimImage,
                              img_two: XMimImage,
                              model_human_readable_id: String,
                              export_dicom_info: Integer,
                              export_contours: Integer,
                              contour_names: String,
                              server_url: String) -> String:
    logger = session.createLogger()
    logger.info("Starting extension InferenceServer4images")
    try:
        client_backend = ClientBackend(base_url=server_url)
        images = [img_zero, img_one, img_two]
        uid = inference_server_post(session=session,
                                    images=images,
                                    model_human_readable_id=model_human_readable_id,
                                    export_dicom_info=export_dicom_info,
                                    contour_names=contour_names,
                                    export_contours=export_contours,
                                    client_backend=client_backend)
        logger.info(f"UID: {uid}")
        return uid
    except:
        logger.error(traceback.format_exc())


@mim_extension_entrypoint(name="InferenceServer2images",
                          author="Mathis Rasmussen",
                          description="See https://github.com/mathiser/MIMExtensions/blob/main/pythonInferenceGTV/src/readme.md",
                          category="Inference server model",
                          institution="DCPT",
                          version=1.0)
def inference_server_2_images(session: XMimSession,
                              img_zero: XMimImage,
                              img_one: XMimImage,
                              model_human_readable_id: String,
                              export_dicom_info: Integer,
                              export_contours: Integer,
                              contour_names: String,
                              server_url: String) -> String:
    logger = session.createLogger()
    logger.info("Starting extension InferenceServer2images")
    try:
        client_backend = ClientBackend(base_url=server_url)
        images = [img_zero, img_one]
        uid = inference_server_post(session=session,
                                    images=images,
                                    model_human_readable_id=model_human_readable_id,
                                    export_dicom_info=export_dicom_info,
                                    contour_names=contour_names,
                                    export_contours=export_contours,
                                    client_backend=client_backend)
        logger.info(f"UID: {uid}")
        return uid

    except:
        logger.error(traceback.format_exc())


@mim_extension_entrypoint(name="InferenceServer1images",
                          author="Mathis Rasmussen",
                          description="See https://github.com/mathiser/MIMExtensions/blob/main/pythonInferenceGTV/src/readme.md",
                          category="Inference server model",
                          institution="DCPT",
                          version=1.0)
def inference_server_1_images(session: XMimSession,
                              img_zero: XMimImage,
                              model_human_readable_id: String,
                              export_dicom_info: Integer,
                              export_contours: Integer,
                              contour_names: String,
                              server_url: String) -> String:
    logger = session.createLogger()
    logger.info("Starting extension InferenceServer4images")
    try:
        client_backend = ClientBackend(base_url=server_url)
        images = [img_zero]
        uid = inference_server_post(session=session,
                                    images=images,
                                    model_human_readable_id=model_human_readable_id,
                                    export_dicom_info=export_dicom_info,
                                    contour_names=contour_names,
                                    export_contours=export_contours,
                                    client_backend=client_backend)
        logger.info(f"UID: {uid}")
        return uid
    except:
        logger.error(traceback.format_exc())


@mim_extension_entrypoint(name="InferenceServerGetFromUid",
                          author="Mathis Rasmussen",
                          description="See https://github.com/mathiser/MIMExtensions/blob/main/pythonInferenceGTV/src/readme.md",
                          category="Inference server model",
                          institution="DCPT",
                          version=1.0)
def inference_server_get_from_uid(session: XMimSession,
                                  uid: String,
                                  reference_image: XMimImage,
                                  server_url: String,
                                  polling_interval_sec: Integer,
                                  timeout_sec: Integer):
    logger = session.createLogger()
    logger.info("Starting extension InferenceServerGetFromUid")
    try:
        client_backend = ClientBackend(base_url=server_url)
        inference_server_get(session=session,
                             uid=uid,
                             reference_image=reference_image,
                             timeout_sec=timeout_sec,
                             polling_interval_sec=polling_interval_sec,
                             client_backend=client_backend)
    except:
        logger.error(traceback.format_exc())

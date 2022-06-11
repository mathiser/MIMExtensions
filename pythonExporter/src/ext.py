import traceback
from MIMPython.EntryPoint import *
from MIMPython.SupportedIOTypes import *
import os

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

@mim_extension_entrypoint(name="Exporter4images",
                          author="Mathis Rasmussen",
                          description="Wraps and ships off four images to the inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def Exporter4images(session: XMimSession,
               img_zero: XMimImage,
               img_one: XMimImage,
               img_two: XMimImage,
               img_three: XMimImage,
               out_dir: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension Exporter4images")
        
        
        from .task_input import TaskInput

        task_input = TaskInput(meta_information=generate_image_meta_information(img_zero))
                               
        task_input.add_array(img_zero.getRawData().copyToNPArray())
        task_input.add_array(img_one.getRawData().copyToNPArray())
        task_input.add_array(img_two.getRawData().copyToNPArray())
        task_input.add_array(img_three.getRawData().copyToNPArray())
        
        task_input.add_dicom_info(generate_dicom_meta(img_zero))
        task_input.add_dicom_info(generate_dicom_meta(img_one))
        task_input.add_dicom_info(generate_dicom_meta(img_two))
        task_input.add_dicom_info(generate_dicom_meta(img_three))
        
        task_input.set_contours(img_zero.getContours())
        
        task_input.save(out_dir)
        
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())
        

@mim_extension_entrypoint(name="Exporter3images",
                          author="Mathis Rasmussen",
                          description="Wraps and ships off four images to the inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def Exporter3images(session: XMimSession,
               img_zero: XMimImage,
               img_one: XMimImage,
               img_two: XMimImage,
               out_dir: String,
               ) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension Exporter3images")

        from .task_input import TaskInput
        
        task_input = TaskInput(meta_information=generate_image_meta_information(img_zero))
                               
        task_input.add_array(img_zero.getRawData().copyToNPArray())
        task_input.add_array(img_one.getRawData().copyToNPArray())
        task_input.add_array(img_two.getRawData().copyToNPArray())
        
        task_input.add_dicom_info(generate_dicom_meta(img_zero))
        task_input.add_dicom_info(generate_dicom_meta(img_one))
        task_input.add_dicom_info(generate_dicom_meta(img_two))
        
        task_input.set_contours(img_zero.getContours())
        
        task_input.save(out_dir)
        
        
     
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())


@mim_extension_entrypoint(name="Exporter2images",
                          author="Mathis Rasmussen",
                          description="Wraps and ships off four images to the inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def Exporter2images(session: XMimSession,
               img_zero: XMimImage,
               img_one: XMimImage,
               export_dicom_info_0_or_1: Integer,
               model_human_readable_id: String,
               server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension Exporter2images")

        from .task_input import TaskInput

                task_input = TaskInput(meta_information=generate_image_meta_information(img_zero))
                               
        task_input.add_array(img_zero.getRawData().copyToNPArray())
        task_input.add_array(img_one.getRawData().copyToNPArray())
        
        task_input.add_dicom_info(generate_dicom_meta(img_zero))
        task_input.add_dicom_info(generate_dicom_meta(img_one))
        
        task_input.set_contours(img_zero.getContours())
        
        task_input.save(out_dir)
        

@mim_extension_entrypoint(name="Exporter1images",
                          author="Mathis Rasmussen",
                          description="Ships off to inference server. Contours are returned and loaded",
                          category="Inference server model",
                          institution="DCPT",
                          version=0.2)
def Exporter1images(session: XMimSession,
                           img_zero: XMimImage,
                           export_dicom_info_0_or_1: Integer,
                           model_human_readable_id: String,
                           server_url: String) -> String:
    
    try:
        logger = session.createLogger()
        logger.info("Starting extension Exporter1images")
       
        from .task_input import TaskInput
        try:
            logger.info(str(generate_dicom_meta(img_zero)))
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            
        task_input = TaskInput(meta_information=generate_image_meta_information(img_zero))
                               
        task_input.add_array(img_zero.getRawData().copyToNPArray())
        
        task_input.add_dicom_info(generate_dicom_meta(img_zero))
        
        task_input.set_contours(img_zero.getContours())
        
        task_input.save(out_dir)
            
    except Exception as e:
        logger.error("ERROR")
        logger.error(e)
        logger.error(traceback.format_exc())


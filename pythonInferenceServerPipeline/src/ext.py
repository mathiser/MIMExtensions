from MIMPython.EntryPoint import *
from MIMPython.SupportedIOTypes import *
import requests
import os
import tempfile
import zipfile
import numpy as np
import SimpleITK as sitk
import shutil
import time
from typing import List
import traceback


def get_mask_by_int(mask_int):
    d = {
    1: "Brain",
    2: "Brainstem",
    3: "Lips",
    4: "LarynxG",
    5: "LarynxSG",
    6: "Parotid_merged",
    7: "PCM_Low",
    8: "PCM_Mid",
    9: "PCM_Up",
    10: "Mandible",
    11: "SMDB_merged",
    12: "Thyroid"
    }
    return d[mask_int]

def get_cert_file_path():
        absolutepath = os.path.abspath(__file__)        
        fileDirectory = os.path.dirname(absolutepath)
        return os.path.join(fileDirectory, "omen.onerm.dk.pem")

def zip_to_np_array(zip_path, logger ) -> np.array:
    ## Unzip directory 
    with tempfile.TemporaryDirectory() as tmp_dir:
        with zipfile.ZipFile(zip_path, "r") as zip:
            zip.extractall(tmp_dir)
    
        ## Loop through and find nifti-file
        for f in os.listdir(tmp_dir):
            if f.endswith(".nii.gz"):
                ## Parse to sitk image
                logger.info("opening {}".format(os.path.join(tmp_dir, f)))
                img = sitk.ReadImage(os.path.join(tmp_dir, f))
                arr = sitk.GetArrayFromImage(img)
                ## Return array
                return arr 
        else:
            raise Exception("No nifti in output")
    
def save_image_data_to_dir(image: XMimImage, dir) -> str:
    image_data = image.getScaledData()
    image_data_arr = image_data.copyToNPArray()
    img_nii = sitk.GetImageFromArray(image_data_arr)
    img_nii.SetSpacing(image.getNoxelSizeInMm())
    
    sitk.WriteImage(img_nii, os.path.join(dir, "tmp_0000.nii.gz"), useCompression=True)
    return os.path.join(dir, "tmp_0000.nii.gz") 


@mim_extension_entrypoint(name = "00_inference_server_pipeline",
                          author = "Mathis Rasmussen",
                          description = "Runs deep learning inference with one input modality",
                          category = "",
                          institution = "DCPT",
                          version = 1.1)
def entrypoint(session : XMimSession, image : XMimImage, model_ids : String):# -> XMimSeriesView:
    logger = session.createLogger()
    logger.info("Starting extension...")
    try:
        model_ids = [int(i) for i in model_ids.split(" ")]
        for i in model_ids:
            if not (i > 0):
                raise Exception("assertion of input failed")
            
    
        ## Save image_array to nifti ...
        input_dir = tempfile.mkdtemp()
        save_image_data_to_dir(image, input_dir)
        ## ... zip the folder
        with tempfile.TemporaryFile() as tmp_file:
            with zipfile.ZipFile(tmp_file, "w", zipfile.ZIP_DEFLATED) as z:
                for file in os.listdir(input_dir):
                    z.write(os.path.join(input_dir, file), arcname=file)
            
            tmp_file.seek(0)
            
            ## ... and post to inference_server
            res = requests.post("https://omen.onerm.dk/api/tasks/",
                                params={"model_ids": model_ids},
                                files={"zip_file": tmp_file},
                                verify=get_cert_file_path())
        
        
        shutil.rmtree(input_dir)
        task_uid = res.json()["uid"]
        
         ## Make output dir and unzip response
        output_dir = tempfile.mkdtemp()
        output_zip = os.path.join(output_dir, "output.zip")
        counter = 0
        while True:
            res = requests.get("https://omen.onerm.dk/api/tasks/{}".format(task_uid),
                              stream=True,
                              verify=get_cert_file_path())
            if res.ok:
                with open(output_zip, "wb") as f:
                    for chunk in res.iter_content(chunk_size=1000000):
                        f.write(chunk)
                break
            else:
                time.sleep(5)
                counter += 5
                print("Waiting ... Waited for {} seconds".format(counter))
                if counter == 120:
                    raise Exception("Timeout")
        
        
        inference_array = zip_to_np_array(output_zip, logger)
        for no in np.unique(inference_array):
            if no == 0:
                continue

            tmp_arr = np.zeros_like(inference_array, dtype=bool)
            tmp_arr[inference_array == no] = True
            
            c_tmp = image.createNewContour(get_mask_by_int(no))
            c_tmp_data = c_tmp.getData()
            c_tmp_data.setFromNPArray(tmp_arr)

            c_tmp.redrawCompletely()
        
        shutil.rmtree(output_dir)
        #return session.addImageAndReturnView(image, "Result of mode: {}".format(str(model_ids)))

    except Exception as e:
        logger.error(traceback.format_exc())

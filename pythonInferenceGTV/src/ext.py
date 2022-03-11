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
from multiprocessing.pool import ThreadPool

def get_mask_by_int(mask_int):
    d = {
    1: "GTVs"
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
   
def save_volume_to_dir(array, spacing, dir, suffix) -> str:
    img = sitk.GetImageFromArray(array)
    img.SetSpacing(spacing)
    path =  os.path.join(dir, "tmp_{}.nii.gz".format(suffix))
    sitk.WriteImage(img, path, useCompression=True)
    return path

@mim_extension_entrypoint(name = "00_GTVs",
                          author = "Mathis Rasmussen",
                          description = "Wraps registered and aligned CT, PET, T1 and T2 and ships off to inference server. Contour is returned and loaded",
                          category = "Inference server model",
                          institution = "DCPT",
                          version = 2.0)
def entrypoint(session : XMimSession, CT : XMimImage, PET: XMimImage, T1: XMimImage, T2: XMimImage, model_ids : String) -> XMimContour:
    logger = session.createLogger()
    logger.info("Starting extension...")
    try:
        model_ids = [i for i in model_ids.split(" ")]
        if not (len(model_ids) > 0):
            raise Exception("You must provide at least one human_readable_id")
        
        ## Save image_array to nifti ...
        with tempfile.TemporaryDirectory() as input_dir:
            tasks = []
            for i, scan in enumerate([CT, PET, T1, T2]):
                logger.info("Adding task: {}".format(scan.getInfo().getCustomName()))
                tasks.append((scan.getRawData().copyToNPArray(),
                                                scan.getNoxelSizeInMm(),
                                                input_dir,
                                                str(10000+i)[1:]))
            tp = ThreadPool(4)
            tp.starmap(save_volume_to_dir, tasks)
            tp.close()
            tp.join()
                
            ## ... zip the folder
            with tempfile.TemporaryFile() as tmp_file:
                with zipfile.ZipFile(tmp_file, "w", zipfile.ZIP_DEFLATED) as z:
                    for file in os.listdir(input_dir):
                        z.write(os.path.join(input_dir, file), arcname=file)
                
                tmp_file.seek(0)
                
                ## ... and post to inference_server
                res = requests.post("https://omen.onerm.dk/api/tasks/",
                                    params={"human_readable_ids": model_ids},
                                    files={"zip_file": tmp_file},
                                    verify=get_cert_file_path())
            
            
    
        task_uid = res.json()["uid"]
        
        with tempfile.TemporaryDirectory() as output_dir:
    
             ## Make output dir and unzip response
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
                    if counter == 360:
                        raise Exception("Timeout")
            
            
            inference_array = zip_to_np_array(output_zip, logger)
            for no in np.unique(inference_array):
                if no == 1:
                    tmp_arr = np.zeros_like(inference_array, dtype=bool)
                    tmp_arr[inference_array == no] = True
                    
                    c_tmp = CT.createNewContour("GTVs")
                    c_tmp_data = c_tmp.getData()
                    c_tmp_data.setFromNPArray(tmp_arr)
        
                    c_tmp.redrawCompletely()
                    
                    return c_tmp
    except Exception as e:
        logger.error(traceback.format_exc())
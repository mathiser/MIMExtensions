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

def get_cert_file_path():
        absolutepath = os.path.abspath(__file__)        
        fileDirectory = os.path.dirname(absolutepath)
        return os.path.join(fileDirectory, "omen.onerm.dk.pem")

def zip_to_np_array(zip_path, logger) -> np.array:
    ## Unzip directory 
    try:
        tmp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, "r") as zip:
            zip.extractall(tmp_dir)
        
        for p in os.listdir(tmp_dir):
            path = os.path.join(tmp_dir, p)
            if p.endswith(".nii.gz"):
                img = sitk.ReadImage(path)
                arr = sitk.GetArrayFromImage(img)
                
                with open(path.replace(".nii.gz", ".json"), "r") as r:
                    j = json.loads(r.read()) 
                
                return j, arr
    
    except Exception as e:
        logger.error(traceback.format_exc())
    
    finally:
        shutil.rmtree(tmp_dir)
   
def save_volume_to_dir(array, spacing, dir, suffix) -> str:
    img = sitk.GetImageFromArray(array)
    img.SetSpacing(spacing)
    path =  os.path.join(dir, "tmp_{}.nii.gz".format(suffix))
    sitk.WriteImage(img, path, useCompression=True)
    return path

@mim_extension_entrypoint(name = "00_GTVt_and_GTVn",
                          author = "Mathis Rasmussen",
                          description = "Wraps registered and aligned CT, PET, T1 and T2 and ships off to inference server. Contour is returned and loaded",
                          category = "Inference server model",
                          institution = "DCPT",
                          version = 2.0)
def entrypoint(session : XMimSession, CT : XMimImage, PET: XMimImage, T1: XMimImage, T2: XMimImage, model_ids : String, timeout_seconds : Integer) -> List[XMimContour]:
    logger = session.createLogger()
    logger.info("Starting extension...")
    try:
        model_ids = [i for i in model_ids.split(" ")]
        if not (len(model_ids) > 0):
            raise Exception("You must provide at least one human_readable_id")
        
        ## Save image_array to nifti ...
        input_dir = tempfile.mkdtemp()
        for i, scan in enumerate([CT, PET, T1, T2]):
            logger.info("Saving image: {}".format(scan.getInfo().getCustomName()))
            save_volume_to_dir(scan.getRawData().copyToNPArray(),
                                            scan.getNoxelSizeInMm(),
                                            input_dir,
                                            str(10000+i)[1:])
    
            
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
        
            if res.ok:
                task_uid = res.json()["uid"]
            else:
                res.raise_for_status()
                
                
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
            
            elif res.status_code == 500:
                raise Exception("Server reports an error - quitting")
            
            else:
                time.sleep(1)
                counter += 1
                print("Waiting ... Waited for {} seconds".format(counter))
                if counter >= timeout_seconds:
                    raise Exception("Timeout")
        
        contour_return = []
        label_dict, array = zip_to_np_label_array_dict(output_zip, logger)
        for label, i in label_dict.items():    
            logger.info(label)
            label, contour = get_or_create_contour(label, ct)
            tmp_array = np.zeros_like(array, dtype=bool)
            tmp_array[array == i] = 1
            contour.getData().setFromNPArray(tmp_array)
            contour_return.append(contour)
            contour.redrawCompletely()
        
        return contour_return
    
    except Exception as e:
        logger.error(traceback.format_exc())
    
    finally:
        shutil.rmtree(input_dir)
        shutil.rmtree(output_dir)
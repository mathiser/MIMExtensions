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
import traceback
from numpy import dtype
from multiprocessing.pool import ThreadPool
from timeit import default_timer as timer
from datetime import timedelta
from importlib.resources import path
from typing import Dict, Tuple, List
import json

labels = ("Brainstem", "SpinalCord", "Lips", "Esophagus", "PCM_Low", "PCM_Mid", "PCM_Up", "Submandibular_merged", "Thyroid", "OralCavity")

def get_cert_file_path():
        absolutepath = os.path.abspath(__file__)        
        fileDirectory = os.path.dirname(absolutepath)
        return os.path.join(fileDirectory, "omen.onerm.dk.pem")


def zip_to_np_label_array_dict(zip_path, logger) -> Dict[str, Dict]:
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
    path =  os.path.join(dir, "{}.nii.gz".format(suffix))
    sitk.WriteImage(img, path, useCompression=True)
    return path


def get_or_create_contour(label: str, ct: XMimImage) -> Tuple[str, XMimContour]:
    for c in ct.getContours():
        if c.getInfo().getName() == label:
            return label, c
    else:
        c = ct.createNewContour(label)
        return label, c
        
    
@mim_extension_entrypoint(name = "01_estro_oar_bounds",
                          author = "Mathis Rasmussen",
                          description = "Runs deep learning inference with one input modality",
                          category = "",
                          institution = "DCPT",
                          version = 1.)
def entrypoint(session : XMimSession,
               ct : XMimImage) -> List[XMimContour]:
    
    logger = session.createLogger()
    logger.info("Starting extension OAR bounds extension...")
    t0 = timer()
    try:
        model_ids = [1]

        ## Save image_array to nifti ...
        input_dir = tempfile.mkdtemp()

        ## Add CT to tasks
        tasks = []
        tasks.append((ct.getRawData().copyToNPArray(),
                                             ct.getNoxelSizeInMm(),
                                             input_dir,
                                             "CT"))
        
        ## Add all organs at risk to tasks
        for label in labels:
            label, contour = get_or_create_contour(label, ct)
            tasks.append((contour.getData().copyToNPArray(),
                                            contour.getNoxelSizeInMm(),
                                            input_dir,
                                            label))
        
        tp = ThreadPool(16)
        tp.starmap(save_volume_to_dir, tasks)
        tp.close()
        tp.join()
        
        ## ... zip the folder
        with tempfile.TemporaryFile() as tmp_file:
            with zipfile.ZipFile(tmp_file, "w", zipfile.ZIP_STORED) as z:
                for file in os.listdir(input_dir):
                    z.write(os.path.join(input_dir, file), arcname=file)
            
            # Reset pointer ready to read again
            tmp_file.seek(0)
                        
            ## ... and post to inference_server
            res = requests.post("https://omen.onerm.dk/api/tasks/",
                                params={"model_ids": model_ids},
                                files={"zip_file": tmp_file},
                                verify=get_cert_file_path())
            
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
            
            elif res.status_code == 500:
                raise Exception("Server reports an error - quitting")
            else:
                time.sleep(1)
                counter += 1
                print("Waiting ... Waited for {} seconds".format(counter))
                if counter == 300:
                    raise Exception("Timeout")
        
        contour_return = []
        label_dict, array = zip_to_np_label_array_dict(output_zip, logger) ## contains {"oar": {"array": ndarray, "json": label_dict}}}
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
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

labels = {"Brainstem": 1, "Lips": 3, "Esophagus": 4, "PCM_Low": 5, "PCM_Mid": 6, "PCM_Up": 7, "OralCavity": 8, "Submandibular_merged": 9, "Thyroid": 10}

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
        
    
@mim_extension_entrypoint(name = "01_estro_oar_bounds_study",
                          author = "Mathis Rasmussen",
                          description = "Runs deep learning inference with one ct and bounds",
                          category = "",
                          institution = "DCPT",
                          version = 2.0)
def entrypoint(session : XMimSession,
               ct : XMimImage,
               human_readable_ids : String,
               timeout : Integer,
               ping_interval : Integer,
               inference_server_url : String,
               ) -> List[XMimContour]:
    
    logger = session.createLogger()
    logger.info("Starting extension OAR bounds extension...")
    try:
        human_readable_ids = human_readable_ids.split(" ")


        ## make an array of zeros from the first label and break
        for label, i in labels.items():
            label, contour = get_or_create_contour(label, ct)
            merged_array = np.zeros_like(contour.getData().copyToNPArray())
            break
        
        ## merge all labels into merged_array
        for label, i in labels.items():
            label, contour = get_or_create_contour(label, ct)
            contour_array = contour.getData().copyToNPArray()
            merged_array[contour_array != 0] = i
            
        ## temporary dir to store ct and oars - to be zipped.
        input_dir = tempfile.mkdtemp()

        # to be zipped and shipped
        tasks = []

        ## Add CT to tasks
        tasks.append((ct.getRawData().copyToNPArray(),
                                             ct.getNoxelSizeInMm(),
                                             input_dir,
                                             "CT"))
        
        ## Add merged OAR
        tasks.append((merged_array,
                    ct.getNoxelSizeInMm(),
                    input_dir,
                    "OAR"))

        ## Save all tasks to input_dir
        for t in tasks:
            save_volume_to_dir(*t)
        
        ## zip the input_dir
        with tempfile.TemporaryFile() as tmp_file:
            with zipfile.ZipFile(tmp_file, "w", zipfile.ZIP_STORED) as z:
                for file in os.listdir(input_dir):
                    z.write(os.path.join(input_dir, file), arcname=file)
            
            # Reset pointer ready to read again
            tmp_file.seek(0)
                        
            ## ... and post to inference_server
            res = requests.post(f"{inference_server_url}/api/tasks/",
                                params={"human_readable_ids": human_readable_ids},
                                files={"zip_file": tmp_file},
                                verify=get_cert_file_path())
            
            task_uid = res.json()["uid"]
    
         ## Make output dir and unzip response
        output_dir = tempfile.mkdtemp()
        output_zip = os.path.join(output_dir, "output.zip")
        counter = 0
        while counter <= int(timeout):
            res = requests.get(f"{inference_server_url}/api/tasks/{task_uid}",
                              stream=True,
                              verify=get_cert_file_path())
            if res.ok:
                ## If okay, write output_zip to output_zip
                with open(output_zip, "wb") as f:
                    for chunk in res.iter_content(chunk_size=1000000):
                        f.write(chunk)
                
                ## ... and break out of while loop
                break
            
            elif res.status_code == 500:
                raise Exception("Server reports an error - quitting")
            
            else:
                time.sleep(int(ping_interval))
                counter += int(ping_interval)
        
        else:
            raise Exception("Timeout")
        
        ## load and redraw returned segmentations
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
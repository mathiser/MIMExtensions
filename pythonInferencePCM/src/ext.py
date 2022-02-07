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
import json

def get_mask_integers(mask_name):
    d = {
        "PCM_Low": 7,
        "PCM_Mid": 8,
        "PCM_Up": 9
    }
    return d[mask_name]

def get_cert_file_path():
        absolutepath = os.path.abspath(__file__)        
        fileDirectory = os.path.dirname(absolutepath)
        return os.path.join(fileDirectory, "omen.onerm.dk.pem")

def zip_to_np_array(zip_path, logger) -> np.array:
    ## Unzip directory 
    with tempfile.TemporaryDirectory() as tmp_dir:
        with zipfile.ZipFile(zip_path, "r") as zip:
            zip.extractall(tmp_dir)
    
        ## Loop through and find nifti-file
        for f in os.listdir(tmp_dir):
            if f.endswith(".npy"):
                ## Parse to sitk image
                logger.info("opening {}".format(os.path.join(tmp_dir, f)))
                return np.load(os.path.join(tmp_dir, f)) 
        else:
            raise Exception("No nifti in output")
    
def save_volumes_to_dir(arrays: dict, meta, dir):
    img_path =  os.path.join(dir, "arrays")
    np.savez_compressed(img_path, **arrays)

    with open(img_path + ".json", "w") as f:
        f.write(json.dumps(meta))
        
@mim_extension_entrypoint(name = "00_inference_server_pcm",
                          author = "Mathis Rasmussen",
                          description = "Runs deep learning inference with one input modality",
                          category = "",
                          institution = "DCPT",
                          version = 1.)
def entrypoint(session : XMimSession,
               ct : XMimImage):# -> XMimSeriesView:
    
    logger = session.createLogger()
    logger.info("Starting extension...")
    t0 = timer()
    try:
        model_ids = [2]
        ## Extract PCMs:
        for c in ct.getContours():
            if c.getInfo().getName() == "PCM_Low":
                pcm_low = c
                logger.info(f"PCM_Low found")
            elif c.getInfo().getName() == "PCM_Mid":
                pcm_mid = c
                logger.info(f"PCM_Mid found")
            elif c.getInfo().getName() == "PCM_Up":
                pcm_up = c
                logger.info(f"PCM_Up found")
            else: 
                pass    
        
        if not pcm_low and pcm_mid and pcm_up:
            raise Exception("Missing PCM input. Make sure that all PCMs (PCM_Low, PCM_Mid, PCM_Up) exist")
        
        ## Save image_array to nifti ...
        input_dir = tempfile.mkdtemp()
        
        ## Pack ct and the three contours to inputzip with appropriate naming for model.
        #save_image_data_to_dir(ct, input_dir, "0000")
        
        ## Same for PCMs
        t01 = timer()
        arrays = {}
        arrays["0000"] = ct.getRawData().copyToNPArray()
        arrays["0001"] = pcm_low.getData().copyToNPArray()              
        arrays["0002"] = pcm_mid.getData().copyToNPArray()              
        arrays["0003"] = pcm_up.getData().copyToNPArray()
        meta = {}
        meta["spacing"] = ct.getNoxelSizeInMm();
        meta["shape"] = arrays["0000"].shape
           
        save_volumes_to_dir(arrays, meta, input_dir)
        
        t1 = timer()
        logger.info(f"Finished extracting CT and PCMs: {timedelta(seconds=t1-t01)}")
        
        ## ... zip the folder
        with tempfile.TemporaryFile() as tmp_file:
            with zipfile.ZipFile(tmp_file, "w", zipfile.ZIP_STORED) as z:
                for file in os.listdir(input_dir):
                    z.write(os.path.join(input_dir, file), arcname=file)
            
            tmp_file.seek(0)
            
            t2 = timer()
            logger.info(f"Finished zipping: {timedelta(seconds=t2-t1)}")
            
            ## ... and post to inference_server
            res = requests.post("https://omen.onerm.dk/api/tasks/",
                                params={"model_ids": model_ids},
                                files={"zip_file": tmp_file},
                                verify=get_cert_file_path())
        
        
        shutil.rmtree(input_dir)
        task_uid = res.json()["uid"]
        t3 = timer()
        logger.info(f"Send to server took: {timedelta(seconds=t3-t2)}")
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
                time.sleep(1)
                counter += 1
                print("Waiting ... Waited for {} seconds".format(counter))
                if counter == 240:
                    raise Exception("Timeout")
        
        t4 = timer()
        logger.info(f"Waited for response in: {timedelta(seconds=t4-t3)}")
        
        inference_array = zip_to_np_array(output_zip, logger)
        for t in [("PCM_Low", pcm_low), ("PCM_Mid", pcm_mid), ("PCM_Up", pcm_up)]:
            name, c = t
            
            tmp_arr = np.zeros_like(inference_array, dtype=bool)
            tmp_arr[inference_array == get_mask_integers(name)] = 1
            logger.info("{} has {} voxels.".format(name, np.count_nonzero(tmp_arr)))
            c.getData().setFromNPArray(tmp_arr)
            
            c.redrawCompletely()
        
        t5 = timer()
        logger.info(f"Loaded into mim: {timedelta(seconds=t5-t4)}")
        
        shutil.rmtree(output_dir)
        #return session(ct, "Result of mode: {}".format(str(model_ids)))
        
        t6 = timer()
        logger.info(f"Total time: {timedelta(seconds=t6-t0)}")
        
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        if input_dir:
            if os.path.exists(input_dir):
                shutil.rmtree(input_dir)
        if output_dir:
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)

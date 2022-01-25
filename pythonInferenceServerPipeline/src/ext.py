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
def get_cert_file_path():
        absolutepath = os.path.abspath(__file__)        
        fileDirectory = os.path.dirname(absolutepath)
        return os.path.join(fileDirectory, "omen.onerm.dk.pem")

def zip_to_np_array(zip_path) -> np.array:
    try:
        ## Unzip directory 
        with tempfile.TemporaryDirectory() as tmp_dir:
            with zipfile.ZipFile(zip_path, "r") as zip:
                zip.extractall(tmp_dir)
        
            ## Loop through and find nifti-file
            for f in os.listdir(tmp_dir):
                if f.endswith(".nii.gz"):
                    ## Parse to sitk image
                    img = sitk.ReadImage(os.path.join(tmp_dir, f))
                    
                    ## Return array
                    return sitk.GetArrayFromImage(img) 
            else:
                raise Exception("No nifti in output")
    except Exception as e:
        raise e
    
def save_image_data_to_dir(image: XMimImage, dir) -> str:
    try:
        img = sitk.GetImageFromArray(image.getScaledData().copyToNPArray(), )
        img.SetSpacing(image.getNoxelSizeInMm())
        
        sitk.WriteImage(img, os.path.join(dir, "tmp_0000.nii.gz"))
        return os.path.join(dir, "tmp_0000.nii.gz")    
    except Exception as e:
        raise e



@mim_extension_entrypoint(name = "00_inference_server_pipeline",
                          author = "Mathis Rasmussen",
                          description = "Runs deep learning inference with one input modality",
                          category = "",
                          institution = "DCPT",
                          version = 1.1)
def entrypoint(session : XMimSession, vol : XMimSeriesView, model_ids : String) -> XMimSeriesView:
    logger = session.createLogger()
    logger.info("Starting extension...")
    try:
        if len(model_ids) is "":
             model_ids = "6 4 1 5 3"
        model_ids = [int(i) for i in model_ids.split(" ")]
        for i in model_ids:
            if not (i > 0):
                raise Exception("assertion of input failed")
            
            
        ## Load mutable copy
        image = vol.getImage()
#        data = image.getScaledData()    
 #       nd_array = data.copyToNPArray()
        
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
        
        
        inference_array = zip_to_np_array(output_zip)
        for no in np.unique(inference_array):
            if no == 0:
                continue
            c_tmp = image.createNewContour(str(no))
            c_tmp_data = c_tmp.getData()
            
            tmp_arr = np.zeros_like(inference_array, dtype=bool)
            tmp_arr[inference_array == no] = True
            c_tmp_data.setFromNPArray(tmp_arr)

            c_tmp.redrawCompletely()
        
        shutil.rmtree(output_dir)
        return session.addImageAndReturnView(image, "Result of mode: {}".format(str(model_ids)))

    except Exception as e:
        #image = vol.getImage().getMutableCopy()
        #data = image.getScaledData()    
        
        #threshold = 200
        #nd_array = data.copyToNPArray()
        #nd_array[nd_array < threshold] = -1024
        
        #data.setFromNPArray(nd_array)
        return session.addImageAndReturnView(image, str(e))


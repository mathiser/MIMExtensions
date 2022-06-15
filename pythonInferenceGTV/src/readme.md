## Welcome to the MIMExtension to serve the inference server (https://github.com/mathiser/inference_server)

This extension is build up as follows:
### ext.py
Is the main file containing entrypoints to run from MIM.
There are four posting methods, which zips images and ships them off to an instance of the inference server. Each of the four (func InferenceServerXimages)
generates an object task_input of type TaskInput, and parse it on to the function "post". "Post" takes care of everything that is necessary to post
the TaskInput to the server, and it returns a UID of the task, which is needed to retrieve the task output again.
 
The function "InferenceServerGetFromUid" takes the UID from a posted task and polls the inference server with a specified interval unil the task is retrieved or timeout.
The retrieved task is loaded as a TaskOutput and loaded into MIM as contours to the reference_image (always img_zero) through ContourLoader.

### inference_client.py
Contains the InferenceClient, which contains a function post_task to post a TaskInput and a function get_task to get the task output from a UID
Actual http-methods are abstracted away to ClientBackend in client_backend.py

### client_backend.py
Contains ClientBackend which takes care of the actual http post and get.

### task_input.py
A container for images as numpy arrays. Can serve them as a temporary zip file for posting

### task_output.py
A container for the output of the InferenceServer. Can serve predictions as a dictionary of {segmentation name: np.ndarray dtype==bool}

### contour_loader.py
Contains ContourLoader, which can set contours to a reference image the dictionary of TaskOutput.get_output_as_label_array_dict

## Interface to inference server
The interface between MIM and the inference server is arbitrary, and thus the following format must be followed exactly

### Variables
When launching InferenceServerXimages extensions the following variables must be set:
- img_{zero..three}: Is the MIM images to ship off.
- export_dicom_info: 0 or 1: sets whether all dicom tags should be shipped along. 
- model_human_readable_id: is the human readable id of the model one prefer to run a given set of images on.
- server_url: is the base url of the instance of the inference server. Could look like: "https://omen.onerm.dk". Do not omit "https://"

When launching InferenceServerGetFromUid the following variables must be set:
- uid: string of the uid returned from a InferenceServerXimage extension.
- reference_image: the mim image to load contours onto
- server_url: is the base url of the instance of the inference server. Could look like: "https://omen.onerm.dk". Do not omit "https://"
- polling_interval_sec: The interval between each poll to the server in seconds
- timeout_sec: Timeout polling and the extension after X seconds

### MIM outputs
TheInferenceServerXimages output:
- tmp_0000.nii.gz (img_zero)
- tmp_0001.nii.gz (img_one)
- tmp_0002.nii.gz (img_two)
- tmp_0003.nii.gz (img_three)
- meta.json (Contains scaling_factor and spacing of img_zero)

Optionally:
- tmp_0000.dicom_info.json
- tmp_0001.dicom_info.json
- tmp_0002.dicom_info.json
- tmp_0003.dicom_info.json

### MIM inputs
When InferenceServerGetFromUid is run and a zip is succesfully received, MIM expects the following files:
- {ANY_NAME}.nii.gz (With contours as integers in a 3D array. Dimensions must be matched with scaling_factor to the input reference image.)
- {ANY_NAME}.json (A json dumped dict of the contour integers as keys and label names as values: {"1": "GTVt", "2": "CaudaEquina"}  
Note that ANY_NAME can be anything, as long as the .nii.gz file matches the .json.




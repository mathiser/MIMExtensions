def get_cert_file_path():
        absolutepath = os.path.abspath(__file__)        
        fileDirectory = os.path.dirname(absolutepath)
        return os.path.join(fileDirectory, "omen.onerm.dk.pem")

def get_spacing_from_image(image: XMimImage):
    return image.getNoxelSizeInMm()

def get_np_array_from_image(image: XMimImage):
    return image.getRawData().copyToNPArray()
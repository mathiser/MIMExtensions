try: # For production
    from MIMPython.SupportedIOTypes import String, Integer, XMimImage

except ModuleNotFoundError: ## For Testing
    from testing.mock_classes import XMimImage, XMimContour

def generate_image_meta_information(reference_image: XMimImage):
        meta = {}
        
        # Scaling factor from image
        contour = reference_image.createNewContour('scaling_factor_getter')
        meta["scaling_factor"] = list(contour.getMultiplier())
        contour.delete()
        
        # Spacing if images
        meta["spacing"] = list(reference_image.getNoxelSizeInMm())
        return meta

def generate_dicom_meta(reference_image: XMimImage):
    tags = reference_image.getInfo().getDicomInfo().getTags()
    tag_dict = {tag: str(reference_image.getInfo().getDicomInfo().getValue(tag)) for tag in tags}
    return tag_dict

def generate_meta_for_contour(contour: XMimContour):
    d = {}
    d["name"] = contour.getInfo().getName()
    d["dimensions"] = contour.getDims()
    d["multiplier"] = contour.getMultiplier()
    
    return d
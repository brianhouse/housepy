from PIL import Image
from .log import log

def ipl_to_pil(cv_image):
    """Convert an ipl (OpenCV) image to PIL"""
    import cv    
    pil_image = Image.fromstring("RGB", cv.GetSize(cv_image), cv_image.tostring(), "raw", "BGR")
    return pil_image
    
def pil_to_ipl(pil_image):
    """Convert a PIL image to ipl (OpenCV)"""    
    import cv
    cv_image = cv.CreateImageHeader(pil_image.size, cv.IPL_DEPTH_8U, 3)
    cv.SetData(cv_image, pil_image.rotate(180).tostring()[::-1])
    return cv_image
    
def numpy_to_ipl(data, channels=1):
    """Convert a NumPy image to ipl (OpenCV) with three channels"""    
    import cv    
    if channels == 1:
        cv_image = cv.CreateImageHeader((data.shape[1], data.shape[0]), cv.IPL_DEPTH_16U, 1)
        cv.SetData(cv_image, data.tostring(), data.dtype.itemsize * data.shape[1])
    elif channels == 3:
        cv_image = cv.CreateImageHeader((data.shape[1], data.shape[0]), cv.IPL_DEPTH_8U, 3)
        cv.SetData(cv_image, data[:, :, ::-1].tostring(), data.dtype.itemsize * 3 * data.shape[1])     # we swap from RGB to BGR here
    return cv_image
    
def resize(image, size, exact=True):
    """Exact mode crops to create the desired aspect ratio. Otherwise, an image of the maximum size will be returned that fits in the bounding box. PIL."""
    filename = None
    if type(image) == str or type(image) == str:
        filename = image
        image = Image.open(filename)
    source_width = image.size[0]
    source_height = image.size[1] 
    target_width, target_height = size                           
    if target_width == 0 or target_height == 0:
        log.warning("Cannot have a dimension of 0")
        return image    
    source_ratio = float(source_width) / float(source_height)
    target_ratio = float(target_width) / float(target_height)            
    # log.info("--> source %sx%s (%s)" % (source_width, source_height, source_ratio))
    # log.info("--> target %sx%s (%s)" % (target_width, target_height, target_ratio))
    if exact:
        if source_ratio < target_ratio:
            res = int(target_width), int(target_width / source_ratio)
            image = image.resize(res, Image.ANTIALIAS)
            cropoff = (image.size[1] - target_height) / 2
            crop = 0, cropoff, image.size[0], image.size[1] - cropoff
            image = image.crop(crop)
        else:
            res = int(target_height * source_ratio), int(target_height)
            image = image.resize(res, Image.ANTIALIAS)
            cropoff = (image.size[0] - target_width) / 2
            crop = cropoff, 0, image.size[0] - cropoff, image.size[1]
            image = image.crop(crop)
    else:
        if source_ratio < target_ratio:
            res = int(target_height * source_ratio), int(target_height)
        else:
            res = int(target_width), int(target_width / source_ratio)
        image = image.resize(res, Image.ANTIALIAS)
    if filename:
        image.save(filename)
    return image    
    
def to_string(image):
    import io    
    f = io.StringIO()
    image.save(f, "PNG")
    f.seek(0)                    
    return f.read()
  
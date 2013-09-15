from PIL import Image
from .log import log

    
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
  
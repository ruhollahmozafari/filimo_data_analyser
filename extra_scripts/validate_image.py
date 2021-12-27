from extra_scripts.EMS import validation_error


def validate_image(image, megabyte_limit=1):
    ImageSize = image.file.size
    if ImageSize > megabyte_limit*1024*1024:
        raise validation_error("Max file size is %sMB" % str(megabyte_limit))

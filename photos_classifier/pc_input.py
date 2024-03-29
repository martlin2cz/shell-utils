""" The input (load and group) module for the photos_classifier """


###############################################################################

import logging
import datetime
import os

import exifread
import datetime

import sys
import yaml

###############################################################################

""" The indicator of no date avaiable (do not use None, causes ton of issues) """
NO_DATE=datetime.datetime(1970, 1, 1, 0, 0, 0)

""" The logger. """
LOGGER = logging.getLogger("p_c")

###############################################################################

def datetime_of_photo_raw(photo_file):
    """ Returns the datetime of the photo taken at, as raw exif data """

    with open(photo_file, 'rb') as fh:
        tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal")
        if "EXIF DateTimeOriginal" in tags.keys():
            return tags["EXIF DateTimeOriginal"]

        if "EXIF DateTimeDigitized" in tags.keys():
            return tags["EXIF DateTimeDigitized"]

        if "Image DateTime" in tags.keys():
            return tags["Image DateTime"]

        raise ValueError(f"The file {photo_file} doesn't contain EXIF timestamp")

def datetime_of_photo(photo_file):
    """ Returns the actual DATE AND TIME of the photo taken at, but as datetime date object """ 

    try:
        raw_datetime = datetime_of_photo_raw(photo_file)
        actual_datetime = datetime.datetime.strptime(str(raw_datetime), "%Y:%m:%d %H:%M:%S")
        return actual_datetime
    except Exception as ex:
        LOGGER.debug(f"Datetime of photo {photo_file} obtain failed: {ex}")
        return NO_DATE


def datetime_of_video_raw(video_file):
    """ Returns the datetime of the video shot at, as a raw string """

    video_metadata = ffmpeg.probe(video_file)
    for stream in video["streams"]:
        if "tags" in keys(stream):
            tags = stream["tags"]
            if "creation_time" in tags:
                return tags["creation_time"]

    raise ValueError(f"The file {video_file} doesn't contain any creation_time metadata")
 
def datetime_of_video(video_file):
    """ Returns the actual DATE AND TIME of the video shot at, but as datetime date object """ 

    try:
        raw_datetime = datetime_of_video_raw(video_file)
        actual_datetime = datetime.datetime.strptime(srt, "%Y-%m-%dT%H:%M:%S.%f%z")
        return actual_datetime
    except Exception as ex:
        LOGGER.debug(f"Datetime of video {video_file} obtain failed: {ex}")
        return NO_DATE
   

def datetime_of_media(media_file):
    """ Returns the actual DATE AND TIME of the photo/video taken at, as datetime date object """ 

    LOGGER.debug(f"Loading datetime of taken/shot of {media_file} ...")
        
    media_datetime = datetime_of_photo(media_file)
    if media_datetime != NO_DATE:
        LOGGER.debug(f"Media file {media_file} is a photo taken at {media_datetime}")
        return media_datetime

    media_datetime = datetime_of_video(media_file)
    if media_datetime != NO_DATE:
       LOGGER.debug(f"Media file {media_file} is a video shot at {media_datetime}")
       return media_datetime

    LOGGER.error(f"Media file {media_file} datetime of take/shot obtain failed")
    return NO_DATE


###############################################################################

def list_files(directories, recurse):
    """ Lists all the files in the given directories, possibly recurring """

    #TODO ensure existence

    result = []
    for directory in directories:
        for (dirpath, dirs, files) in os.walk(directory):
            LOGGER.debug(f"Loaded files {files} in dir {dirpath}")
            #TODO filter files by extension
            files_resolved = [os.path.join(dirpath, f) for f in files]
            result.extend(files_resolved)
            if not recurse:
                break

    return result

def load(directories, recurse):
    """ Loads the medias and their date of taken into file->datetime dict,
        either from the directories (if provided) or from YAML read from stdin (if no dirs).
    """
    
    if len(directories) > 0:
        LOGGER.info(f"Loading media files from {directories}")
        files = list_files(directories, recurse)
        LOGGER.info(f"Loaded  {len(files)} media files")

        LOGGER.info(f"Loading dates of taken of {len(files)} media files")
        with_datetimes = dict(map( lambda f: (f, datetime_of_media(f)), files))
        LOGGER.info(f"Loaded  dates of taken of {len(files)} media files")

        return with_datetimes

    else:
        LOGGER.info(f"Loading media files with dates of taken from YAML on stdin")
        _input = sys.stdin
        with_datetimes = load_from_yaml(_input)
        LOGGER.info(f"Loaded  {len(with_datetimes)} media files with dates of taken")

        return with_datetimes


###############################################################################

def load_from_yaml(_input):
    """ Loads the dict file->datetime from the given yaml file """

    return yaml.load(_input, Loader=yaml.CLoader)



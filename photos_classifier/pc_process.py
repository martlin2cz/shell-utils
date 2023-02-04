""" The middle (the processing) module of the photos_classifier. 
Collects data from the input and provides them to the output. """

###############################################################################

import pc_input

import logging
import datetime


###############################################################################

LOGGER = logging.getLogger("p_c")
###############################################################################

def load_and_group_by_date(directory, recurse):
    """ Loads the medias in the given directory and groups them by date of taken """

    files = pc_input.load(directory, recurse)
    files_count = len(files)

    result = {}
    for media_file in files.keys():
        media_datetime = files[media_file]
        date = media_datetime.date()
        group_of_date = None

        if date in result.keys():
            LOGGER.debug(f"Inserting {media_file} into existing group {date}")
            group_of_date = result[date]
        else:
            LOGGER.debug(f"Creating new group {date} for {media_file}")
            group_of_date = []
            result[date] = group_of_date

        group_of_date.append(media_file)

    groups_count = len(result)
    LOGGER.info(f"Collected {groups_count} groups, averaging {files_count / groups_count} medias per group")

    return result

def load_and_group_by_day_and_hour(directory, recurse):
    """ Loads the medias in the given directory and groups them by date and hour of taken """

    files = pc_input.load(directory, recurse)
    files_count = len(files)

    result = {}
    for media_file in files.keys():
        media_datetime = files[media_file]
        hour = media_datetime.replace(microsecond=0, second=0, minute=0)
        group_of_hour = None

        if hour in result.keys():
            LOGGER.debug(f"Inserting {media_file} into existing group {hour}")
            group_of_hour = result[hour]
        else:
            LOGGER.debug(f"Creating new group {hour} for {media_file}")
            group_of_hour = []
            result[hour] = group_of_hour

        group_of_hour.append(media_file)

    groups_count = len(result)
    LOGGER.info(f"Collected {groups_count} groups, averaging {files_count / groups_count} medias per group")

    return result



""" The middle (the processing) module of the photos_classifier. 
Collects data from the input and provides them to the output. """

###############################################################################

import pc_input

import logging
import datetime
import pandas

import pprint

###############################################################################

""" The logger. """
LOGGER = logging.getLogger("p_c")

""" The mapping of groupper->range of "children" sub-groups (1-7 days a week, 0-59 minutes in hour, and so) """
SUBGROUP_CHILDREN_RANGE_MAPPING = { "month": range(1, 13), "week": range(1, 4), "_day-of-week": range(0, 7), "day": range(1, 31), "hour": range(0, 24), "_minute": range(0, 60) }

""" The mapping of groupper->child groupper (year->month, ...) """
SUBGROUP_CHILD_GROUPPER_MAPPING = { "year": "month", "month": "day", "week": "_day-of-week", "day": "hour", "hour": "_minute" }

###############################################################################

def range_from_first_to_last(dates, groupper):
    """ Returns range range from first to last dates in the given dates stepped by the groupper """

    min_date = min(dates)
    if (min_date == pc_input.NO_DATE):
        min_date = sorted(dates)[1]

    max_date = max(dates)

    #child_groupper = SUBGROUP_CHILD_GROUPPER_MAPPING[groupper]
    groupper_to_freq_map = {"year": "Y", "month": "MS", "week": "W", "day": "D", "hour": "H", "_minute": "m"}
    freq_identifer = groupper_to_freq_map[groupper]

    ranged = pandas.date_range(min_date, max_date, freq = freq_identifer)

    return ranged

def range_whole_interval(dates, groupper):
    """ Returns range of the whole interval (represented by one unit of the groupper) owning the given dates """

    # HACK: if someone would ever try to list all the years within the ... universe,
    # just list from first to last of the years
    if groupper == "year":
        return range_from_first_to_last(dates, groupper)

    dates_tmp_iter = iter(dates)
    some_date = next(dates_tmp_iter)
    if some_date == pc_input.NO_DATE:
        if len(dates) > 1:
            some_date = next(dates_tmp_iter)
        else:
            return [pc_input.NO_DATE]

    # HAACK: compute_key of _day-of-week is actually the date itself, 
    # we have to adjust that to compute the start of the week (only in this particular case)
    key_groupper = groupper if groupper != "_day-of-week" else "week"
    start_date = compute_key(some_date, key_groupper)

    #sub_groupper = SUBGROUP_CHILD_GROUPPER_MAPPING[groupper]
    children_range = SUBGROUP_CHILDREN_RANGE_MAPPING[groupper]

    result = []
    for child_i in children_range:
        sub_date = combine_key(start_date, groupper, child_i)
        result.append(sub_date)    
    
    return result
        

def range_the_dates(groups, groupper, fill):
    """ Returns the range of dates to iterate over in the given groups.
    If fill is true, returns all dates between the starting and ending.
    Otherwise just the dates of the groups. """

    # if has only one actual (non-NO_DATE) date, we doesn't have to
    # take the fill into an account
    has_only_one_actual_date = (len(groups.keys()) <= 1) and (pc_input.NO_DATE not in groups.keys()) \
                            or (len(groups.keys()) <= 2) and (pc_input.NO_DATE in groups.keys())

    if fill == "none":
        return sorted(set(groups.keys()))

    if fill == "fill-the-interval":
        if len(groups.keys()) < 1:
            return []
        else:
            return range_whole_interval(groups.keys(), groupper)

    if has_only_one_actual_date:
        return groups.keys()

    if fill == "from-first-to-last":
        return range_from_first_to_last(groups.keys(), groupper)
    
    raise ValueError(f"Unsupported fill {fill}")

###############################################################################

def process(files, groupper, fill_missing, quora, make_sub_groups):
    """ Does the actual preparation. Groups the files (optionally constructing sub-groups) and optionally fills missing (y/n) and/or filters out based on the given quora (number or None). """


    LOGGER.info(f"Groupping {len(files)} files by groupper {groupper}")
    groups = group_by(files, groupper)
    LOGGER.info(f"Groupped  {len(files)} files into {len(groups)} groups")

    if make_sub_groups:
        LOGGER.info(f"Sub-groupping {len(groups)} groups")
        groups = sub_group(groups, files, groupper)
        LOGGER.info(f"Sub-groupped  {len(groups)} groups")

    groups_fill = "from-first-to-last" if fill_missing else "none"
    empty_filler = "empty-dict" if make_sub_groups else "empty-list"

    LOGGER.info(f"Preparing {len(groups)} groups")
    groups = prepare_groups(groups, groupper, groups_fill, quora, empty_filler)
    LOGGER.info(f"Prepared  {len(groups)} groups")

    if make_sub_groups:
        sub_fill = "fill-the-interval"
        sub_quora = None
        LOGGER.info(f"Preparing {len(groups)} subgroups")
        groups = prepare_sub_groups(groups, groupper, sub_fill, sub_quora)
        LOGGER.info(f"Prepared  {len(groups)} subgroups")

    return groups

###############################################################################

def prepare_sub_groups(subgrouped_grups, groupper, fill, quora):
    """ Does all the technical work regarding to the subgrouped groups (delegates to prepare_groups for each sub-group) """

    subgroupper = SUBGROUP_CHILD_GROUPPER_MAPPING[groupper]
    LOGGER.debug(f"Preparing {len(subgrouped_grups)} sub-groups groupped by {groupper}/{subgroupper} by filling strategy {fill} and limiting to quora {quora}")

    result = {}
    for group_date in subgrouped_grups.keys():
        subgroup = subgrouped_grups[group_date]
        prepared_subgroup = prepare_groups(subgroup, subgroupper, fill, quora, "empty-list")
        result[group_date] = prepared_subgroup

    return result 

def prepare_groups(groups, groupper, fill, quora, empty_filler):
    """ Does all the technical work regarding to the groups: Fills missing or drops extra groups. """

    LOGGER.debug(f"Preparing {len(groups)} groups groupped by {groupper} by filling strategy {fill} and limiting to quora {quora}")

    ranged = range_the_dates(groups, groupper, fill)
    result = {}    
    for media_date in ranged:
        media_files = None
        if media_date in groups.keys():
            media_files = groups[media_date]
        else:
            empty_value = compute_empty_value(empty_filler)
            media_files = empty_value

        if quora and len(media_files) < quora:
            pass
        else:
            result[media_date] = media_files

    return result

        
def compute_empty_value(empty_filler):
    """ Returns the instance particular value to be used as the filler based on the key (either empty-list or empty-value) """

    if empty_filler == "empty-list":
        return []

    if empty_filler == "empty-dict":
        return {}

    raise ValueError(f"Unknown {empty_filler}")

def sub_group(groups, files, groupper):
    """ Groups each of the group (grouped by the groupper) into groups of sub-groups. """

    subgroup_groupper = SUBGROUP_CHILD_GROUPPER_MAPPING[groupper]
    LOGGER.debug(f"Groupping {len(groups)} groups (groupped by {groupper}) by sub-groupper {subgroup_groupper})")

    result = {}    
    for media_date in groups.keys():
        group_files_list = groups[media_date]
        group_files_dated = dict(map(lambda f: (f, files[f]), group_files_list))

        subgroup_groups = group_by(group_files_dated, subgroup_groupper)
        result[media_date] = subgroup_groups

    return result


def group_by(files, groupper):
    """ Groups the given file->datetime dict by the given groupper (years, months, weeks, days, hours) """

    LOGGER.debug(f"Groupping {len(files)} files by the groupper {groupper}")

    files_count = len(files)
    if files_count == 0:
        LOGGER.warn(f"No files to be groupped")
        return {}
    
    result = {}
    for media_file in files.keys():
        media_datetime = files[media_file]
        group_key = compute_key(media_datetime, groupper)
        group_of_key = None

        if group_key in result.keys():
            LOGGER.debug(f"Inserting {media_file} ({media_datetime}) into existing group {group_key}")
            group_of_key = result[group_key]
        else:
            LOGGER.debug(f"Creating new group {group_key} for {media_file} ({media_datetime})")
            group_of_key = []
            result[group_key] = group_of_key

        group_of_key.append(media_file)

    groups_count = len(result)
    LOGGER.debug(f"Collected {groups_count} groups, averaging {files_count / groups_count} medias per group")

    return result


###############################################################################

def combine_key(media_datetime, sub_groupper, sub_value):
    """ Returns the given datetime but with the given value of the groupper set """    

    if media_datetime == pc_input.NO_DATE:
        return pc_input.NO_DATE

    if sub_groupper == "year":
        raise ValueError(f"Year can never be a sub_groupper")
        
    if sub_groupper == "month":
        return media_datetime.replace(month = sub_value)

    if sub_groupper == "week":
        #raise ValueError(f"Week can never be a sub_groupper")
        return media_datetime + datetime.timedelta(weeks = sub_value)

    if sub_groupper == "_day-of-week":
        return media_datetime + datetime.timedelta(days = sub_value)

    if sub_groupper == "day":
        # try-except because not all months has 31 days
        try:
            return media_datetime.replace(day = sub_value)
        except:
            return None    

    if sub_groupper == "hour":
        return media_datetime.replace(hour = sub_value)

    if sub_groupper == "_minute":
        return media_datetime.replace(minute = sub_value)

    raise ValueError(f"Unsupported groupper: {groupper}")

def compute_key(media_datetime, groupper):
    """ Extracts the datetime "rounded" (floored) to the given groupper unit """

    if media_datetime == pc_input.NO_DATE:
        return pc_input.NO_DATE

    if groupper == "year":
        return media_datetime.replace(microsecond=0, second=0, minute=0, hour=0, day = 1, month = 1)

    if groupper == "month":
        return media_datetime.replace(microsecond=0, second=0, minute=0, hour=0, day = 1)

    if groupper == "week":
        _day = media_datetime.replace(microsecond=0, second=0, minute=0, hour=0)
        return _day - datetime.timedelta(days=_day.weekday())

    if groupper == "_day-of-week":
        # little tricky
        _day = media_datetime.replace(microsecond=0, second=0, minute=0, hour=0)
        return _day# - datetime.timedelta(days=_day.weekday())

    if groupper == "day":
        return media_datetime.replace(microsecond=0, second=0, minute=0, hour=0)

    if groupper == "hour":
        return media_datetime.replace(microsecond=0, second=0, minute=0)

    if groupper == "_minute":
        return media_datetime.replace(microsecond=0, second=0)

    raise ValueError(f"Unsupported groupper: {groupper}")


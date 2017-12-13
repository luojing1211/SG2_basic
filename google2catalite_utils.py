"""This is a utility functions file for google2sg2 script
"""
import numpy as np
from image_info_from_url import SG2ImageWebInfo
import sys

def parse_camera_info(camera_file_contents, image_id):
    """This is fast way to get camera informations from the camera_file.
    Parameter
    ---------
    camera_file_contents: list
        Camera file content list. All the content in the file.
    image_id: str
        Seaching image id.
    """
    infos = {}
    parsed = False
    ids = camera_file_contents[:, 2].astype(int)
    n_image_id = int(image_id)
    if n_image_id > ids[-1] or n_image_id < ids[0]:
        return parsed, infos
    target_idx = np.where(ids == n_image_id)[0]
    if len(target_idx) == 0:
        return parsed, infos
    #NOTE Each image should only have one unique line.
    target_line = camera_file_contents[target_idx][0]
    infos['date'] = target_line[3]
    infos['time'] = target_line[4]
    infos['focal_length'] = target_line[5]
    infos['camera'] = target_line[6]
    if len(target_line) > 7:
        extra_idx = len(target_line) - 7
        for ii in range(extra_idx):
            infos['camera'] += ' ' + target_line[ii + 7]
    parsed = True
    return parsed, infos

def split_lat_long(coords):
    """This function assumes lat and long are coming in pair and only one pair.
    """
    upper_coords = coords.upper().rstrip()
    if upper_coords.startswith("\xc2\xa0"):
        upper_coords = upper_coords.replace("\xc2\xa0", '')
    dir_index = np.array([0,0,0,0])
    directions = ['N', 'S', 'E', 'W']
    for ii, direction in enumerate(directions):
        dir_index[ii] = upper_coords.find(direction)
    mid_idx = np.argsort(dir_index)[len(dir_index)//2]
    mid_char = directions[mid_idx]
    coord1 = upper_coords[0:dir_index[mid_idx]+1]
    coord2 = upper_coords.split(mid_char)[-1]
    result = {}
    if mid_char in ['N', 'S']:
        result['lat'] = coord1.replace(' ', '')
        result['long'] = coord2.replace(' ', '')
    else:
        result['lat'] = coord2.replace(' ', '')
        result['long'] = coord1.replace(' ', '')
    return result

def coord_str2deg(coord):
    # assume there is only one coordinate char
    # NOTE this function assumes the lat and long are in the right format
    upper_coord = coord.upper().rstrip()
    upper_coord = upper_coord.lstrip()

    if upper_coord.endswith('N'):
        sign = 1
        direction = 'N'
    elif upper_coord.endswith('S'):
        sign = -1
        direction = 'S'
    elif upper_coord.endswith('W'):
        sign = -1
        direction = 'W'
    elif upper_coord.endswith('E'):
        sign = 1
        direction = 'E'
    else:
        pass

    coord_split = coord.split('\xc2\xb0')
    deg = float(coord_split[0])
    coord_split = coord_split[1].split("\'")
    minutes = float(coord_split[0])
    coord_split = coord_split[1].split("\"%s" % direction)
    seconds = float(coord_split[0])
    total_deg = (deg + minutes / 60.0 + seconds / 3600.0) * sign
    return total_deg

def translate_coords(coords):
    ll = split_lat_long(coords)
    LAT = ll['lat']
    LONG = ll['long']
    n_lat = coord_str2deg(LAT)
    n_long = coord_str2deg(LONG)
    return n_lat, n_long

def get_info_from_url(img_id):
    image = SG2ImageWebInfo(img_id)
    try:
        image.get_image_info()
    except:
        print sys.exc_info()
        raise RuntimeError('Image information is not correctly parsed from website.')
    try:
        image.translate_info_as_data()
    except:
        print sys.exc_info()
        raise RuntimeError('Image information is not correctly translated.')
    return image

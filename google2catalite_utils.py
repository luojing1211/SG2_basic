"""This is a utility functions file for google2sg2 script
"""
import numpy as np

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

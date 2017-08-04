"""
This is a script that transfer ARCC google doc to catalite style file.
Input:
google sheet csv file.
Output:
Jacobs catalite style file.
"""
import os
import google2catalite_utils as g2cu
import csv
import numpy as np

class SG2Image(object):
    """This is a class for sg2 image information.
    """
    def __init__(self, image_full_id=None):
        """
        Parameter
        ---------
        image_id: str
            The id of the image. ISS040-E-105041 style
        **infos: dict
            Input information.
        """
        if image_full_id != None:
            self.set_id(image_full_id)

    def set_id(self, image_full_id):
        self.image_full_id = image_full_id
        id_split = self.image_full_id.split('-')
        self.mission_id = id_split[0]
        self.separation_sign = id_split[1]
        self.image_id = id_split[2]

    def add_info(self, info):
        for key, v in list(info.items()):
            setattr(self, key, v)

    def get_camera_info(self, camera_file_contents=None, camera_dir=None):
        """
        This function is to parse the camera information from camera_directory
        """
        if camera_file_contents is None:
            if camera_dir is None:
                raise ValueError("One of another 'camera_file_contents' or"
                                 " 'camera_dir' should be given.")
            camera_file_path = os.path.join(camera_dir, self.mission_id)
            camera_file_name = self.mission_id + "camera.txt"
            camera_file = os.path.join(camera_file_path, camera_file_name)
            camera_file_contents = np.genfromtxt(camera_file, dtype='str')
        parsed, c_info = g2cu.parse_camera_info(camera_file_contents, \
                                                     self.image_id)
        if not parsed:
            raise ValueError("Can not fine image '%s' in the camera file." \
                             % self.image_full_id)
        for key, v in list(c_info.items()):
            setattr(self, key, v)

class GoogleSheetCSV(object):
    """This is a class for processing the Google Sheet CSV files
    """
    def __init__(self, csv_file):
        self.filename = csv_file
        self.read_csv_file(self.filename)
        self.content_list, self.name_field = self.read_csv_file(self.filename)
        self.image_ids = self.content_list[:, 1]
        self.missions, self.missions_list = self.get_missions(self.image_ids)

    def read_csv_file(self, csv_file):
        name_field = {}
        with open(csv_file, 'r') as f:
             reader = csv.reader(f)
             content_list = list(reader)
        for line in content_list:
            if line[0] == 'ID':
                for ii, l in enumerate(line):
                    if l == '':
                        continue
                    name_field[l] = ii
                break
        return np.array(content_list), name_field

    def get_missions(self, image_ids):
        missions_list = []
        for image_id in image_ids:
            try:
                image_id_fields = image_id.split('-')
                missions_list.append(image_id_fields[0])
            except:
                missions_list.append('')
        missions = set(missions_list)
        missions.remove('')
        missions.remove('Image ID')
        return missions, np.array(missions_list)

class CataliteFiles(object):
    """This is a class for catelite output file.
    """
    def __init__(self, filename, google_sheet_cls, catelite_path='.'):
        self.filename = filename
        self.sheet_cls = google_sheet_cls
        self.catelite_path = catelite_path
        self.image_clses = self.get_images(self.sheet_cls, self.catelite_path)

    def get_images(self, sheet_cls, catelite_path):
        images_clses = []
        for img_id in sheet_cls.content_list[:, 1]:
            try:
                images_clses.append(SG2Image(img_id))
            except:
                if img_id != "" and img_id != 'Image ID':
                    print("Image ID '%s' is not in the right format." % img_id)
                images_clses.append(SG2Image())
                continue
        for mission in sheet_cls.missions:
            msk = np.where(sheet_cls.missions_list == mission)[0]
            camera_dir = os.path.join(catelite_path, 'camera')
            camera_file_path = os.path.join(camera_dir, mission)
            camera_file_name = mission + "camera.txt"
            camera_file = os.path.join(camera_file_path, camera_file_name)
            camera_file_contents = np.genfromtxt(camera_file, dtype='str')
            print i
            for idx in msk:
                images_clses[idx].get_camera_info(camera_file_contents)
                # TODO Get input information. 
        return images_clses

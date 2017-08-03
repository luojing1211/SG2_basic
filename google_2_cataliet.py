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
    def __init__(self, image_full_id, **infos):
        """
        Parameter
        ---------
        image_id: str
            The id of the image. ISS040-E-105041 style
        **infos: dict
            Input information.
        """
        self.image_full_id = image_full_id
        self.input_info = infos
        id_split = self.image_full_id.split('-')
        self.mission_id = id_split[0]
        self.separation_sign = id_split[1]
        self.image_id = id_split[2]
        for key, v in list(self.input_info.items()):
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
        
    def read_csv_file(self, csv_file):
        name_field = []
        with open(csv_file, 'r') as f:
             reader = csv.reader(f)
             content_list = list(reader)
        for line in content_list:
            if line[0] == 'ID':
                for l in line:
                    name_field.append(l)
                break
        return np.array(content_list), name_field

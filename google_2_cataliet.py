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
        self.good_image = False
        if image_full_id != None:
            try:
                self.set_id(image_full_id)
                self.web_info = self.get_web_info()
                self.nadir_point = self.get_nadir_point()
                self.sun_azimuth = self.web_info.sun_azimuth
                self.sun_elevation = self.web_info.sun_elevation
                self.spacecraft_alt_mile = self.web_info.spacecraft_alt_mile
                self.good_image = True
            except:
                pass

    def set_id(self, image_full_id):
        self.image_full_id = image_full_id
        id_split = self.image_full_id.split('-')
        self.mission_id = id_split[0]
        self.separation_sign = id_split[1]
        self.image_id = id_split[2]

    def add_info(self, info):
        for key, v in list(info.items()):
            if key == "center_point":
                v = g2cu.translate_coords(v)
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
    def get_web_info(self):
        im_info = g2cu.get_info_from_url(self.image_full_id)
        return im_info

    def get_nadir_point(self):
        # TODO Duplicate code.
        nd = self.web_info.nadir
        final_nd = np.zeros(2)
        for ii, coord in enumerate(nd):
            upper_coord = coord.upper().rstrip()
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

            deg = coord.split(' ')[0]
            final_deg = float(deg) * sign
            final_nd[ii] = final_deg
        return final_nd

class GoogleSheetCSV(object):
    """This is a class for processing the Google Sheet CSV files
    """
    def __init__(self, csv_file):
        self.filename = csv_file
        self.read_csv_file(self.filename)
        self.content_list, self.name_field = self.read_csv_file(self.filename)
        self.image_ids = self.content_list[:, 1]
        self.missions, self.missions_list = self.get_missions(self.image_ids)
        self.name_field_map = {'center_point': 'Center Point',
                               'features': 'Features',
                               'geographic_name':'Geographic Name',
                               'cloud_percentage': 'Cloud Percentage',
                               'ho_lo': 'HO / LO'}
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

    def get_column_idx(self, field_name):
        if field_name not in list(self.name_field.keys()):
            fn = self.name_field_map[field_name]
            return self.name_field[fn]
        else:
            return self.name_field[field_name]

class CataliteFiles(object):
    """This is a class for catelite output file.
    """
    def __init__(self, filename, google_sheet_cls, catelite_path='.'):
        self.filename = filename
        self.sheet_cls = google_sheet_cls
        self.catelite_path = catelite_path
        self.required_info = ['mission_id', 'separation_sign', 'image_id', \
                              'date', 'time', 'nadir_point', 'center_point', \
                              'features', 'geographic_name', 'cloud_percentage',\
                              'focal_length']
        self.from_input = ['center_point', 'features', 'geographic_name', \
                           'cloud_percentage', 'ho_lo']
        self.image_clses = self.get_images(self.sheet_cls, self.catelite_path)
        self.geo_names = self.load_geo_names(self.catelite_path)
        self.geo_coords = None
        self.catalite_params = self.load_catalite_parameters(self.catelite_path)

    def load_geo_names(self, catelite_path):
        f = open(os.path.join(catelite_path, 'GeoNames.txt'))
        geo_name = []
        for l in f.readlines():
            geo_name.append(l.strip())
        f.close()
        return geo_name

    def load_geo_coords(self, catelite_path):
        geo_coor = np.genfromtxt(os.path.join(catelite_path, 'GeonCoords.tsv'), \
                                 dtype=str)
        self.geo_coords = geo_coor

    def load_catalite_parameters(self, catelite_path):
        f = open(os.path.join(catelite_path, 'CatalogParameters.txt'))
        cp = {}
        for l in f.readlines():
            if l.startswith('#') or l=="":
                continue
            l = l.strip()
            lf = l.split(':')
            if len(lf) == 1:
                lf = lf[0].split("=")
                if lf[0] == "":
                    continue
            cp[lf[0]] = lf[1]
        f.close()
        return cp

    def get_rules(self, rule_name):
        rule = self.catalite_params[rule_name]
        l = rule.split('|')
        if len(l) < 2:
            l = l[0]
        return l

    def get_geoname_from_geocoord(self, Lat, Long, tol=0.5):
        if self.geo_coords is None:
            print("Loading geographic coordinates. It may take a minute.")
            self.load_geo_coords(self.catelite_path)
        lats = self.geo_coords[:,0].astype(float)
        longs = self.geo_coords[:,1].astype(float)
        lat_diff = np.abs(lats-Lat)
        lat_diff_min = lat_diff.min()
        lat_idx = np.where(lat_diff == lat_diff_min)[0]
        # search closest long within cloest lat idxs.
        long_diff = np.abs(longs[lat_idx]-Long)
        long_diff_min = long_diff.min()
        long_idx = np.where(long_diff == long_diff_min)[0]
        if lat_diff_min > tol or long_diff_min > tol:
            raise ValueError("Can not map Lat %.2f Long %.2f " % (Lat, Long) )
        result_idx = lat_idx[long_idx]
        return self.geo_coords[result_idx,2][0]

    def get_images(self, sheet_cls, catelite_path):
        images_clses = []
        for img_id in sheet_cls.content_list[:, 1]:
            img = SG2Image(img_id)
            if not img.good_image:
                if img_id != "" and img_id != 'Image ID':
                    print("Can not form image for '%s'. Need to "
                          "checkout the ID format or net connection. " % img_id)
            images_clses.append(img)

        for mission in sheet_cls.missions:
            msk = np.where(sheet_cls.missions_list == mission)[0]
            camera_dir = os.path.join(catelite_path, 'camera')
            camera_file_path = os.path.join(camera_dir, mission)
            camera_file_name = mission + "camera.txt"
            camera_file = os.path.join(camera_file_path, camera_file_name)
            camera_file_contents = np.genfromtxt(camera_file, dtype='str')
            for idx in msk:
                images_clses[idx].get_camera_info(camera_file_contents)
                input_info = {}
                for name in self.from_input:
                    col_idx = sheet_cls.get_column_idx(name)
                    input_info[name] = sheet_cls.content_list[idx, col_idx]
                images_clses[idx].add_info(input_info)
        return images_clses

    def output_line(self, img_cls):
        outline = ""
        # ids
        outline += img_cls.mission_id + '\t'
        outline += img_cls.separation_sign + '\t'
        outline += img_cls.image_id + '\t\t'
        # date and time
        date = img_cls.date.replace(':', '\t')
        outline += date + '\t'
        time = img_cls.time.replace(':', '\t')
        outline += time + '\t'
        # Nadir Point
        nadir = img_cls.nadir_point
        outline += "%.2f" % nadir[0] + '\t' + "%.2f" % nadir[1] + '\t'
        # center_point
        center_point = img_cls.center_point
        outline += "%.2f" % center_point[0] + '\t' + "%.2f" % center_point[1] + '\t'
        # geographic_name
        geo_name = img_cls.geographic_name.replace(" ", '')
        if geo_name.upper() in self.geo_names:
            outline += geo_name.upper() + "\t"
        else:
            print("Can not find Geographic name '%s' in the list." % geo_name)
            print("Search Geographic name using center_point")
            geo_name = self.get_geoname_from_geocoord(img_cls.center_point[0], \
                                                      img_cls.center_point[1])
            outline += geo_name + "\t"
        #features
        features = img_cls.features
        if features is '':
            outline += 'NOT SPECIFIED\t'
        else:
            outline += features.upper() + '\t'
        #Cloud Percentage
        cp = img_cls.cloud_percentage.replace('%', '')
        outline += cp + '\t'
        # focal_length
        fl = img_cls.focal_length
        outline += fl + '\t'
        # Ho/Lo
        holo = img_cls.ho_lo
        outline += holo + '\t'
        #Camera
        camera = ""
        film_type = ""
        camera_rule = self.get_rules('CameraAndFilmRules')
        for cr in camera_rule:
            crf = cr.split(',')
            if crf[0] in img_cls.camera:
                camera = crf[1]
                film_type = crf[2]
                break
            else:
                continue
        if camera == "" or film_type == "":
            raise ValueError("Can not match camera '%s'." % img_cls.camera)
        outline += camera + '\t' + film_type + '\t'
        # TODO Need azimuth, Evelation, altitude look direction

        Azimuth = img_cls.sun_azimuth
        Elevation = img_cls.sun_elevation
        Altitude = img_cls.spacecraft_alt_mile
        outline += "%d\t%d\t%d\t" % (Azimuth, Elevation, Altitude)
        # Look direction
        diff = nadir - center_point
        if diff[0] < 0.0:
            dir_NS = 'N'
        else:
            dir_NS = 'S'

        if diff[1] < 0.0:
            dir_EW = 'E'
        else:
            dir_EW = 'W'
        # TODO Add direction check
        direction = dir_NS + dir_EW
        outline += direction
        return outline

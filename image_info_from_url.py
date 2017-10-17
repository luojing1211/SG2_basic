# This is a simple file that help sg2 to get images and class the images for
# NASA Astronaut photoes.
# Author : Jing, Aldo, and sg2 members
import urllib2
import os
import re
import time
from datetime import datetime

urlbase = 'http://eol.jsc.nasa.gov/DatabaseImages/ESC'
infopage = 'http://eol.jsc.nasa.gov/SearchPhotos/photo.pl?'
class SG2ImageWebInfo(object):
    """This is a class for astronaut image information.
    """
    def __init__(self,image_id,mission = None, parse_info=False):
        self.image_id = image_id
        if mission is None:
            self.mission = self.get_mission(self.image_id)
        else:
            self.mission = mission
        self.image_url = self.get_url()
        self.image_url_large = self.get_url(large=True)
        self.page_url = self.get_page_url()
        self.image_info_pattern = {'Spacecraft nadir point':
            re.compile(r'Spacecraft nadir point:</b></em> \d+.+\d+&deg;+ [A-Z]+'),
                                   'Photo center point':
            re.compile(r'Photo center point:</b></em> \d+.+\d+&deg;+ [A-Z]+'),
                                   'Spacecraft Altitude':
            re.compile(r'\d+ +nautical miles'),
                           'Focal Length':
            re.compile(r'\d+mm'),
                           'Date taken':
            re.compile(r'\d+.+\d+.+\d'),
                           'Time taken':
            re.compile(r'\d+:+\d+:+\d+ +GMT'),
                           'Sun Elevation':
            re.compile(r'Sun Elevation Angle:</b></em></div></td> <td>+\d+&deg'),
                           'Sun Azimuth':
            re.compile(r'Sun Azimuth:</b></em></div></td> <td>+\d+&deg;')}
        self.image_info = {'Spacecraft nadir point': '',
                           'Photo center point': '',
                           'Spacecraft Altitude': '',
                           'Focal Length': '',
                           'Date taken': '',
                           'Time taken': '',
                           'Sun Elevation':'',
                           'Sun Azimuth':''}

        self.img_category = None
        if parse_info:
            self.get_image_info()
        self.info_list = ['nadir', 'photo_center', 'focal_length',
                          'time_taken', 'img_category', 'spacecraft_alt']

    def get_mission(self, image_id):
        """Get astronaut photo taken mission for image id
        """
        image_id_field = image_id.split('-')
        return image_id_field[0]

    def get_url(self, large=False):
        """This is a function that get image url from data website.
        Parameter
        ----------
        large : bool, optional, default is False
            A flag to select the large image or not.
        return
        ----------
        url of the image in the data website.
        """
        if large:
            size = '/large/'
        else:
            size = '/small/'

        url = urlbase + size + self.mission + '/' + self.image_id + '.JPG'
        return url

    def get_page_url(self):
        """This is a function that get image information page url.
        """
        mission_part = 'mission=' + self.mission
        id_num = self.image_id.split('-')[2]
        id_part = 'roll=E&frame=' + id_num
        page_url = infopage + mission_part + '&' + id_part
        return page_url

    def get_image_info(self):
        """Get the image information from the webpage"""
        page = urllib2.urlopen(self.page_url, timeout=1)
        htmlstr = page.read()
        if 'removed' in htmlstr:
            raise ValueError('The Page URL for image ' + self.image_id +
                             ' is invalid.')
        for keywords in self.image_info.keys():
            startIndex =  htmlstr.find(keywords)
            if startIndex == -1:
                raise RuntimeError('Can not find string ' + keywords + ' in '
                                    'the webpage.')
            search_length = 100
            pattern = self.image_info_pattern[keywords]
            search_str = htmlstr[startIndex - search_length :startIndex + search_length]
            match = re.findall(pattern, search_str)
            if match != []:
                if '</b></em>' in match[0]:
                    result = match[0].split('</em>')[1]
                else:
                    result = match[0]
                self.image_info[keywords] = result

    def translate_info_as_data(self):
        """This function takes image_info attrbution and set attrbutions to the
        right format
        """
        # get focus lenght in unit of mm
        setattr(self,'focal_length', float(self.image_info['Focal Length'][:-2]))
        # get Altitude in unit of km
        alt_str = self.image_info['Spacecraft Altitude']
        alt_str = alt_str.split()
        alt_nautical_mile = float(alt_str[0])
        alt_km = alt_nautical_mile*1.852
        setattr(self, 'spacecraft_alt', alt_km)
        setattr(self, 'spacecraft_alt_mile', alt_nautical_mile)
        # get data and time
        date_str = self.image_info['Date taken']
        time_str = self.image_info['Time taken']
        date_str = date_str.split('.')
        time_str = time_str.split(':')
        date = [int(x) for x in date_str]
        time = [int(x) for x in time_str[0:2]]
        time.append(int(time_str[2][0:2]))
        setattr(self, 'time_taken', datetime(date[0], date[1], date[2],
                                             time[0], time[1], time[2]))
        # Process nadir and center point
        ndstr = self.image_info['Spacecraft nadir point']
        ctstr = self.image_info['Photo center point']
        sun_elev = self.image_info['Sun Elevation']
        sun_az = self.image_info['Sun Azimuth']
        if ndstr != '':
            ndstr = ndstr.split(',')
            latstr = self.process_latlon_str(ndstr[0])
            lonstr = self.process_latlon_str(ndstr[1])
            setattr(self, 'nadir', [latstr,lonstr])
        else:
            setattr(self, 'nadir', [])

        if ctstr != '':
            ctstr = ctstr.split(',')
            latstr = self.process_latlon_str(ctstr[0])
            lonstr = self.process_latlon_str(ctstr[1])
            setattr(self, 'photo_center', [latstr,lonstr])
        else:
            setattr(self, 'photo_center', [])

        num = re.compile(r'\d+')
        if sun_elev != '':
            match = re.findall(num, sun_elev)
            if match == []:
                sun_elevation = None
            else:
                sun_elevation = float(match[0])
            setattr(self, 'sun_elevation', sun_elevation)

        if sun_az != '':
            match = re.findall(num, sun_az)
            if match == []:
                sun_azimuth= None
            else:
                sun_azimuth = float(match[0])
            setattr(self, 'sun_azimuth', sun_azimuth)

    def process_latlon_str(self,lstr):
        """get latitude and longitude from image string
        """
        ldata = lstr.replace('&deg;', '')
        return ldata.lstrip()

    # This secret discovered by Aldo
    def download_image(self, download_path=None):
        """Save the image from url.
        Parameter
        ----------
        download_path : str
            the path to you download directory
        """
        if download_path is None:
            outfilename = self.image_id+'.jpg'
        else:
            outfilename = os.path.join(download_path,self.image_id + '.jpg')
        image = urllib.urlopen(self.image_url)
        data = image.read()
        if 'removed' in data:
            raise ValueError('The URL for image ' + self.image_id +
                             ' is invalid.')

        output = open(outfilename,"wb")
        output.write(data)
        output.close()


if __name__ == "__main__":
    pass

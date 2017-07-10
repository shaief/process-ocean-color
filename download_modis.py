#!/usr/bin/env python3
import os
from datetime import datetime, date, time
import re

import requests

def download_files(start_date, number_of_days, lon, lat, target_directory):
    target = '%s{}' % target_directory
    start_datetime = datetime.combine(start_date, time.min)
    first_day = int(start_datetime.timestamp() / 86400)  # days since epoch

    BASE_URL = 'https://oceancolor.gsfc.nasa.gov/cgi/browse.pl'
    GET_FILE_URL = 'https://oceandata.sci.gsfc.nasa.gov/cgi/getfile/'
    url = BASE_URL + '?sub=level1or2list&sen=am&per=DAY&dnm=D&day={}&n={}&s={}&w={}&e={}'

    for d in range(first_day, first_day + number_of_days):
        _url = url.format(d, lat[1], lat[0], lon[0], lon[1])
        _data = requests.get(_url)
        if _data:
            content = _data.content
            all_a = re.findall(r'(?<=<a href=")[^"]*', str(content))
            for a in all_a:
                if 'filenamelist' in a and 'CHL' in a:
                    data_url = '{}?{}'.format(BASE_URL, a.split('?')[1])
                    print(data_url)
                    url_data_file = requests.get(data_url).content
                    for line in url_data_file.split(b'\n'):
                        line = line.decode('UTF-8')
                        if 'OC' in line:
                            nc_file = GET_FILE_URL + line
                            print(GET_FILE_URL + line)
                            try:
                                response = requests.get(nc_file, timeout=(3, 60))
                                with open(target.format(line), 'wb') as f:
                                    f.write(response.content)
                                print('downloaded file {}'.format(line))
                            except Exception as e:
                                print('Failed to download file due to: {}'.format(e))


if __name__ == '__main__':
    start_date = date(2016, 5, 1)

    number_of_days = 45
    lon = (30, 36)
    lat = (30, 38)

    target = '/home/shaief/Thesis/Data/MODIS/test_script/{}'

    download_files(start_date, number_of_days, lon, lat, target_directory)

#!/usr/bin/env python3
import os
import pathlib
from datetime import datetime, date, time
import re

import requests

def download_files(start_date, number_of_days, lon, lat, target_directory):
    print('Downloading files...')
    if not os.path.exists(f'{target_directory}/originals'):
        os.makedirs(f'{target_directory}/originals')
    target = '%s/originals/{}' % target_directory
    pathlib.Path(target_directory).mkdir(parents=True, exist_ok=True)
    start_datetime = datetime.combine(start_date, time.min)
    first_day = int(start_datetime.timestamp() / 86400)  # days since epoch

    BASE_URL = 'https://oceancolor.gsfc.nasa.gov/cgi/browse.pl'
    GET_FILE_URL = 'https://oceandata.sci.gsfc.nasa.gov/cgi/getfile/'
    url = BASE_URL + '?sub=level1or2list&sen=am&per=DAY&day={}&prm=CHL&n={}&s={}&w={}&e={}'

    for d in range(first_day, first_day + number_of_days):
        _url = url.format(d, lat[1], lat[0], lon[0], lon[1])
        _data = requests.get(_url)
        if _data:
            content = _data.content
            all_a_href = re.findall(r'(?<=<a href=")[^"]*', str(content))
            for a_href in all_a_href:
                # if 'getfile' in a_href and any((True for x in ['OC', 'SST'] if x in a_href)):
                if 'file' in a_href:
                    try:
                        response = requests.get(BASE_URL + a_href, timeout=(3, 60))
                        for link in re.findall(r'(?<=<a href=")[^"]*', str(response.content)):
                            if 'LAC_OC.nc' in link:
                                filename = link.split('/')[-1]
                                r = requests.get(link)
                                if not os.path.exists(target.format(filename)):
                                    with open(target.format(filename), 'wb') as f:
                                        f.write(r.content)
                                    print('downloaded file {}'.format(filename))
                    except Exception as e:
                        print('Failed to download file due to: {}'.format(e))
    print('Done downloading files...')

if __name__ == '__main__':
    start_date = date(2016, 5, 1)

    number_of_days = 5
    lon = (30, 36)
    lat = (30, 38)

    target = '/home/shaief/Thesis/Data/MODIS/test_script/{}'

    download_files(start_date, number_of_days, lon, lat, target_directory)

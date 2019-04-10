#!/usr/bin/env python3
import os
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, date, time
import re

import requests
from tqdm import tqdm

import colors

BASE_URL = 'https://oceancolor.gsfc.nasa.gov/cgi/browse.pl'
GET_FILE_URL = 'https://oceandata.sci.gsfc.nasa.gov/cgi/getfile/'
url = BASE_URL + '?sub=level1or2list&sen=am&per=DAY&day={}&prm=CHL&n={}&s={}&w={}&e={}'


def download_file(d, lat, lon, target):
    _url = url.format(d, lat[1], lat[0], lon[0], lon[1])
    success = ''
    error = ''
    try:
        _data = requests.get(_url, timeout=3)
    except requests.exceptions.Timeout as e:
        error = f'{colors.YELLOW}Download from {_url} timedout{colors.END}'
        _data = None
    except Exception as e:
        error = f'{colors.BOLD}{colors.RED}Failed to download from {_url} due to: {e}{colors.END}'
        _data = None
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
                                success = f'downloaded file {filename}'
                except requests.exceptions.Timeout as e:
                    error = f'{colors.YELLOW}Download from {BASE_URL + a_href} timedout{colors.END}'
                except Exception as e:
                    error = f'{colors.BOLD}{colors.RED}Failed to download {BASE_URL + a_href} due to: {e}{colors.END}'

    return error, success


def download_files(start_date, number_of_days, lon, lat, target_directory):
    print('Downloading files...')
    errors = []
    successes = []
    if not os.path.exists(f'{target_directory}/originals'):
        os.makedirs(f'{target_directory}/originals')
    target = '%s/originals/{}' % target_directory
    pathlib.Path(target_directory).mkdir(parents=True, exist_ok=True)
    start_datetime = datetime.combine(start_date, time.min)
    first_day = int(start_datetime.timestamp() / 86400)  # days since epoch

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_list = []
        for d in range(first_day, first_day + number_of_days):
            future_list += [
                executor.submit(
                    download_file, d, lat, lon, target
                )
            ]
        for future_object in tqdm(as_completed(future_list), total=len(future_list)):
            error, success = future_object.result()
            if error:
                errors.append(error)
            if success:
                successes.append(success)
    for error in errors:
        print(error)
    for success in successes:
        print(success)
    print('Done downloading files...')

if __name__ == '__main__':
    start_date = date(2016, 5, 1)

    number_of_days = 5
    lon = (30, 36)
    lat = (30, 38)

    target = '/home/shaief/Thesis/Data/MODIS/test_script/{}'

    download_files(start_date, number_of_days, lon, lat, target_directory)

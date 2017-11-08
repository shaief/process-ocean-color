import glob
import os
import stat
import subprocess
from datetime import date
from download_modis import download_files
import templates

HOME_DIRECTORY = os.path.expanduser('~')
SEADAS_PATH = "ocssw"

BASE_DIRECTORY = 'Thesis/Data/MODIS'
target_directory = 'project_directory'

DOWNLOAD = True
CONVERT_TO_NetCDF4 = False  # True
start_date = date(2016, 5, 1)
end_date = date(2016, 5, 10)
lon = (30, 36)
lat = (30, 38)

target_directory = os.path.join(HOME_DIRECTORY,BASE_DIRECTORY, target_directory, '')
if not os.path.exists(target_directory):
    os.makedirs(target_directory)

SEADAS_PATH = os.path.join(HOME_DIRECTORY, SEADAS_PATH)
print('Files will be saved at: {}'.format(target_directory))
number_of_days = (end_date - start_date).days
west, east = lon
south, north = lat

day_of_year = start_date.timetuple().tm_yday
days_in_year = ' '.join([str(
    d) for d in range(day_of_year, day_of_year + number_of_days)])

arguments = {
    'batchl2bin': {'SEADAS_PATH': SEADAS_PATH,
                   'directory': target_directory},
    'batchl3bin': {'SEADAS_PATH': SEADAS_PATH,
                   'directory': target_directory,
                   'west': west,
                   'south': south,
                   'east': east,
                   'north': north,
                   'days_in_year': days_in_year,
                   'year': start_date.year},
    'batchl3mapgen': {'SEADAS_PATH': SEADAS_PATH,
                      'directory': target_directory,
                      'west': west,
                      'south': south,
                      'east': east,
                      'north': north},
    'batchSmigen': {'SEADAS_PATH': SEADAS_PATH,
                    'directory': target_directory,
                    'west': west,
                    'south': south,
                    'east': east,
                    'north': north},
}


def create_file(filename):
    print(filename)
    template = getattr(templates, filename)
    target_file = os.path.join(target_directory, '{}.bsh'.format(filename))
    with open(target_file, 'w') as f:
        f.write(template.format(**arguments[filename]))
    st = os.stat(target_file)
    os.chmod(target_file, st.st_mode | stat.S_IEXEC)

if DOWNLOAD:
    download_files(start_date, number_of_days, lon, lat, target_directory)

for filename in ['batchl2bin', 'batchl3bin', 'batchl3mapgen']:
    create_file(filename)
    cmd = os.path.join(target_directory, './{}.bsh'.format(filename))
    subprocess.call(cmd, shell=True)

if CONVERT_TO_NetCDF4:
    from hdf5_to_netcdf import convert_hdf5_to_netcdf4
    os.chdir('{}/OC_maps'.format(target_directory))
    for filename in glob.glob("*.hdf"):
        print(filename)
        filename, file_extension = os.path.splitext(filename)
        hdf_file = filename + '.hdf'
        netcdf_file = filename + '.nc'
        convert_hdf5_to_netcdf4(hdf_file, netcdf_file)

    os.chdir('../../')

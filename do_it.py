import os
import stat
import subprocess
from datetime import date
from download_modis import download_files
import templates


HOME_DIRECTORY = os.path.expanduser('~')
BASE_DIRECTORY = 'Thesis/Data/MODIS'
target_directory = 'project_directory'

target_directory = os.path.join(HOME_DIRECTORY,BASE_DIRECTORY, target_directory, '')

CONVERT_TO_NetCDF4 = True
start_date = date(2016, 5, 1)
end_date = date(2016, 5, 31)
lon = (30, 36)
lat = (30, 38)

number_of_days = (end_date - start_date).days
west, east = lon
south, north = lat

day_of_year = start_date.timetuple().tm_yday
days_in_year = ' '.join([str(
    d) for d in range(day_of_year, day_of_year + number_of_days)])

arguments = {
    'batchl2bin': {'directory': target_directory},
    'batchl3bin': {'directory': target_directory,
                   'west': west,
                   'south': south,
                   'east': east,
                   'north': north,
                   'days_in_year': days_in_year,
                   'year': start_date.year},
    'batchl3mapgen': {'directory': target_directory,
                    'west': west,
                    'south': south,
                    'east': east,
                    'north': north},
    'batchSmigen': {'directory': target_directory,
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

download_files(start_date, number_of_days, lon, lat, target_directory)

for filename in ['batchl2bin', 'batchl3bin', 'batchSmigen']:
    create_file(filename)
    cmd = os.path.join(target_directory, './{}.bsh'.format(filename))
    # subprocess.Popen(cmd,
    #                  shell=True,
    #                  stdout=subprocess.PIPE,
    #                  stderr=subprocess.PIPE)
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

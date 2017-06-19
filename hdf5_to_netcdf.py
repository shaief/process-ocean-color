import glob, os

import xarray as xr


def convert_hdf5_to_netcdf4(input_file, output_file):
    ds = xr.open_dataset(input_file)
    chl = ds['chlor_a'].to_dataset()
    chl.to_netcdf(output_file, format='NETCDF4_CLASSIC')


if __name__ == '__main__':
    os.chdir('OC_maps')
    for filename in glob.glob("*.hdf"):
        print(filename)
        filename, file_extension = os.path.splitext(filename)
        hdf_file = filename + '.hdf'
        netcdf_file = filename + '.nc'
        convert_hdf5_to_netcdf4(hdf_file, netcdf_file)

    os.chdir('../../')

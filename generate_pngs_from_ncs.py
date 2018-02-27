from glob import glob
import os

import xarray as xr
import numpy as np
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
from matplotlib.ticker import LogFormatter
from mpl_toolkits.basemap import Basemap


def create_pngs(target_directory, param='chlor_a'):
    cwd = os.getcwd()
    os.chdir(os.path.join(target_directory, 'OC_maps'))
    all_hdf_files = sorted(glob('*.nc'))

    try:
        for i, f in enumerate(all_hdf_files):
            try:
                dataset = xr.open_dataset(f)
                maxvalue = np.nanmax(dataset.chlor_a.data)
                minvalue = np.nanmin(dataset.chlor_a.data)
                sst_array = np.ma.masked_where(
                    np.isnan(dataset.chlor_a.data), dataset.chlor_a.data)
                lon = {
                    'min': dataset.geospatial_lon_min,
                    'max': dataset.geospatial_lon_max,
                    'dims': dataset.dims['lon'],
                }
                lat = {
                    'min': dataset.geospatial_lat_min,
                    'max': dataset.geospatial_lat_max,
                    'dims': dataset.dims['lat'],
                }

                fig = plt.figure()
                lonv = np.linspace(lon['min'], lon['max'], lon['dims'])
                latv = np.linspace(lat['max'], lat['min'], lat['dims'])
                lons, lats = np.meshgrid(lonv, latv)

                map = Basemap(
                    llcrnrlon=lon['min'],
                    llcrnrlat=lat['min'],
                    urcrnrlon=lon['max'],
                    urcrnrlat=lat['max'],
                    resolution='i',
                    projection='merc')
                map.drawcoastlines()
                map.drawcountries()
                if param == 'sst':
                    ax = map.pcolormesh(
                        lons,
                        lats,
                        sst_array,
                        vmin=minvalue,
                        vmax=maxvalue,
                        latlon=True, )
                    map.colorbar(
                        ax,
                        location="right",
                        size="5%",
                        pad='2%',
                        label='SST [°C]')
                elif param == 'chlor_a':
                    ax = map.pcolormesh(
                        lons,
                        lats,
                        sst_array,
                        norm=LogNorm(),
                        vmin=0.001,
                        vmax=0.63,
                        latlon=True, )
                    formatter = LogFormatter(10, labelOnlyBase=True)
                    map.colorbar(
                        ax,
                        location="right",
                        size="5%",
                        pad='2%',
                        label='CHL [mg/m3]',
                        ticks=[0.02, 0.1, 0.25, 0.4, 0.63],
                        format=formatter)
                print(f,
                      dataset.time_coverage_start.split('T')[0],
                      dataset.time_coverage_end.split('T')[0],
                      dataset.time_coverage_start.split('T')[0] ==
                      dataset.time_coverage_end.split('T')[0])
                plot_date = dataset.time_coverage_end.split('T')[0]
                plt.title(f"MODIS Aqua - {param.upper()} - {plot_date}")
                plt.savefig(
                    dataset.product_name.replace('.nc', '.png'),
                    bbox_inches='tight')
                plt.close(fig)
            except Exception as e:
                print(f'Could not plot {f} due to {e}')

    finally:
        os.chdir(cwd)

import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def calc_stats_master():

    df = pd.DataFrame()
    files = [
        (f'{root}/data/global_atlas/wind/USA_wind-speed_{str(s)}m.tif', int(s)) for s in [50, 100, 150]
    ]

    for f,h in files:
        print(h)
        temp = calc_stats(f,h)
        temp = clean(temp, h)

        df = df.append(temp)

    # output
    with open(f'{root}intermediates/global_atlas/wind.pkl', 'wb') as f:
        pickle.dump(df, f)
    df.to_csv(f'{root}intermediates/global_atlas/wind.csv', index=False)

    return None
def calc_stats(file, speed):

    # read the gdf
    with open(f'{root}intermediates/counties/county_panel_geo.pkl', 'rb') as f:
        counties = pickle.load(f)

    # select only one year (NOTE WE ASSUME THE COUNTY BOUNDARIES DID NOT CHANGE)
    counties = counties.drop_duplicates(['fips']).reset_index(drop=True)

    # read the raster
    data = rasterio.open(file)
    affine = data.transform
    array = data.read(1)
    stats = pd.DataFrame(rasterstats.zonal_stats(counties, array, affine=affine))

    # convert to data frame format
    # attach stats to counties

    gdf = pd.concat([counties, stats], axis=1)
    df = pd.DataFrame(gdf)

    # check if there are any NAs
    (df['count'] == 0).sum()

    # basically, Puerto Rico is not in here
    print(df[(df['count'] == 0)]['state'].value_counts())

    return df

def clean(df, height):

    # create county fips code
    #df['fips'] = df['STATE'] + df['COUNTY']

    # select the columns
    df = df[['fips','count','min','mean','max']]

    # create speed column
    df['height'] = height

    return df



def main():

    calc_stats_master()

if __name__ == '__main__':
    main()
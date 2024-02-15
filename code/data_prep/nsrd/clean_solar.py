import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def sample_points(polygon, n, seed=42):

    '''

    sample n points within a polygon

    '''

    # set the seed
    random.seed(seed)

    min_x, min_y, max_x, max_y = polygon.bounds
    points = []
    while len(points) < n:
        random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if (random_point.within(polygon)):
            points.append(random_point)

    return points


def sample_long_lat():

    '''
    sample points within each county
    '''

    # read the gdf
    with open(f'{root}intermediates/counties/county_panel_geo.pkl', 'rb') as f:
        counties = pickle.load(f)

    # select only one year (NOTE WE ASSUME THE COUNTY BOUNDARIES DID NOT CHANGE)
    counties = counties.drop_duplicates(['fips']).reset_index(drop=True)

    all_samples = {}

    for idx, row in counties.iterrows():

        name = row['fips']
        polygon = row['geometry']
        points = sample_points(polygon, 20)
        all_samples[name] = points

    # save the sampled points
    with open(f'{root}intermediates/solar/sampled_points.pkl', 'wb') as f:
        pickle.dump(all_samples, f)

    return all_samples


def master():

    # read in the sampled points
    with open(f'{root}intermediates/solar/sampled_points.pkl', 'rb') as f:
        points = pickle.load(f)

    # I need to change this so it keeps track of the counties!!
    # flatten points
    all_points = [point for points_list in points.values() for point in points_list]
    # also get the keys corresponding to the points
    all_keys = [key for key in points.keys() for i in range(len(points[key]))]

    transformer = Transformer.from_crs("EPSG:4269", "EPSG:4326")
    all_points = [transformer.transform(p.x, p.y) for p in all_points]

    # df to store results
    df = pd.DataFrame()

    # loop through all points
    i = 0
    for longitude, latitude in all_points:

        try:
            df_tmy, location = fetch_data(latitude, longitude)

            result_fixed = calc_irr('fixed', df_tmy, location)
            result_tilt = calc_irr('tracking', df_tmy, location)

            df = df.append({'county':all_keys[i],
                            'lat':latitude,
                            'lon':longitude,
                            'tilt_irr':result_tilt,
                            'fixed_irr':result_fixed},
                           ignore_index=True)

        except:
            df = df.append({'county':all_keys[i],
                            'lat':latitude,
                            'lon':longitude,
                            'tilt_irr':9999,
                            'fixed_irr':9999},
                           ignore_index=True)

        i = i+1

        # if i is multiple of 100, save the data
        if i % 100 == 0:
            df.to_csv(f'{root}intermediates/solar/solar_irr.csv', index=False)

    return df

# #####################
# Solar Calculations
# https://pvsc-python-tutorials.github.io/PVSC48-Python-Tutorial/Tutorial%202%20-%20POA%20Irradiance.html#:~:text=A
# %20fixed%20array%20has%20fixed,best%20match%20the%20sun%27s%20position.
# #####################

def fetch_data(latitude, longitude):

    # get df with the solar data

    data = pvlib.iotools.get_pvgis_tmy(latitude, longitude)
    metadata = data[2]
    df_tmy = data[0]

    df_tmy = df_tmy.rename(columns={'ghi': 'GHI','dni': 'DNI','dhi': 'DHI'})
    location = pvlib.location.Location(latitude=metadata['location']['latitude'],
                                       longitude=metadata['location']['longitude'])

    return df_tmy, location


def calc_irr(type, df_tmy, location):


    times = df_tmy.index - pd.Timedelta('30min')
    solar_position = location.get_solarposition(times)
    # but remember to shift the index back to line up with the TMY data:
    solar_position.index += pd.Timedelta('30min')

    if type == 'fixed':

        df_poa = pvlib.irradiance.get_total_irradiance(
            surface_tilt=location.latitude,  # input the latitude
            surface_azimuth=180,  # facing South
            dni=df_tmy['DNI'],
            ghi=df_tmy['GHI'],
            dhi=df_tmy['DHI'],
            solar_zenith=solar_position['apparent_zenith'],
            solar_azimuth=solar_position['azimuth'],
            model='isotropic')

        # take the mean of the irradiance
        irr = df_poa['poa_global'].mean()

    elif type == 'tracking':

        tracker_data = pvlib.tracking.singleaxis(
            solar_position['apparent_zenith'],
            solar_position['azimuth'],
            axis_azimuth=180,  # axis is aligned N-S
        )

        tilt = tracker_data['surface_tilt'].fillna(0)
        azimuth = tracker_data['surface_azimuth'].fillna(0)

        df_poa_tracker = pvlib.irradiance.get_total_irradiance(
            surface_tilt=tilt,  # time series for tracking array
            surface_azimuth=azimuth,  # time series for tracking array
            dni=df_tmy['DNI'],
            ghi=df_tmy['GHI'],
            dhi=df_tmy['DHI'],
            solar_zenith=solar_position['apparent_zenith'],
            solar_azimuth=solar_position['azimuth'])

        # take the mean of the irradiance
        irr = df_poa_tracker['poa_global'].mean()

    return irr

def main():

    sample_long_lat()
    df = master()

def fix():

    # read the solar data from nsrd
    with open(f'{root}intermediates/solar/solar_irr.csv', 'rb') as f:
        df = pd.read_csv(f)

    # shift tilt irr up by 1
    df['tilt_irr'] = df['tilt_irr'].shift(-1)

    # drop the rows with nan
    df = df.dropna(how='any').reset_index()

    # for the lat/lon in the dataframe find the county
    temp = pd.Series(all_keys[:len(df)])

    df['geoid'] = temp

    # extract the fips from the GEOID
    df['fips'] = df['geoid'].astype(str).apply(lambda x: x[-5:])

    # for each fips, get the average of the tilt and fixed irr
    df = df.groupby('fips')[['fixed_irr','tilt_irr']].mean().reset_index()

    # output as pickle
    with open(f'{root}intermediates/solar/solar_irr_clean.pkl', 'wb') as f:
        pickle.dump(df, f)
    df.to_csv(f'{root}intermediates/solar/solar_irr_clean.csv', index=False)


    return df

if __name__ == '__main__':
    main()
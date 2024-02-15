import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def combine_plant():

    '''

    Combine all the plant level data into one dataframe

    '''

    df = pd.read_csv(f'{root}intermediates/eia/file_list_annotated.csv')

    # use only plants
    df = df[df['type'].isin(['plant'])]

    # if year is greater than or equal to 2011, set header == 1
    df['head'] = np.where(df['year'] >=2011, 1, 0)

    # note: only utilities have plant level data

    # read and combine all the files into one dataframe
    plant_df = pd.DataFrame()
    full_col_map = map_plant_columns()
    #cols = pd.DataFrame()
    for idx, row in df.iterrows():

        temp = pd.read_excel(row['path'], header=row['head'])
        temp['path'] = row['path']
        temp['year_file'] = row['year']

        col_map = {k:v for k,v in full_col_map.items() if k in temp.columns}
        temp = temp.rename(columns=col_map)

        final_cols = set(col_map.values())
        final_cols.add('path')
        final_cols.add('year_file')

        temp = temp[list(final_cols)]
        plant_df = pd.concat([plant_df,temp], ignore_index=True,axis=0)

    return plant_df


def map_plant_columns():

    col_map = {'COUNTYCODE':'county_code',
               'County Code':'county_code',
               'CTYCODE':'county_code',
               'CNTYNAME':'county_name',
                'COUNTY':'county_name',
               'COUNTYNAME':'county_name',
                'COUNTY_NAME':'county_name',
               'CTYNAME':'county_name',
                'County Name':'county_name',
               'PLANTSTATE':'plant_state',
               'PLNTST':'plant_state',
               'PLNTSTATE':'plant_state',
               'Plant State':'plant_state',
               'STATE':'plant_state',
               'State':'plant_state',
               'Latitude':'lat',
               'Longitude':'lon',
                'Plant Code':'plant_code',
                'PLANT_CODE':'plant_code',
               'PLNTCODE':'plant_code',
               'PLANT_CODE.1':'plant_name',
                'Plant Name':'plant_name',
                'PLANT_NAME':'plant_name',
               'PLANT NAME':'plant_name',
               'PLNTNAME':'plant_name',
    }


    return col_map


def clean_plant(plant_df):

    # 1993 file has everything duplicated, drop duplicates if year=1993
    plant_df = plant_df[~((plant_df['year_file'] == 1993) & (plant_df.duplicated(['plant_code','year_file'])))]

    # make lat/lon numeric
    plant_df['lat'] = pd.to_numeric(plant_df['lat'], errors='coerce')
    plant_df['lon'] = pd.to_numeric(plant_df['lon'], errors='coerce')

    # drop if plant_code is null
    plant_df = plant_df[~pd.isnull(plant_df['plant_code'])]

    # duplicates? check if plant_code and year provide a key
    if not plant_df.set_index(['plant_code', 'year_file']).index.is_unique:
        print('Duplicates found')
        raise

    # match the counties to the plant location
    plant_df = match_counties(plant_df)

    # select variables
    plant_df = plant_df[['plant_code','plant_name', 'year_file', 'fips']]

    # output
    with open(f'{root}intermediates/eia/plant.pkl', 'wb') as f:
        pickle.dump(plant_df, f)

    plant_df.to_csv(f'{root}intermediates/eia/plant.csv', index=False)

    return None

def make_constant(df, id_var, var):


    '''
    make a variable constant across an id var
    by taking the mode
    '''

    df_counts = df.groupby([id_var]).agg(var = (var,'nunique'))

    print(df_counts['var'].value_counts())

    result = df[~pd.isnull(df[var])].groupby(['plant_code'])[var].agg(pd.Series.mode).to_frame()

    # if  there are multiple modes, take the first one
    result[var] = result[var].apply(lambda x: x[0] if isinstance(x, np.ndarray) else x)

    df = df.drop(columns=[var])
    df = df.merge(result, how='left', on=id_var)

    df = df.reset_index(drop=True)

    return df


def state_county_code(plant_df):

    # 1. generate fips from state and county code

    # create the fips
    plant_df['fips1'] = plant_df['state_fips'] + plant_df['county_code'].astype(
        'Int64', errors='ignore').astype(
        str).str.zfill(3)
    plant_df['fips1'] = np.where(pd.isnull(plant_df['state_fips']) | pd.isnull(plant_df['county_code']), np.nan,
                                 plant_df['fips1'])

    plant_df = make_constant(plant_df, 'plant_code', 'fips1')

    return plant_df

def state_matched_county_code(plant_df):

    # 2. generate fips from state and matched county code
    plant_df['fips2'] = plant_df['state_fips'] + plant_df['matched_county_code']
    plant_df['fips2'] = np.where(pd.isnull(plant_df['state_fips']) | pd.isnull(plant_df['matched_county_code']), np.nan,
                                 plant_df['fips2'])

    plant_df = make_constant(plant_df, 'plant_code', 'fips2')

    return plant_df

def latlon_county_code(plant_df):

    # 3. generate fips from lat and lon

    # read county pickle file
    with open(f'{root}/intermediates/counties/county_panel_geo.pkl', 'rb') as f:
        counties = pickle.load(f)

    # select only one year (NOTE WE ASSUME THE COUNTY BOUNDARIES DID NOT CHANGE)
    counties = counties.drop_duplicates(['fips'])

    plant_df = make_constant(plant_df, 'plant_code', 'lon')
    plant_df = make_constant(plant_df, 'plant_code', 'lat')

    plant_df['fips3'] = np.nan
    for idx, row in plant_df.iterrows():

        if idx % 1000 == 0:
            print(idx)

        lat = row['lat']
        lon = row['lon']

        try:
            if ~pd.isnull(lat) | ~pd.isnull(lon):
                plant_df.loc[idx, 'fips3'] = latlon_to_fips(lon, lat, counties)
        except:
            print(idx)
            raise

    return plant_df

def latlon_to_fips(lon, lat, polygon):

    result = polygon[polygon.contains(Point(lon,lat))]

    if len(result) == 0:
        return np.nan

    else:
        return result['state_fips'].iloc[0] + result['county_fips'].iloc[0]

def match_county_name_to_code(plant_df):

    '''

    using the counties spreadsheet, match the county name to the county code

    '''

    # read pickle file for counties
    with open(f'{root}intermediates/counties/county_panel.pkl', 'rb') as f:
        counties = pd.DataFrame(pickle.load(f))

    counties = counties[['county_name','county_fips','state_fips']].drop_duplicates()

    #make lower case and remove "County"
    counties['county_name'] = counties['county_name'].str.lower()

    for w in ['county','parish','borough','municipality']:
        counties['county_name'] = counties['county_name'].str.replace(w, '').str.strip()

    # rename county_fips to matched_county_code
    counties = counties.rename(columns={'county_fips':'matched_county_code'})

    # check if county is uniquely identified
    if not (counties['county_name'] + counties['state_fips'].astype(str)).is_unique:
        raise

    # merge to plant_df
    plant_df = plant_df.merge(counties, how='left', left_on=['county_name','state_fips'],
                              right_on=['county_name','state_fips'])

    return plant_df

def match_counties(plant_df):

    plant_df = plant_df.sort_values(['plant_code','year_file'], ascending=True).reset_index()

    # convert state to two letter code
    plant_df['state_fips'] = plant_df['plant_state'].map(utils.state_codes)

    # convert county name to lowercase
    plant_df['county_name'] = plant_df['county_name'].str.lower()

    # find the code based on county name

    plant_df = match_county_name_to_code(plant_df)

    # 1. use the given state code and county code - fips1
    plant_df = state_county_code(plant_df)

    # 2. use the given state code and county name (to get county code) -fips2
    plant_df = state_matched_county_code(plant_df)

    # 3. use the lat lon to get the county code - fips3
    plant_df = latlon_county_code(plant_df)

    # Priority: fips3, fips1, fips2
    plant_df['fips'] = plant_df['fips3'].fillna(plant_df['fips1']).fillna(plant_df['fips2'])

    # Manually fill in ----------
    # Hatch Solar Energy Center is in Dona Ana County, NM
    plant_df.loc[plant_df['plant_code'] == 57591, 'fips'] = '35013'
    # Laurel Oaks Solar is in Hillsborough County, FL
    plant_df.loc[plant_df['plant_code'] == 65684, 'fips'] = '12057'
    # NMSU Solar and Storage is in Dona Ana County, NM
    plant_df.loc[plant_df['plant_code'] == 64881, 'fips'] = '35013'
    # Roadrunner Solar is in upton county, TX
    plant_df.loc[plant_df['plant_code'] == 57338, 'fips'] = '48461'
    # SunE EPE2 LLC is in Dona Ana County, NM
    plant_df.loc[plant_df['plant_code'] == 57985, 'fips'] = '35013'
    # WSMR I is in Dona Ana County, NM
    plant_df.loc[plant_df['plant_code'] == 58010, 'fips'] = '35013'

    # Analyze the missing counties
    # note there may also be an issue of some counties not being in the county panel
    # we will deal with those when making the county level dataset
    n_missing = (plant_df['fips'].isnull()).sum()

    print('N plant-years missing counties: ', n_missing)

    # separate the missing counties into another dataset
    plant_df_missing = plant_df[plant_df['fips'].isnull()]

    # output
    plant_df_missing.to_csv(f'{root}intermediates/eia/plant_missing.csv', index=False)

    # if missing set the fips to "unknown"
    plant_df['fips'] = plant_df['fips'].fillna('unknown')


    return plant_df


def main():

    plant_df = combine_plant()
    clean_plant(plant_df)


if __name__ == '__main__':
    main()
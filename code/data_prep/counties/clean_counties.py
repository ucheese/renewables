import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def read_files():

    # Read in the data
    df2020 = pd.read_csv(f'{root}data/census/counties/national_county2020.txt', sep='|')
    df2010 = pd.read_csv(f'{root}data/census/counties/national_county2010.txt', sep=',', header=None)

    # Subset the data
    cols = ['STATE', 'STATEFP', 'COUNTYFP', 'COUNTYNAME', 'CLASSFP']
    df2010.columns = cols
    df2020 = df2020[cols]

    # Add year column
    df2010['year'] = 2010
    df2020['year'] = 2020

    # Combine the data
    df = pd.concat([df2010, df2020], axis=0)

    return df



def make_county_panel(df):

    # Goal: make a panel of county years
    # For now, only keep counties that have the same name and code across years
    # May need to revisit this later

    df['STATEFP'] = df['STATEFP'].astype(str).str.zfill(2)
    df['COUNTYFP'] = df['COUNTYFP'].astype(str).str.zfill(3)

    df['fips'] = df['STATEFP'].astype(str).str.zfill(2) + df['COUNTYFP'].astype(str).str.zfill(3)

    df['name_fips']  = df['fips'] + df['COUNTYNAME']
    # count the number of times each county appears
    df['count'] = df.groupby(['name_fips'])['name_fips'].transform('count')

    # 46 counties occur only once, drop for now

    # keep only counties that occur twice
    df = df[df['count'] == 2]

    # rename columns
    df = df.rename(columns={'STATE': 'state',
                            'STATEFP':'state_fips',
                            'COUNTYFP': 'county_fips',
                            'COUNTYNAME': 'county_name',
                             'CLASSFP':'class_fips'})

    # the classes are county equivalents

    # drop extra columns

    df = df.drop(columns={'year','name_fips','count', 'class_fips'})
    df = df.drop_duplicates()

    df['fips'].is_unique

    # make panel
    df['year'] = ','.join([str(y) for y in range(1990, 2023+1)])
    df['year'] = df['year'].str.split(',')
    df = df.explode('year')
    df['year'] = df['year'].astype(int)

    return df

def set_county_boundaries(df):

    # assume that county boundaries are the same across years, with 2010 as the reference year
    # may need to go back and fix this

    # read the gdf
    gdf = gpd.read_file(f'{root}data/census/counties_shp/gz_2010_us_050_00_500k/gz_2010_us_050_00_500k.shp')
    gdf = gdf.to_crs({'init': 'epsg:4326'})

    # make variable for the fips
    gdf['fips'] = gdf['STATE'] + gdf['COUNTY']

    # merge the polygon to the counties df
    df = df.merge(gdf[['fips','geometry']], on='fips', how='left')

    # drop if geometry is not merged
    df = df.dropna(subset=['geometry'])

    # output
    df.drop(columns=['geometry']).to_csv(f'{root}intermediates/counties/county_panel.csv', index=False)

    # output as pickle
    with open(f'{root}intermediates/counties/county_panel.pkl', 'wb') as f:
        pickle.dump(df, f)

    # as geodataframe
    geo_df = gpd.GeoDataFrame(df, geometry='geometry')
    with open(f'{root}intermediates/counties/county_panel_geo.pkl', 'wb') as f:
        pickle.dump(geo_df, f)

    return None

def main():

    df = read_files()
    df = make_county_panel(df)
    set_county_boundaries(df)

if __name__ == '__main__':

    main()
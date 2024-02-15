import getpass
import sys
import pandas as pd
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def merge_eia(df):

    # read in eia data
    with open(f'{root}intermediates/eia/eia_county.pkl', 'rb') as f:
        eia = pickle.load(f)

    # check if there were fips in eia that were not in counties
    fips_missing = eia[~eia['fips'].isin(df['fips'])]['fips'].unique()

    # get the number of plants for these fips
    eia['n_solar_or_wind'] = eia['n_plants_solar'] + eia['n_plants_wind']
    conflict = eia[eia['fips'].isin(fips_missing)].groupby('fips')['n_solar_or_wind'].sum().reset_index()

    print('Fips were in the EIA data but not in the counties data:')
    print(fips_missing)

    # output the conflicts
    conflict.to_csv(f'{root}intermediates/master/merge_log/eia_conflict.csv', index=False)

    # merge
    df = df.merge(eia, how='left', on=['fips','year'])

    #eia = eia.merge(df, how='left', on=['fips','year'], indicator=True)

    # only keep 2001 forward
    df = df[df['year'] >= 2001]

    # fill na
    df = df.fillna(0)

    return df

def merge_turbine(df):

    turbine = pd.read_csv(f'{root}intermediates/eere/capacity_height_diameter.csv')
    df = df.merge(turbine, how='left', on='year')

    return df

def merge_wind(df):

    with open(f'{root}intermediates/global_atlas/wind.pkl', 'rb') as f:
        wind = pickle.load(f)

    heights = df['height'].dropna().unique()

    #for each fips, interpolate the wind speed at the turbine height

    def interpolate_group(group):

        group = group.set_index('height')
        interpolated = group.reindex(group.index.union(heights)).interpolate(method='linear').loc[heights]
        interpolated = interpolated.drop(columns=['fips','count'])
        interpolated = interpolated.reset_index()

        return interpolated

    # Applying the interpolation function to each group
    interpolated_wind = wind.groupby(['fips','count']).apply(interpolate_group).reset_index()
    interpolated_wind = interpolated_wind.drop(columns=['level_2'])

    interpolated_wind = interpolated_wind.add_suffix('_wind')

    df = df.merge(interpolated_wind, how='left',
                  left_on=['fips','height'], right_on=['fips_wind','height_wind'],
                  suffixes=('','_wind'))

    # drop capacity, diameter, and height
    df = df.drop(columns=['capacity','diameter','height'])

    return df

def merge_solar_costs(df):

    # read the nrel solar costs data
    solar_costs = pd.read_excel(f'{root}data/nrel/solar_cost/solar_costs.xlsx')

    # reshape solar costs to be wide
    solar_costs = solar_costs.pivot(index=['year'], columns='type', values='cost').reset_index()

    # merge the solar costs
    df = df.merge(solar_costs, how='left', on='year')

    return df

def merge_solar(df):

    # read in the solar irr data
    with open(f'{root}intermediates/solar/solar_irr_clean.pkl', 'rb') as f:
        solar = pickle.load(f)

    # merge the data on fips
    df = df.merge(solar, how='left', on='fips')

    # check if any fips were not merged (these are missing for now because we didn't finish running the file)
    fips_missing = df[df['tilt_irr'].isna()]['fips'].unique()

    # get the diff between fixed and tilt irr
    df['diff_irr'] = df['tilt_irr'] - df['fixed_irr']
    df['diff_cost'] = df['tracker'] - df['fixed']

    # "tracking potential"
    df['tracking_potential'] = df['diff_irr'] / df['diff_cost']


    return df


def merge_bank(df):

    #read in the bank data
    with open(f'{root}intermediates/bank/bank.p', 'rb') as f:
        bank = pickle.load(f)

    df = df.merge(bank, how='left', on=['fips','year'])

    return df

def merge_qcew(df):

    # read in the qcew data
    with open(f'{root}intermediates/qcew/employment.pkl', 'rb') as f:
        qcew = pickle.load(f)

    df = df.merge(qcew, how='left', on=['fips','year'], indicator=True)

    # drop indicator
    df = df.drop(columns=['_merge'])

    return df

def merge_zillow(df):

    # read in the zillow data
    with open(f'{root}intermediates/zillow/zillow.pkl', 'rb') as f:
        zillow = pickle.load(f)

    df = df.merge(zillow, how='left', on=['fips','year'], indicator=True)

    # drop indicator
    df = df.drop(columns=['_merge'])

    return df

def merge_state_local(df):

    # read in the state local data
    with open(f'{root}intermediates/state_local/state_local_combined.pkl', 'rb') as f:
        state_local = pickle.load(f)

    df = df.merge(state_local, how='left', on=['fips','year'], indicator=True)

    return df

def output(df):

    # drop the geometry column
    df = df.drop(columns=['geometry'])

    # keep only up to 2022
    df = df[df['year'] <= 2022]

    # output
    with open(f'{root}intermediates/master/master.pkl', 'wb') as f:
        pickle.dump(df, f)
    df.to_csv(f'{root}intermediates/master/master.csv', index=False)

    return None

# need to output a merge error message


def main():

    # read in counties data from pickle
    with open(f'{root}intermediates/counties/county_panel.pkl', 'rb') as f:
        df = pickle.load(f)

    # drop 2023
    df = df[df['year'] != 2023]

    # no wind for state fips = 72, drop Puerto Rico
    df = df[df['fips'] != 72]

    df = merge_eia(df)
    df = merge_turbine(df)
    df = merge_wind(df)
    # solar starts in 2010 because we only have the cost data since 2010
    df = merge_solar_costs(df)
    # bank data starts in 2005
    df = merge_bank(df)
    df = merge_qcew(df)
    df = merge_zillow(df)
    df = merge_state_local(df)

    output(df)

if __name__ == '__main__':
    main()
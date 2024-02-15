import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils


def merge():

    # read in plant data
    with open(f'{root}intermediates/eia/plant.pkl', 'rb') as f:
        plant = pickle.load(f)
    plant = plant.rename(columns={'year_file':'year'})

    # read in generator data
    with open(f'{root}intermediates/eia/generator.pkl', 'rb') as f:
        gen = pickle.load(f)

    # merge plant onto generator
    df = gen.merge(plant, how='left', on=['plant_code','year'], indicator=True)

    print(df['_merge'].value_counts())

    # no unmerged generators! drop _merge
    df = df.drop(columns=['_merge'])

    # sort by plant_code and year
    df = df.sort_values(['plant_code','year'], ascending=True).reset_index()

    # output
    with open(f'{root}intermediates/eia/eia.pkl', 'wb') as f:
        pickle.dump(df, f)
    df.to_csv(f'{root}intermediates/eia/eia.csv', index=False)

    return df

def make_county(df):

    '''
    make a county level dataset
    '''

    # tag the solar and the wind
    col         = 'prime_mover'
    conditions  = [ df[col] == 'photovoltaic', \
                    df[col] == 'onshore wind' ]
    choices     = [ 'solar', 'wind' ]

    df['tech'] = np.select(conditions, choices, default='other')

    # keep operating plants
    df = df[df['status'] == 'operating']

    # do group by to get the number in each county

    agg = {
        'plant_code': pd.Series.nunique,  # Count unique plant_codes
        'id': 'count',                    # Count of ids
        'capacity': 'sum'                 # Sum of capacity
    }

    agg_df = df.groupby(['fips', 'tech', 'year']).agg(agg).reset_index()
    agg_df.rename(columns={'plant_code': 'n_plants', 'id': 'n_generators'}, inplace=True)

    # reshape wide
    df = agg_df.pivot(index=['fips','year'], columns='tech', values=['n_plants','capacity'])

    # collapse multiindex into one column name
    df.columns = ['_'.join(col).strip() for col in df.columns.values]
    df = df.reset_index()

    # fill nan with 0
    df = df.fillna(0)

    # sort by fips and year
    df = df.sort_values(['fips','year'], ascending=True).reset_index(drop=True)

    # output
    with open(f'{root}intermediates/eia/eia_county.pkl', 'wb') as f:
        pickle.dump(df, f)
    df.to_csv(f'{root}intermediates/eia/eia_county.csv', index=False)

    return None



def main():

    df = merge()
    make_county(df)

if __name__ == '__main__':
    main()
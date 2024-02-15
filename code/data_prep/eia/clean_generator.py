import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils


def combine_generator():

    df = read_file_list()

    # use only generator or existing generator
    df = df[df['type'].isin(['generator','existing_generator'])]

    # clean file format for 2012-2022
    gen_12_22 = df[df['year'].between(2012,2022)]
    gen_12_22_data = clean_generator_12_22(gen_12_22)

    # clean file format for 2011
    gen_11 = df[df['year'].between(2011,2011)]
    gen_11_data = clean_generator_11(gen_11)

    # clean file format for 2009-2010
    gen_09_10 = df[df['year'].between(2009,2010)]
    gen_09_10_data = clean_generator_09_10(gen_09_10)

    # clean file format for 2001-2008
    gen_01_08 = df[df['year'].between(2001,2008)]
    gen_01_08_data = clean_generator_01_08(gen_01_08)

    # clean file format for 1998-2000
    gen_98_00 = df[df['year'].between(1998,2000)]
    gen_98_00_data = clean_generator_98_00(gen_98_00)

    # clean file format for 1992-1997
    gen_92_97 = df[df['year'].between(1992,1997)]
    gen_92_97_data = clean_generator_92_97(gen_92_97)

    # clean file format for 1990-1991
    gen_90_91 = df[df['year'].between(1990,1991)]
    gen_90_91_data = clean_generator_90_91(gen_90_91)

    # combine all
    all = pd.concat([gen_90_91_data,
                     gen_92_97_data,
                     gen_98_00_data,
                     gen_01_08_data,
                     gen_09_10_data,
                     gen_11_data,
                     gen_12_22_data], ignore_index=True)

    return all

def read_chunk(paths, header_row):

    df = pd.DataFrame()

    for idx, row in paths.iterrows():

        path = row['path']
        year = row['year']

        temp = pd.read_excel(path, sheet_name=row['sheetname'], header=header_row)
        temp['year'] = year

        df = pd.concat([df, temp], ignore_index=True)

    return df


def clean_generator_90_91(paths):

    df = read_chunk(paths, header_row=0)

    col_map = {
        'year': 'year',
        'Plant Code': 'plant_code',
        'Generator Code': 'generator_code',
        'Prime Mover': 'prime_mover',
        'Nameplate Capacity': 'capacity',
        'Status Code': 'status_code',
        'In-Service Year': 'in_service_year',
        'In-Service Month': 'in_service_month',
    }

    df = df.rename(columns=col_map)
    df = df[col_map.values()]

    return df


def clean_generator_92_97(paths):

    df = read_chunk(paths, header_row=0)

    col_map = {
        'year': 'year',
        'PLNTCODE': 'plant_code',
        'GENCODE': 'generator_code',
        'PRIMEMOVER': 'prime_mover',
        'NAMEPLATE': 'capacity',
        'STATUSCODE': 'status_code',
        'INSERVYR': 'in_service_year',
        'INSERVMTH': 'in_service_month',
    }

    df = df.rename(columns=col_map)
    df = df[col_map.values()]

    return df



def clean_generator_98_00(paths):

    df = read_chunk(paths, header_row=0)

    col_map = {
        'year': 'year',
        'PLANT_CODE': 'plant_code',
        'GENERATOR_ID': 'generator_code',
        'PRIMEMOVER': 'prime_mover',
        'EXISTING_NAMEPLATE': 'capacity',
        'EXISTING_STATUS': 'status_code',
        'OPERATING_MONTH': 'in_service_month',
        'OPERATING_YEAR': 'in_service_year'
    }

    df = df.rename(columns=col_map)
    df = df[col_map.values()]

    return df

def clean_generator_09_10(paths):

    df = read_chunk(paths, header_row=0)

    col_map = {
        'year': 'year',
        'PLANT_CODE': 'plant_code',
        'GENERATOR_ID': 'generator_code',
        'PRIME_MOVER': 'prime_mover',
        'NAMEPLATE': 'capacity',
        'STATUS': 'status_code',
        'OPERATING_MONTH': 'in_service_month',
        'OPERATING_YEAR': 'in_service_year'
    }

    df = df.rename(columns=col_map)
    df = df[col_map.values()]

    return df

def clean_generator_01_08(paths):

    df = read_chunk(paths, header_row=0)

    col_map = {
    'year': 'year',
    'PLNTCODE': 'plant_code',
    'GENCODE': 'generator_code',
    'PRIMEMOVER': 'prime_mover',
    'NAMEPLATE': 'capacity',
    'STATUS': 'status_code',
    'INSVMONTH': 'in_service_month',
    'INSVYEAR': 'in_service_year'
    }

    df = df.rename(columns=col_map)
    df = df[col_map.values()]

    return df

def clean_generator_12_22(paths):

    df = read_chunk(paths, header_row=1)

    col_map = {
        'year': 'year',
        'Plant Code': 'plant_code',
        'Generator ID': 'generator_code',
        'Prime Mover': 'prime_mover',
        'Nameplate Capacity (MW)': 'capacity',
        'Status': 'status_code',
        'Operating Month': 'in_service_month',
        'Operating Year': 'in_service_year'
    }

    df = df.rename(columns=col_map)
    df = df[col_map.values()]

    return df

def clean_generator_11(paths):

    df = read_chunk(paths, header_row=1)

    col_map = {
        'year': 'year',
        'PLANT_CODE': 'plant_code',
        'GENERATOR_ID': 'generator_code',
        'PRIME_MOVER': 'prime_mover',
        'NAMEPLATE': 'capacity',
        'STATUS': 'status_code',
        'OPERATING_MONTH': 'in_service_month',
        'OPERATING_YEAR': 'in_service_year'
    }

    df = df.rename(columns=col_map)
    df = df[col_map.values()]

    return df


def read_file_list():

    df = pd.read_csv(f'{root}intermediates/eia/file_list_annotated.csv')

    return df

def clean_generator(df):

    # drop if all nan, except year
    df = df.dropna(how='all', subset=[x for x in df.columns if x != 'year'])

    # generate plant-generator id
    df['id'] = df['plant_code'].astype(int).astype(str) + '_' + df['generator_code'].astype(str)

    # some duplicates in earlier files (1990, 1991, 2001, and 1997)
    # drop total duplicates
    df = df.drop_duplicates()

    # check if plant-generator id is unique within year
    df['unique'] = df.groupby(['year','id'])['id'].transform('count')

    dups = df[df['unique'] > 1]
    # one plant has a duplicated generator in 1990 and 1991, just drop it completely for now
    df = df[~((df['id'] == '2518_1') & (df['year'].isin([1990,1991])))]

    # remove proposed generators pre-1997
    df = df [~(( df['year'] <= 1997 ) & pd.isnull(df['status_code']))]

    # map the status codes
    status_map = {
        'OP': 'operating',
        'SB': 'standby',
        'RE': 'retired',
        'OS': 'out_of_service',
        'OA': 'out_of_service',
        'SD': 'sold_non_utility',
        'SC':  '??',
        'BU': 'backup',
        'TS': 'construction_completed_testing'
    }

    df['status'] = df['status_code'].map(status_map)

    # map the prime mover

    prime_mover_map = {
            'IC': 'internal combustion',
            'HY': 'hydroelectric turbine',
            'ST': 'steam turbine',
            'GT': 'combustion gas turbine',
            'PV': 'photovoltaic',
            'SP': 'photovoltaic',
            'CT': 'combustion cycle turbine',
            'WT': 'onshore wind',
            'HC': 'hydraulic turbine',
            'CA': 'combined cycle steam turbine',
            'PS': 'hydraulic turbine',
            'BA': 'energy storage',
            'BT': 'binary cycle turbine',
            'FC': 'fuel cell',
            'JE': 'jet engine',
            'CS': 'combined cycle single shaft',
            'HL': 'hydraulic turbine pipeline',
            'NP': 'steam turbine',
            'HR': 'hydraulic turbine',
            'OT': 'other',
            'CW': 'combined cycle steam turbine',
            'NB': 'steam turbine',
            'GE': 'steam turbine geothermal',
            'CH': 'steam turbine',
            'AB': 'atmospheric combustion',
            'FW': 'energy storage',
            'CP': 'energy storage',
            'CE': 'energy storage',
            'CC': 'combined cycle',
            'IG': 'integrated coal gasification',
            'WS': 'offshore wind',
            'NH': 'steam turbine',
            'SS': 'steam turbine solar',
            'CG': '??',
            'PB': 'pressurized fluidized bed combustion',
            'ic': 'internal combustion'
    }

    df['prime_mover'] = df['prime_mover'].map(prime_mover_map)


    # capacity was in kW up to and including 2000
    # divide capacity by 1,000 before 2000
    df['capacity'] = np.where((df['year'] <= 2000), df['capacity']/1000, df['capacity'])


    cols = ['year','plant_code','generator_code','id','prime_mover','capacity','status','in_service_year','in_service_month']
    df = df[cols]

    # output dataframe
    with open(f'{root}intermediates/eia/generator.pkl', 'wb') as f:
        pickle.dump(df, f)

    df.to_csv(f'{root}intermediates/eia/generator.csv',index=False)


    return df

def main():

    df = combine_generator()
    df = clean_generator(df)


if __name__ == '__main__':
    main()
import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def create_name_fips_key():

    '''
    earlier years do not have fips code, so we use the later year data set to create a key
    '''

    # clean up later years ========================
    df2 = pd.read_pickle(f'{root}/intermediates/state_local/state_local_post-2012.pkl')

    # get unique id_name and fips
    key2 = df2[['county_name','fips']].drop_duplicates()

    # make county name lower case and remove spaces and punctuation
    key2['county_name'] = key2['county_name'].str.lower().str.strip()
    key2['county_name'] = key2['county_name'].str.replace('-','').str.replace('.','').str.replace(',',
                                                                                                  '').str.replace(' ','')

    # get the states fips code
    key2['fips_state'] = key2['fips'].str[:2]

    # clean up earlier years ========================
    df1 = pd.read_pickle(f'{root}/intermediates/state_local/state_local_pre-2013.pkl')

    key1 = df1[['county_name','fips_state']].drop_duplicates()

    key1['orig_county_name'] = key1['county_name']

    # remove county from the name
    key1['county_name'] = key1['county_name'].str.replace(' COUNTY','')
    key1['county_name'] = key1['county_name'].str.replace(' PARISH','')
    key1['county_name'] = key1['county_name'].str.lower().str.strip()
    key1['county_name'] = key1['county_name'].str.replace('-','').str.replace('.','').str.replace(',',
                                                                                                  '').str.replace(' ','')

    # merge
    key1 = key1.merge(how='left', right=key2, on=['county_name','fips_state'])

    # fill in manually
    fill_in = {
    ('metropolitandade', '12'): '12025',
    ('jefferson', '21'): '21111',
    ('berkshire', '25'): '25003',
    ('ftbend', '48'): '48157',
    ('chattahoochee', '13'): '13053',
    ('quitman', '13'): '13239',
    ('webster', '13'): '02282',
    ('obrien', '19'): '19141',
    ('greeley', '20'): '20071',
    ('shannon', '46'): '46113',
    ('yakutatborough', '02'): '02282',
    ('skagwayborough', '02'):'02230',
    }

    for key, val in fill_in.items():
        print(key,val)
        key1['fips'] = np.where((key1['county_name'] == key[0]) & (key1['fips_state'] == key[1]), val, key1['fips'])

    assert(len(key1[key1['fips'].isna()]) == 0)

    key1 = key1.drop(columns=['county_name']).rename(columns={'orig_county_name':'county_name'})
    key1 = key1.drop_duplicates()

    return key1


def read_data():

    df1 = pd.read_pickle(f'{root}/intermediates/state_local/state_local_pre-2013.pkl')
    df2 = pd.read_pickle(f'{root}/intermediates/state_local/state_local_post-2012.pkl')

    # get the fips for df1
    key = create_name_fips_key()

    df1 = df1.merge(key, how='left', on=['county_name','fips_state'])

    # check that fips year is a unique identifier
    assert(len(df1[['county_name','fips_state','year']].drop_duplicates()) == len(df1))

    return df1, df2

def compare_2012(df1, df2):

    df1 = df1[df1['year'] == 2012]
    df2 = df2[df2['year'] == 2012]


    # get variables that are in the intersection of both columns
    cols = list(set(df1.columns).intersection(set(df2.columns)))

    # merge df1 and df2
    df = pd.merge(df1, df2, on=['fips','year'], how='outer', indicator=True)

    # see the number of matches
    print(df['_merge'].value_counts())

    # get the left only and the right only
    left_only = df[df['_merge'] == 'left_only']
    right_only = df[df['_merge'] == 'right_only']

    # there are two that are not matched, I think these are counties that are changed, drop them
    df = df[df['_merge'] == 'both']

    # for the common cols, check if the values are the same
    for col in cols:
        if col not in ['county_name','year','fips']:
            df[f'{col}_diff'] = df[col+'_x'].astype(int) - df[col+'_y'].astype(int)
            print(col)
            print(len(df[abs(df[f'{col}_diff']) > 1]))

    temp = df[abs(df['property_tax_diff']) > 1][['fips','property_tax_x','property_tax_y', 'property_tax_diff']]
    temp = df[abs(df['property_tax_diff']) > 1][['fips','property_tax_x','property_tax_y', 'property_tax_diff']]


def combine_files():
    df1, df2 = read_data()
    cols = list(set(df1.columns).intersection(set(df2.columns)))

    # keep 2012 from the new data
    df2 = df2[df2['year'] != 2012]

    # keep the common cols
    df1 = df1[cols]
    df2 = df2[cols]

    # stack df1 and df2
    df = pd.concat([df1, df2], axis=0)

    # drop fips state and county name
    df = df.drop(columns=['county_name'])

    # output the dataset
    df.to_pickle(f'{root}/intermediates/state_local/state_local_combined.pkl')

    return None

def main():
    combine_files()

if __name__ == '__main__':
    main()
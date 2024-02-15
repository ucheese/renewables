import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def meta_data(folder_path):

    files = glob.glob(f'/{folder_path}/**/*.*', recursive=True)

    df = pd.DataFrame({'path':files})

    # keep only the text files
    df = df[df['path'].str.contains('Txt')]

    # extract the file name
    df['file_name'] = df['path'].apply(lambda x: os.path.basename(x))

    # extract the year
    df['year'] = df['file_name'].str.extract(r'(\d{2})')[0]

    # keep if the year is between 2000 and 2012
    df = df[(df['year'] >= '00') & (df['year'] <= '12')]

    # get the variables from the excel files
    for idx, row in df.iterrows():

        path = row['path']

        temp = pd.read_csv(path)
        df.loc[idx, 'vars'] = '##'.join(list(temp.columns))

    #explode the variable names into multiple words
    df = df.assign(vars=df.vars.str.split('##')).explode('vars')

    # output
    df.to_csv(f'{root}intermediates/state_local/variable_list.csv',index=False)

    return None


def read_data():

    # from 2000 to 2012

    files = [f'IndFin{str(y)[-2:]}' for y in range(2000, 2012+1)]

    df = pd.DataFrame()

    for f in files:

        a = pd.read_csv(f'{root}data/state_local/_IndFin_1967-2012/{f}a.txt')
        b = pd.read_csv(f'{root}data/state_local/_IndFin_1967-2012/{f}b.txt')
        c = pd.read_csv(f'{root}data/state_local/_IndFin_1967-2012/{f}c.txt')

        a = a.set_index('ID')
        b = b.set_index('ID')
        c = c.set_index('ID')

        # find the columns that are duplicated across the three dataframes
        intersect = list(set(a.columns).intersection(set(b.columns)).intersection(set(c.columns)))

        # remove these columns from b and c
        b = b.drop(columns=intersect)
        c = c.drop(columns=intersect)

        # set the id as the index

        temp = a.merge(b, how='left', left_index=True, right_index=True)
        temp = temp.merge(c, how='left', left_index=True, right_index=True)

        # all the variables are the same so lets vertically stack them
        df = pd.concat([df, temp], axis=0)

    # output as pickle
    df.to_pickle(f'{root}intermediates/state_local/state_local_combined.pkl')

    return None

def clean_data():

    # read pickle file
    df = pd.read_pickle(f'{root}intermediates/state_local/state_local_combined.pkl')

    # get the counties only
    # what I think the type codes are

    # 0 = state
    # 1 = county
    # 2 = city
    # 3 = town
    # 4 = authorities such as airport, water
    # 5 = school districts
    # 6 = federal governments

    df = df[df['Type Code'] == 1]

    # get the fips code
    df['fips_state'] = df['FIPS Code-State'].astype(str).str.zfill(2)
    df['year'] = df['Year4'].astype(int)
    df['county_name'] = df['Name']

    # check fips and year are unique identifier
    assert (len(df[['fips_state','county_name','year']].drop_duplicates()) == len(df))

    # there are no zero data observations
    # apprently zero data for finance were removed from the input file for 2007-2012
    print(df['ZeroData'].value_counts())

    # what are the variables that i want (get from UserGuide.xlsx, tab: 2. Variables)
    # Population
    # Total Revenue
    # Total Revenue from own Sources
    # General Revenue
    # General Revenue from own Sources
    # Total Taxes
    # Property Tax
    # General Charges Total
    # Total Expenditure
    # ZeroData: 1 - this means that all finance variables equal 0,
    # 2- all four major totals equal 0, but at least 1 finance variables not in these totals has data
    # none of these have ZeroData
    # nans or zeros??


    # total revenue includes those marked for specific projects, capital revenues
    # general revenue is day to day operations
    # own sources does not include transfers from the federal or state governments
    # From user guide, all finance data is in $1000's of dollars


    vars = {
        'Population':'population',
        'Total Revenue':'total_rev',
        'Total Rev-Own Sources':'total_rev_own_sources',
        'General Revenue':'gen_rev',
        'Gen Rev-Own Sources':'gen_rev_own_sources',
        'Total Taxes':'total_taxes',
        'Property Tax':'property_tax',
        'Total General Charges':'gen_charges',
        'Total Expenditure': 'total_exp'
    }

    # keep the vars in vars along with fips, year
    df = df[['fips_state','county_name','year'] + list(vars.keys())]

    # map the columns
    df = df.rename(columns=vars)

    # divide everything by 10 to get to millions, except popultion
    finance_vars = list(vars.values())
    finance_vars.remove('population')
    df[finance_vars] = df[finance_vars]/1000

    # output
    df.to_pickle(f'{root}intermediates/state_local/state_local_pre-2013.pkl')

    return None



def main():

    read_data()
    clean_data()



if __name__ == "__main__":
    main()

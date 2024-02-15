import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def import_data():

    # read the files and combine them into one dataframe

    df = pd.DataFrame()

    for y in range(2005, 2021+1):

        temp = pd.read_csv(f'{root}data/cra/retail_loan_county_agg_all_{str(y)}.csv')
        temp['year'] = y
        df = pd.concat([df, temp])

    # get the number of observations by year


    return df


def clean_bank():

    df = import_data()
    df['fips'] = df['State_Code'].astype(str).str.zfill(2) + df['County_Code'].astype(str).str.zfill(3)

    # select the right variables
    vars = ['fips',
            'year',
            'Loan_Orig',
            'Amt_Orig',
            'Loan_Orig_SFam',
            'Amt_Orig_SFam',
            'SB_Loan_Orig',
            'SB_Amt_Orig',
            'Population',
            'HouseHold_Count',
            'Total_Housing_Units',
            'Vacant_Units',
            'Establishments_Small_Business']

    df = df[vars]

    # Loan orig is mortgage loan origination

    # check if year and area fips uniquely identify the observations
    test = df.groupby(['fips', 'year']).size().reset_index().rename(columns={0:'count'})

    if test['count'].max() > 1:
        raise ValueError('fips and year do not uniquely identify the observations')


    # rename variables
    df = df.rename(columns={'Loan_Orig': 'n_loan_orig',
                            'Amt_Orig': 'amt_orig',
                            'Loan_Orig_SFam': 'n_loan_orig_sfam',
                            'Amt_Orig_SFam': 'amt_orig_sfam',
                            'SB_Loan_Orig': 'n_sb_loan_orig',
                            'SB_Amt_Orig': 'sb_amt_orig',
                            'Population': 'population',
                            'HouseHold_Count': 'n_households',
                            'Total_Housing_Units': 'n_housing_units',
                            'Vacant_Units': 'n_vacant_units',
                            'Establishments_Small_Business': 'n_sb'})

    # output
    df.to_csv(f'{root}intermediates/bank/bank.csv', index=False)

    with open(f'{root}intermediates/bank/bank.p', 'wb') as f:
        pickle.dump(df, f)

    #colorscale = [
    #    'rgb(253, 232, 57)',
    #    'rgb(195, 180, 106)',
    #    'rgb(138, 133, 121)',
    #    'rgb(59, 73, 108)',
    #    'rgb(20, 52, 112)',
    #    'rgb(0, 35, 78)',
    #]

    # some counties are missing
    #fig = ff.create_choropleth(fips=list(df['area_fips']), values=list(df['Amt_Orig']),
    #                           colorscale=colorscale, binning_endpoints=[1e4, 5*1e4, 1e5, 5*1e5, 1e6])
    #fig.layout.template = None
    #fig.write_image(f'{root}output/cra/loan_amt.pdf')


if __name__ == '__main__':

    clean_bank()

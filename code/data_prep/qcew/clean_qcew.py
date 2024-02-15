import getpass
import sys
import pandas as pd
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

#https://www.bls.gov/cew/downloadable-data-files.htm

def clean_data(naics, abbrev):

    # read data
    df = pd.read_csv(f'{root}intermediates/qcew/{naics}.csv')

    # get the county level data

    if len(naics) == 2:
        df = df[df['agglvl_title'].str.contains('County, Total Covered')]
    elif len(naics) == 4:
        df = df[df['agglvl_title'].str.contains('County, NAICS 4-digit -- by ownership sector')]
    elif len(naics) == 6:
        df = df[df['agglvl_title'].str.contains('County, NAICS 6-digit -- by ownership sector')]

    print(df['agglvl_title'].value_counts())

    assert len(df) == len(df[['year','area_fips','qtr','own_title']].drop_duplicates())

    # select variables
    df = df[['disclosure_code',
             'year',
             'qtr',
             'area_fips',
             'month1_emplvl',
             'month2_emplvl',
             'month3_emplvl',
             'qtrly_estabs_count',
             'total_qtrly_wages']]

    # keep the last month in the year
    df = df[df['qtr'] == 4]
    df = df.rename(columns={'month3_emplvl':'employment'})

    # collapse within fips and year, sum employment and weekly wage
    # this is summing across the sectors
    df = df.groupby(['area_fips','year']).sum().reset_index()

    # make weekly wage as total quarterly wages divided by (12 x employment)
    df['avg_wkly_wage'] = df['total_qtrly_wages']/(12*df['employment'])

    # drop the total quarterly wages and other employment variables
    df = df.drop(columns=['total_qtrly_wages','month1_emplvl','month2_emplvl'])

    # when disclosure code is "-", replace the employment to be NULL
    #df['employment'] = np.where(df['disclosure_code'].isin(['-','N']),np.nan, df['employment'])

    # fill the fips to be 5 digits
    df['area_fips'] = df['area_fips'].astype(str).str.zfill(5)
    df = df.rename(columns={'area_fips':'fips', 'qtrly_estabs_count':'n_esttabs'})

    df['naics'] = naics
    df['industry'] = abbrev

    # check that fips, year uniquely identify the data
    assert len(df) == len(df[['year','fips']].drop_duplicates())

    # get the duplicates
    duplicates = df[df[['year','qtr','fips']].duplicated(keep=False)]

    return df

def combine_data():

    abbrev_map = {
        '221112':'ff_power',
        '2111':'oil_gas_extract',
        '2121':'coal_mining',
        '221114':'solar_power',
        '221115':'wind_power',
        '10':'total'
    }

    df = pd.DataFrame()

    for naics, abbrev in abbrev_map.items():
        df = pd.concat([df, clean_data(naics, abbrev)], axis=0)

    # reshape from long to wide
    df = df.pivot(index=['fips','year'], columns=['industry'], values=['employment','avg_wkly_wage',
                                                                       'n_esttabs']).reset_index()
    df = df.reset_index()

    # concatenate the column names
    df.columns = ['_'.join(col).strip() if col[1]!='' else col[0] for col in df.columns.values]

    # output
    df.to_csv(f'{root}intermediates/qcew/employment.csv', index=False)
    with open(f'{root}intermediates/qcew/employment.pkl', 'wb') as f:
        pickle.dump(df, f)



def solar_employment():

    year = 2023
    #df = pd.read_csv(f'{root}data/qcew/2023.q1-q1.by_industry/2023.q1-q1 221114 NAICS 221114 Solar electric power
    # generation.csv')
    df = pd.read_csv(f'{root}data/qcew/2023.q1-q1.by_industry/2023.q1-q1 22 NAICS 22 Utilities.csv')

    df = df[df['agglvl_title'].str.contains('County')]
    df = df[df['own_title'] == 'Private']

    # replace the employment to be NULL if disclosure code is N

    #df['month1_emplvl'] = np.where(df['disclosure_code'] == 'N', -1, df['month1_emplvl'])

    df = df[df['disclosure_code'] != 'N']
    df = df[['area_fips','month1_emplvl']]

    # there is one duplicate
    df = df[~df['area_fips'].duplicated()]

    colorscale = [
        'rgb(253, 232, 57)',
        'rgb(195, 180, 106)',
        'rgb(138, 133, 121)',
        'rgb(59, 73, 108)',
        'rgb(20, 52, 112)',
        'rgb(0, 35, 78)',
    ]


    # some counties are missing
    fig = ff.create_choropleth(fips=list(df['area_fips']), values=list(df['month1_emplvl']),
                               colorscale=colorscale, binning_endpoints=[10, 100, 1000, 10000],)
    fig.layout.template = None
    fig.write_image(f'{root}output/qcew/utilities_employment.pdf')


def import_data(year, industry, industry2016):

    try:
        df = pd.read_csv(f'{root}data/qcew/{year}.q1-q4.by_industry/{year}.q1-q4 {industry}.csv')
    except:
        df = pd.read_csv(f'{root}data/qcew/{year}.q1-q4.by_industry/{year}.q1-q4 {industry2016}.csv')

    return df

def process_ind(industry, industry2016):

    master = pd.DataFrame()

    for year in range(2010, 2023):
        df = import_data(year, industry, industry2016)

        # keep US
        df = df[df['agglvl_title'].str.contains('National')]

        # keep relevant vars
        df = df[['year','qtr','own_title','month1_emplvl', 'month2_emplvl', 'month3_emplvl']]

        # set industry
        df['industry'] = industry

        master = pd.concat([master,df], axis=0)


    return master

def process_all():

    master = pd.DataFrame()

    # coal mining
    industry = '2121 Coal mining'
    industry2016 = '2121 NAICS 2121 Coal mining'

    df = process_ind(industry, industry2016)
    master = pd.concat([master,df], axis=0)

    # fossil fuel electric power generation
    industry = '221112 Fossil fuel electric power generation'
    industry2016 = '221112 NAICS 221112 Fossil fuel electric power generation'

    df = process_ind(industry, industry2016)
    master = pd.concat([master,df], axis=0)

    # oil and gas extraction
    industry = '2111 Oil and gas extraction'
    industry2016 = '2111 NAICS 2111 Oil and gas extraction'

    df = process_ind(industry, industry2016)
    master = pd.concat([master,df], axis=0)

    # collapse across the ownership
    master = master.groupby(['year','qtr','industry']).sum().reset_index()

    # keep only Q1
    master = master[master['qtr'] == 1]

    master['avg_employment'] = master[['month1_emplvl', 'month2_emplvl', 'month3_emplvl']].sum(axis=1)/1e3

    industries = ['221112 Fossil fuel electric power generation', '2111 Oil and gas extraction', '21211 Coal mining']

    master['year'] = master['year'].astype(str)
    sns.lineplot(data=master, x='year', y='avg_employment', hue='industry', legend=True, linewidth=4)
    plt.ylabel("Employment in the U.S. ('000s)")
    plt.xlabel("Year")
    plt.xticks(master['year'][::6])
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    sns.despine()

    plt.savefig(f'{root}output/qcew/fossil_fuel_employment.pdf', bbox_inches='tight')


def main():

    combine_data()



if __name__ == '__main__':

    main()
import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils


def read_data():

    with open(f'{root}intermediates/master/master.pkl', 'rb') as f:
        df = pickle.load(f)

    return df


## Table 1

def table1(df):

    # get number of years, number of counties, and total number of observations

    min_year = df['year'].min()
    max_year = df['year'].max()
    years = df['year'].nunique()
    counties = df['fips'].nunique()
    obs = df.shape[0]

    # make a latex table
    table = pd.DataFrame({'Number of Years': [years],
                          'First Year': [min_year],
                           'Last Year': [max_year],
                          'Number of Counties': [counties],
                          'Total Observations': [obs]})

    # output table to latex
    table.style.hide(axis='index').to_latex(f'{root}output/tables/table1.tex',hrules=True)

    return None

## Table 2

def table2(df):

    # get solar, wind and other plants, mean, median, min, max, std for each year

    def helper(df, prefix):
        vars = [f'{prefix}_{x}' for x in ['solar','wind','other']]
        table = df.groupby(['year'])[vars].agg(['mean','median','sum']).reset_index()

        # round to first decimal place
        table = table.round(1)

        # output table to latex
        table.style.hide(axis='index') \
            .format(escape="latex")\
            .format(precision=1)\
            .to_latex(f'{root}output/tables/table2_{prefix}.tex',hrules=True)

    helper(df, 'n_plants')
    helper(df, 'capacity')

    return None

## Table 3

def table3(df):

    # by year, get difference between counties that have wind and those that don't
    # want difference in population, employment_total, avg_weekly_age_total, n_establishments_total,

    # create indicator variable for having wind
    df['has_wind'] = df['n_plants_wind'] > 0

    vars = ['population','employment_total','avg_wkly_wage_total','n_esttabs_total']

    def helper(df, vars, year):
        table = df.groupby(['year','has_wind'])[vars].agg(['mean']).reset_index()

        table = table[table['year'] == year]

        # transpose the table
        table = table.T

        table.columns = ['No Wind', 'Has Wind']

        return table

    for year in [2005,2010,2015]:

        table_year = helper(df, vars, year)
        table = pd.concat([table, table_year], axis=0)

    table = table.reset_index()

    # drop level_1
    table = table.drop(columns=['level_1'])

    # output table to latex
    table.style.hide(axis='index') \
        .format(escape="latex") \
        .format(precision=1) \
        .to_latex(f'{root}output/tables/table3.tex',hrules=True)

    return None


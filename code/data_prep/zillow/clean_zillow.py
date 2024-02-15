import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def clean_zillow():

    df = pd.read_csv(f'{root}data/zillow/County_zhvi_uc_sfr_tier_0.33_0.67_sm_sa_month.csv')

    df['fips'] = df['StateCodeFIPS'].astype(str).str.zfill(2) + df['MunicipalCodeFIPS'].astype(str).str.zfill(3)

    # reshape long
    df = df.melt(id_vars=['fips'], var_name='date', value_name='sf_housing_price')

    # keep the December values
    df = df[df['date'].str.contains('12-31')]
    df['year'] = df['date'].str[:4].astype(int)

    # check that there are no duplicates
    assert len(df) == len(df[['fips','year']].drop_duplicates())

    # drop date variable
    df = df.drop(columns=['date'])

    # output
    df.to_csv(f'{root}intermediates/zillow/zillow.csv', index=False)
    with open(f'{root}intermediates/zillow/zillow.pkl', 'wb') as f:
        pickle.dump(df, f)

    return None
#    colorscale =  [
#        'rgb(253, 232, 57)',
#        'rgb(195, 180, 106)',
#        'rgb(138, 133, 121)',
#        'rgb(59, 73, 108)',
#        'rgb(20, 52, 112)',
#        'rgb(0, 35, 78)',
#    ]



    # some counties are missing
#    fig = ff.create_choropleth(fips=list(df['area_fips']), values=list(df['2023-01-31']),
#                               colorscale=colorscale, binning_endpoints=[50000, 100000, 250000, 750000, 1000000])
#    fig.layout.template = None
#    fig.write_image(f'{root}output/zillow/housing_prices.pdf')

#    return df

def main():

    clean_zillow()

if __name__ == '__main__':
    main()
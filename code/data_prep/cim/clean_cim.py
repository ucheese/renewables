import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils


'''
NOTES:

- company names are not standard
- sometimes joint ventures are not labeled as such (ultium cells llc) is a joint venture but we can't ID it
- sometimes we have the name of the facility, but not the name of the company
- i didnt remove the cancelled ones, or filter on the investment status
- why are there investments that are duplicated?
- how do we get the actual investment?
- there are some nan's in company1
- how do we treat company groups
'''

def import_data():

    df = pd.read_csv(f'{root}data/clean_investment_monitor/facilities.csv',
                     header=3)

    return df

def import_keys(name):

    '''

    origin, name_map, rename

    '''

    df = pd.read_excel(f'{root}data/clean_investment_monitor/manual.xlsx',
                     sheet_name=name)
    return df

def clean_data():

    # read the data
    df = import_data()
    print(f'{len(df)} rows...')

    name_map = import_keys('name_map')
    rename = import_keys('rename')
    origin = import_keys('origin')

    # make column headers lowercase
    df.columns = [x.lower() for x in df.columns]

    df = clean_companies(df, rename, origin, name_map)

    # dates
    df['year'] = pd.to_datetime(df['announcement_date']).dt.year

    # merge to foreign or not
    origin['parent'] = origin['parent'].fillna(origin['company'])
    map_dict = dict(zip(origin.parent, origin.origin))
    for i in range(1,7):
        df[f'origin{i}'] = df[f'company{i}'].map(map_dict)

    # output
    df.to_csv(f'{root}intermediates/cim/facilities_clean.csv')

    return df


def clean_companies(df, rename, origin, name_map):

    # strip out the stuff in parens that is in [Siler City Solar 2, LLC (63749)]
    df['company'] = df['company'].apply(lambda x: re.sub(r'\([^)]*\)', '', x))

    # clean the company name
    df['company'] = df['company'].apply(lambda x: cleanco.basename(x))
    df['company'] = df['company'].str.strip()

    # map company name to new name
    map_dict = dict(zip(rename.company, rename.new_name))
    df['company'] = df['company'].replace(map_dict)

    # split into new columns, this is to identify partnerships and JV
    df[[f'company{i}' for i in range(1,7)]] = df['company'].str.split(',', expand=True)

    # strip the name
    for i in range(1,7):
        df[f'company{i}'] = df[f'company{i}'].str.strip()

    # map to name correction, or to parent

    map_dict = dict(zip(name_map.name, name_map.name_group))
    for i in range(1,7):
        df[f'company{i}'] = df[f'company{i}'].replace(map_dict)

    temp = origin[~pd.isnull(origin['parent'])]
    map_dict = dict(zip(temp.company, temp.parent))
    for i in range(1,7):
        df[f'company{i}'] = df[f'company{i}'].replace(map_dict)

    # create a list of companies and assign an ID
    companies = []
    for i in range(1,7):
        companies.extend(df[f'company{i}'].tolist())

    companies = set(companies)
    companies = pd.DataFrame(companies).reset_index(drop=True)
    companies.columns = ['company']
    companies = companies.sort_values(['company']).reset_index(drop=True)
    companies['company_id'] = companies.index
    companies = companies[~pd.isnull(companies['company'])]
    companies.to_csv(f'{root}intermediates/cim/companies.csv')

    # merge the ID to the original
    for i in range(1,7):
        df = df.merge(companies.rename(columns={'company_id':f'company_id{i}'}),
                      how='left',
                      right_on='company',
                      left_on=f'company{i}',
                      suffixes=('','_drop'))
        df = df.drop(columns={'company_drop'})

    return df

def main():

    df = clean_data()
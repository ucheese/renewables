import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils


def meta_data(folder_path):

    files = glob.glob(f'/{folder_path}/**/*.*', recursive=True)

    df = pd.DataFrame({'path':files})

    # keep only the text files
    df = df[df['path'].str.contains('txt')]

    # don't include the files from the earlier years
    df = df[~df['path'].str.contains('1967-2012')]

    # extract the file name
    df['file_name'] = df['path'].apply(lambda x: os.path.basename(x))

    # extract the year
    df['year'] = df['path'].str.extract(r'(20\d{2})')[0]

    # tag the file type
    df['type'] = ''
    df.loc[df['file_name'].str.contains('statetype'), 'type'] = 'state_type'
    df.loc[df['file_name'].str.contains('Fin_PID|Fin_GID'), 'type'] = 'id'
    df.loc[df['file_name'].str.contains('FinEstDAT'), 'type'] = 'dat'

    # the state type file is the state level data

    # get the variables from the excel files
    # for idx, row in df.iterrows():

    #    path = row['path']

    #    if row['type'] == 'id':
    #        temp = pd.read_csv(path, header=None, names=[0,'1','2'], sep=",,")
    #    elif row['type'] == 'dat':
    #        temp = pd.read_csv(path, header=None)

    #    df.loc[idx, 'vars'] = '##'.join(list(temp.columns))

    #explode the variable names into multiple words
    #df = df.assign(vars=df.vars.str.split('##')).explode('vars')

    # output
    df.to_csv(f'{root}intermediates/state_local/file_list_later_years.csv',index=False)

    return None


def import_data_master():

    file_list = pd.read_csv(f'{root}intermediates/state_local/file_list_later_years.csv')

    df = pd.DataFrame()

    # loop through the years and read the files
    for y in range(2012, 2021+1):

        print(y)
        select = file_list[file_list['year'] == y]

        assert(len(select) == 3)

        # get paths
        key_path = select[select['type'] == 'id']['path'].values[0]
        df_path = select[select['type'] == 'dat']['path'].values[0]

        temp = clean_data(df_path, key_path, y)

        df = pd.concat([df, temp], axis=0)

    # output a list of the item_codes
    codes = df.groupby(['item_code']).agg({'unit_id':lambda x: pd.Series.count(x)}).reset_index()

    codes.to_csv(f'{root}intermediates/state_local/item_codes.csv', index=False)

    # reshape
    wide = df.pivot(index=['fips','year','county_name'], columns='item_code', values='value').reset_index()

    return wide

def calc_variables(df):

    # taxes
    df['property_tax'] = df['T01']
    vars = [x for x in df.columns if x[0] == "T"]
    df['total_taxes'] = df[vars].sum(min_count=0, axis=1)

    # total revenue
    vars = [x for x in df.columns if x[0] in ['A','B','C','D','U','T']]
    vars = vars + ['X01','X05','X08']
    df['total_rev'] = df[vars].sum(min_count=0, axis=1)

    # total own source revenue
    vars = [x for x in df.columns if x[0] in ['A','U','T']]
    vars = vars + ['X01','X05','X08']
    df['total_rev_own_sources'] = df[vars].sum(min_count=0, axis=1)

    # total charges
    vars = [x for x in df.columns if x[0] in ['A']]
    df['gen_charges'] = df[vars].sum(min_count=0, axis=1)

    # total expenditures
    vars = [x for x in df.columns if x[0] in ['E','F','G','L','M','Q','I']]
    vars = vars + ['X11','X12']
    df['total_exp'] = df[vars].sum(min_count=0, axis=1)

    # keep relevant variables
    vars = ['fips','county_name','year','property_tax','total_taxes','total_rev','total_rev_own_sources','gen_charges',
            'total_exp']
    df = df[vars]

    # fill nas with 0
    df = df.fillna(0)

    # output as pickle
    df.to_pickle(f'{root}intermediates/state_local/state_local_post-2012.pkl')

    #test = pd.read_pickle(f'{root}intermediates/state_local/state_local_pre-2013.pkl')

    return None

def import_data(df_path, key_path):

    df = pd.read_csv(df_path, header=None)
    key = pd.read_csv(key_path, header=None,
                      names=[0,'1','2'], sep=",,")

    return df, key


def clean_data(df_path, key_path, year):

    df, key = import_data(df_path, key_path)

    if year < 2017:
    # clean the key, the key is for the entity

        key['unit_id'] = key[0].str[:14]
        key['id_name'] = key[0].str[17:78].str.strip()
        key['county_name'] = key[0].str[78:113].str.strip()
        key['fips_state'] = key[0].str[113:115]
        key['fips_county'] = key[0].str[115:118]

        # unit id is unique identifier in key
        assert(len(key) == len(key['unit_id'].unique()))

        #df['fips_state'] = df[0].str[0:2]
        df['type'] = df[0].str[2:3]
        #df['fips_county'] = df[0].str[3:6]
        # technically, this goes to 14, but I want the unit id to be 6 long
        df['unit_id'] = df[0].str[0:14]
        df['item_code'] = df[0].str[14:17]
        df['flag'] = df[0].str[-1:]
        df['year'] = df[0].str[-5:-1]
        df['value'] = df[0].str[-15:-5]

    elif year >= 2017:

        key['fips_state'] = key[0].str[0:2]
        #key['id_type'] = key[0].str[2:3]
        key['fips_county'] = key[0].str[3:6]
        key['unit_id'] = key[0].str[6:12]
        key['id_name'] = key[0].str[14:75].str.strip()
        key['county_name'] = key[0].str[75:110].str.strip()

        # unit id is unique identifier in key
        assert(len(key) == len(key['unit_id'].unique()))

        #df['fips_state'] = df[0].str[0:2]
        df['type'] = df[0].str[2:3]
        #df['fips_county'] = df[0].str[3:6]
        #df['unit_id'] = df[0].str[0:12]
        df['unit_id'] = df[0].str[6:12]
        df['item_code'] = df[0].str[12:15]
        df['flag'] = df[0].str[-1:]
        df['year'] = df[0].str[-5:-1]
        df['value'] = df[0].str[-16:-5]

    # merge key onto data
    df = df.merge(key[['unit_id','fips_county', 'county_name','fips_state']], how='left', on='unit_id')

    #keep county level data
    #df = df[df['id_name'].str[-6:] == 'COUNTY']
    df = df[df['type']=='1']

    # I don't want imputed data
    # df = df[df['flag'] == 'R']

    df['fips'] = df['fips_state'] + df['fips_county']

    # get duplicated fips and item code
    #temp = df[df.duplicated(subset=['fips','item_code'], keep=False)]

    assert(len(df) == len(df[['fips','item_code']].drop_duplicates()))

    # data is in thousands, covert to millions
    df['value'] = df['value'].astype(int)/1000

    # convert year to int
    df['year'] = df['year'].astype(int)

    return df


def main():

    meta_data(f'{root}data/state_local/')
    df = import_data_master()
    calc_variables(df)



if __name__ == 'main':

    main()

    # Okay so to get the same variables as the previous data I need to add stuff together

#    colorscale = [
#        'rgb(253, 232, 57)',
#        'rgb(195, 180, 106)',
#        'rgb(138, 133, 121)',
#        'rgb(59, 73, 108)',
#        'rgb(20, 52, 112)',
#        'rgb(0, 35, 78)',
#    ]

#    # some counties are missing
#    fig = ff.create_choropleth(fips=list(df['area_fips']), values=list(df['value']),
#                               colorscale=colorscale, binning_endpoints=[0.1, 1, 5, 10, 100])
#    fig.layout.template = None
#    fig.write_image(f'{root}output/state_local/property_tax.pdf')


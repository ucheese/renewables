import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

userkey = {"user_key":"4d08268476de052b9d2615a670874c6a"}


def import_data(name):

    df = pd.read_csv(f'{root}data/crunchbase/bulk_export/{name}.csv')

    return df

def create_database():

    files = glob.glob(f'{root}data/crunchbase/bulk_export/*.csv')
    file_names = [os.path.basename(x).split('.')[0] for x in files]

    for type in file_names:

        print(type)
        df = import_data(type)
        conn = sqlite3.connect(f'{root}data/crunchbase/sql/crunchbase.db')
        df.to_sql(type, conn, if_exists='replace')

    print('SQL database populated')

    return None

def query_cb(query):

    conn = sqlite3.connect(f'{root}data/crunchbase/sql/crunchbase.db')
    df = pd.read_sql(query, conn)

    print('query successful')

    return df


def get_green_firms():

    # get all the categories of organizations

    categories = query_cb('SELECT DISTINCT category_list FROM organizations')
    split_categories = categories['category_list'].str.split(',').explode()
    unique_categories = split_categories.unique()


    categories = query_cb('SELECT DISTINCT category_groups_list FROM organizations')
    split_categories = categories['category_groups_list'].str.split(',').explode()
    unique_categories = split_categories.unique()

    relevant = ['Energy',\
                'AgTech',\
                'CleanTech',\
                'Water',\
                'Environmental Engineering',\
                'GreenTech',\
                'Farming',\
                'Agriculture',\
                'Clean Energy Solar',\
                'Oil and Gas',\
                'Renewable Energy',\
                'Energy Storage',\
                'Electric Vehicle',\
                'Wind Energy',\
                'Fossil Fuels',\
                'Fuel',\
                'Forestry',\
                'Fuel Cell']

    relevant = ['Sustainability']

    #Automatovie is not a good one
    query_conditions = " OR ".join([f"category_groups_list LIKE '%{s}%'" for s in relevant])
    query = f"SELECT * FROM organizations WHERE {query_conditions};"

    organizations = query_cb(query)
    organizations = organizations[organizations['primary_role'] == 'company']

    # search for key words in non sustainability stuff


    # clean energy startups over time in terms of number by founding date

    # how do they exit

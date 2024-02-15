import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils


def read_files():

    # read file
    df = pd.read_csv(f'{root}/data/eere/capacity_height_diameter.csv')

    # rename columns
    df = df.rename(columns={'\'98−99': '1998', '\'00−01': '2000', '\'02−03': '2002', '\'04−05':'2004'})

    # add var names
    df = df.rename(columns = {'Unnamed: 0':'variable'})
    df['variable'] = ['capacity', 'diameter','height']

    # flip dims of dataframe
    df = df.T
    df.columns = df.iloc[0]
    df = df.iloc[1:]

    # fill index so that the years are continguous
    df = df.reset_index().rename(columns={'index':'year'})
    df['year'] = df['year'].astype(int)
    df = df.set_index('year')
    df = df.reindex(range(1998,2022+1))

    # fill forward the missing values
    df = df.fillna(method='ffill')

    # output as pickle and csv
    with open(f'{root}/intermediates/eere/capacity_height_diameter.pkl', 'wb') as f:
        pickle.dump(df, f)
    df.to_csv(f'{root}/intermediates/eere/capacity_height_diameter.csv')

    return None

def main():

    read_files()

if __name__ == '__main__':
    main()
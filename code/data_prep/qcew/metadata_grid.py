import pandas as pd
import glob


def metadata(folder_path):

    root = '/user/yz3937/Documents/Thesis/'

    files = glob.glob(f'/{folder_path}/**/*.*', recursive=True)

    df = pd.DataFrame({'path':files})

    # remove the zip files
    df = df[~df['path'].str.contains('zip')]

    # remove temp files
    df = df[~df['path'].str.contains('~')]

    # keep only csv
    df = df[df['path'].str.contains('csv')]

    # extract the file name
    df['file_name'] = df['path'].apply(lambda x: os.path.basename(x))

    # extract the year
    df['year'] = df['path'].str.extract(r'((20|19)\d{2})')[0]

    # tag the form type
    df['temp'] = df['file_name'].replace('^(19|20)\d{2}\.q1-q4', '', regex=True)
    df['temp'] = df['temp'].replace('^(19|20)\d{2}\.q1-q1', '', regex=True)
    df['naics'] = df['temp'].str.split(' ').str[1].str.strip()

    df['naics_des'] = df['temp'].str.extract(r'\d+ ([;\-\'\(\)\s\.,a-zA-Z]*?)\.csv$')

    # extract the immediate folder the file is in
    df['folder'] = df['path'].apply(lambda x: os.path.basename(os.path.dirname(x)))

    # output
    df.to_csv(f'{root}intermediates/qcew/file_list.csv',index=False)



def main():

    metadata(f'{root}data/qcew/')


if __name__ == '__main__':

    main()
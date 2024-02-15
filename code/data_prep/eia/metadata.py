import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def get_files(folder_path):

    # Generate dataframe with all files in the eia folder
    # the columns are the path, the folder name, the file name, and the sheet name

    files = glob.glob(f'/{folder_path}/**/*.*', recursive=True)

    df = pd.DataFrame({'path':files})

    # remove the zip files
    df = df[~df['path'].str.contains('zip')]

    # remove temp files
    df = df[~df['path'].str.contains('~')]

    # extract the file name
    df['file_name'] = df['path'].apply(lambda x: os.path.basename(x))

    # extract the year
    df['year'] = df['path'].str.extract(r'((20|19)\d{2})')[0]

    # tag the form type
    df['form_type'] = np.where(df['path'].str.contains('eia860a') , 'a', 'all')
    df['form_type'] = np.where(df['path'].str.contains('eia860b') , 'b', df['form_type'])

    # extract the immediate folder the file is in
    df['folder'] = df['path'].apply(lambda x: os.path.basename(os.path.dirname(x)))

    # for excel files, extract all sheet names, using a loop
    # append all sheet names as an extra row in the dataframe

    for idx, row in df.iterrows():

        file = row['file_name']
        file_path = row['path']

        if file.endswith(('.xls', '.xlsx')):
            # Read the Excel file to get sheet names
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names

            df.loc[idx, 'sheetname'] = '##'.join(sheet_names)

    # explode the sheet names into multiple rows
    df = df.assign(sheetname=df.sheetname.str.split('##')).explode('sheetname')

    # sort
    df = df.sort_values(['year','form_type'])

    # write to folder
    df.to_csv(f'{root}intermediates/eia/file_list.csv',index=False)

    return None


def get_variables():

    # read in annotated file list
    df = pd.read_csv(f'{root}intermediates/eia/file_list_annotated.csv')

    # only keep plant and generator stuff for now
    df = df[df['type'].isin(['plant','generator','existing_generator'])]

    # get the variables from the excel files
    for idx, row in df.iterrows():

        path = row['path']

        if row['year'] >= 2011:
            temp = pd.read_excel(path, sheet_name=row['sheetname'], header=1)
        else:
            temp = pd.read_excel(path, sheet_name=row['sheetname'], header=0)

        df.loc[idx, 'vars'] = '##'.join(list(temp.columns))

    #explode the variable names into multiple words
    df = df.assign(vars=df.vars.str.split('##')).explode('vars')

    # output
    df.to_csv(f'{root}intermediates/eia/variable_list.csv',index=False)


def main():

    folder_path = f'{root}data/eia/'
    get_files(folder_path)
    get_variables()


if __name__ == '__main__':

    main()
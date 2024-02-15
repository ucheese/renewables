import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def read_data():

    with open(f'{root}intermediates/global_atlas/wind.pkl', 'rb') as f:
        df = pickle.load(f)

    return df


def plot_map(df, height):

    # select the height
    temp = df[df['speed'] == height]

    colorscale = [
        'rgb(253, 232, 57)',
        'rgb(195, 180, 106)',
        'rgb(138, 133, 121)',
        'rgb(59, 73, 108)',
        'rgb(20, 52, 112)',
        'rgb(0, 35, 78)',
    ]

    fig = ff.create_choropleth(fips=list(temp['fips']), values=list(temp['mean']),
                               colorscale=colorscale, binning_endpoints=[1,3,5,7,9],
                               title=f'{height} m: mean', legend_title= 'Mean Wind Speed')
    fig.layout.template = None
    fig.write_image(f'{root}output/global_atlas/{height}_mean.pdf')

    fig = ff.create_choropleth(fips=list(temp['fips']), values=list(temp['max']),
                               colorscale=colorscale, binning_endpoints=[1,3,5,7,9],
                               title=f'{height} m: max', legend_title= 'Max Wind Speed')
    fig.layout.template = None
    fig.write_image(f'{root}output/global_atlas/{height}_max.pdf')

    return None


def plot_map_master(df):


    for height in [50, 100, 150]:

        plot_map(df, height)


def main():




if __name__ == '__main__':
    main()
import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils


def plot_sampled_points():

    # save the sampled points
    with open(f'{root}intermediates/solar/sampled_points.pkl', 'rb') as f:
        all_sample = pickle.load(f)

    # plot all the sampled points on map of US
    us_map = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    all_points = [point for points_list in all_samples.values() for point in points_list]
    points_gdf = gpd.GeoDataFrame(geometry=all_points)

    # Plotting
    fig, ax = plt.subplots(figsize=(15, 10))

    # Plot the US map
    us_map.plot(ax=ax, color='lightgrey')

    # Plot the points
    points_gdf.plot(ax=ax, color='red', markersize=5)

    plt.title('Sampled Points Across US Counties')
    plt.show()

    return None

def plot_tracking_potential():

    # read the master file
    with open(f'{root}intermediates/master/master.pkl', 'rb') as f:
        df = pickle.load(f)

    temp = df.dropna(subset=['tracking_potential'])
    temp = temp[temp['year']==2015]

    colorscale = [
        'rgb(253, 232, 57)',
        'rgb(195, 180, 106)',
        'rgb(138, 133, 121)',
        'rgb(59, 73, 108)',
        'rgb(20, 52, 112)',
        'rgb(0, 35, 78)',
    ]

    fig = ff.create_choropleth(fips=list(temp['fips']), values=list(temp['tracking_potential']),
                               colorscale=colorscale, binning_endpoints=[50,100,150,200,250],
                               title=f'Tracking Potential', legend_title= 'Tracking Potential IRR/Dollar')
    fig.layout.template = None
    fig.write_image(f'{root}output/solar/tracking_potential.pdf')

import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

# make maps by year of where stuff is located

def read_data():

    with open(f'{root}intermediates/eia/eia.pkl', 'rb') as f:
        df = pickle.load(f)

    return df


def plot_totals():

    df = read_data()

    col         = 'prime_mover'
    conditions  = [ df[col] == 'photovoltaic',\
                    df[col] == 'onshore wind' ]
    choices     = [ 'solar', 'wind' ]

    df['tech'] = np.select(conditions, choices, default='other')

    # keep operating plants
    df = df[df['status'] == 'operating']


    # plot total number of generators, plants, capacity over time (solar, wind, other)

    # total number of generators
    temp = df.groupby(['year','tech'])['id'].count().reset_index()
    temp = temp.pivot(index='year', columns='tech', values='id')
    temp.plot()
    plt.ylabel('# of Generators')
    plt.title('Number of Generators in the US')
    plt.savefig(f'{root}output/eia/ts_n_generators.pdf', bbox_inches='tight')
    plt.clf()

    # total number of plants
    temp = df.groupby(['year','tech'])['plant_code'].nunique().reset_index()
    temp = temp.pivot(index='year', columns='tech', values='plant_code')
    temp.plot()
    plt.ylabel('# of Plants')
    plt.title('Number of Plants in the US')
    plt.savefig(f'{root}output/eia/ts_n_plants.pdf', bbox_inches='tight')
    plt.clf()

    # total capacity
    temp = df.groupby(['year','tech'])['capacity'].sum().reset_index()
    temp = temp.pivot(index='year', columns='tech', values='capacity')
    temp.plot()
    plt.ylabel('Capacity (MW)')
    plt.title('Total Capacity in the US')
    plt.savefig(f'{root}output/eia/ts_capacity.pdf', bbox_inches='tight')


    return None

def plot_map(df, tech, year):

    # keep anything with capacity of >= 1 MW
    df = df[df['capacity'] >= 1]

    df = df[df['year'] == year]

    # group by county (fips) and tech, get number of plants, number of generators, and sum of capacity
    temp = df.groupby(['fips', 'tech'])['plant_code'].nunique().reset_index()
    temp = temp.rename(columns={'plant_code':'n_plants'})
    temp = temp.merge(df.groupby(['fips', 'tech'])['id'].count().reset_index().rename(columns={'id':'n_generators'}),
                      how='left', on=['fips', 'tech'])
    temp = temp.merge(df.groupby(['fips', 'tech'])['capacity'].sum().reset_index().rename(columns={
        'capacity':'capacity'}), how='left', on=['fips', 'tech'])

    colorscale = [
        'rgb(253, 232, 57)',
        'rgb(195, 180, 106)',
        'rgb(138, 133, 121)',
        'rgb(59, 73, 108)',
        'rgb(20, 52, 112)',
        'rgb(0, 35, 78)',
    ]


    temp = temp[temp['tech'] == tech]
    temp = temp[temp['fips'] != 'None Found']

    # some counties are missing
    fig = ff.create_choropleth(fips=list(temp['fips']), values=list(temp['n_plants']),
                               colorscale=colorscale, binning_endpoints=[1,5,10,15,20],
                               title=f'{tech}: {year}', legend_title= 'Number of Plants')
    fig.layout.template = None
    fig.write_image(f'{root}output/eia/{tech}_{year}_plants.pdf')


    fig = ff.create_choropleth(fips=list(temp['fips']), values=list(temp['capacity']),
                               colorscale=colorscale, binning_endpoints=[1,100, 500, 1000, 5000],
                               title=f'{tech}: {year}', legend_title= 'Capacity (MW)')
    fig.layout.template = None
    fig.write_image(f'{root}output/eia/{tech}_{year}_capacity.pdf')

    return None


def plot_map_master(df):


    for tech in ['solar', 'wind', 'other']:

        # first, do individual plots by year
        for y in range(2001, 2022+1):
            plot_map(df, tech, y)


        for type in ['plants', 'capacity']:
            # next, combine the annual plots into one pdf
            pdfs = [f'{tech}_{y}_{type}.pdf' for y in range(2001, 2022+1)]

            merger = PdfMerger()

            for pdf in pdfs:
                merger.append(f'{root}/output/eia/{pdf}')
                os.remove(f'{root}/output/eia/{pdf}')

            merger.write(f'{root}/output/eia/{tech}_{type}.pdf')
            merger.close()

def plot_gen(gen):

    # plot of all energy production in the US
    temp = gen.groupby(['technology'])['capacity'].sum()
    temp.plot.pie(y='capacity', figsize=(5, 5), autopct='%.0f%%')
    plt.ylabel('')
    plt.title('Electricity Generation in the US, 2022')
    plt.savefig(f'{root}output/eia/energy_US.pdf', bbox_inches='tight')
    plt.clf()

    # plot new
    gen = gen[gen['oper_year'] == 2022]
    temp = gen.groupby(['technology'])['capacity'].sum()
    temp.plot.pie(y='capacity', figsize=(5, 5), autopct='%.0f%%')
    plt.ylabel('')
    plt.title('Electricity Generation in the US, New Operations in 2022')
    plt.savefig(f'{root}output/eia/energy_US_2022.pdf', bbox_inches='tight')
    plt.clf()

    return None

def merge():

    solar = clean_solar()
    wind = clean_wind()
    plant = clean_plant()

    # solar
    df = solar.merge(plant, how='left', on='plant_code')
    #df = pd.read_csv("Long_Lats.csv", delimiter=',', skiprows=0, low_memory=False)

    import plotly.graph_objects as go
    fig = go.Figure(data=go.Scattergeo(
        lon = df['lon'],
        lat = df['lat'],
        mode = 'markers',
        marker=dict(
            color='MediumPurple',
            size=3
        )
    ))

    fig.update_layout(
        geo_scope='usa',
    )
    fig.write_image(f'{root}output/eia/solar.pdf')

    # wind
    df = wind.merge(plant, how='left', on='plant_code')
    fig = go.Figure(data=go.Scattergeo(
        lon = df['lon'],
        lat = df['lat'],
        mode = 'markers',
        marker=dict(
            color='Blue',
            size=3
        )
    ))

    fig.update_layout(
        geo_scope='usa',
    )
    fig.write_image(f'{root}output/eia/wind.pdf')

def main():




if __name__ == '__main__':
    main()
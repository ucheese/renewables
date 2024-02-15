import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def import_data():

    df = pd.read_csv(f'{root}intermediates/cim/facilities_clean.csv',
                        index_col=0)

    return df

def graphs():

    df = import_data()

    # convert investment to billions
    df['investment_estimated'] = df['investment_estimated']/1000


    # Number and $$ of investments by category and subcategory, cut by investment type and investment status
    # split by segment, manufacturing

    for var in ['technology','subcategory']:
        for cat in ['Manufacturing','Energy and Industry']:

            data = df
            data = data[data['segment'] == cat]
            data = df.groupby(var).agg({'investment_estimated': ['sum', 'count']}).reset_index()
            data = data.sort_values(('investment_estimated','sum'))
            if var == 'subcategory':
                fig, axs = plt.subplots(1,2, figsize=(8, 20))
            elif var == 'technology':
                fig, axs = plt.subplots(1,2)
            axs[0].barh(data[(var,'')],data[('investment_estimated','sum')])
            axs[0].set_title('$ Billions')
            axs[1].barh(data[(var,'')],data[('investment_estimated','count')])
            axs[1].set_title('# of Facilities')
            axs[1].set_yticks([])
            plt.savefig(f'{root}output/cim/{var}_{cat}.pdf', bbox_inches='tight')


    # Same as above but over time

    for var in ['technology']:
        for cat in ['Manufacturing','Energy and Industry']:

            data = df
            data = data[data['segment'] == cat]
            data = data.groupby([var,'year']).agg({'investment_estimated': ['sum', 'count']}).reset_index()
            categories = data[var].unique()
            fig, axs = plt.subplots(len(categories), sharey=True,sharex=True, figsize=(5, 20))

            for i in range(len(categories)):
                data_subset = data[data[var] == categories[i]]
                axs[i].plot(data_subset['year'],data_subset[('investment_estimated','sum')])
                axs[i].set_title(categories[i])
                axs[i].set_ylabel('$ Billions')

            plt.savefig(f'{root}output/cim/{var}_{cat}_ts.pdf', bbox_inches='tight')


    # Top states invested in, and for top states what they are invested in
    var = 'state'
    data = df.groupby([var]).agg({'investment_estimated': ['sum', 'count']}).reset_index()
    data = data.sort_values(('investment_estimated','sum'))
    data = data.iloc[-20:]
    states_to_keep = data['state']
    fig, axs = plt.subplots(1, 2)
    axs[0].barh(data[(var,'')],data[('investment_estimated','sum')])
    axs[0].set_xlabel('$ Billions')
    axs[1].barh(data[(var,'')],data[('investment_estimated','count')])
    axs[1].set_yticks([])
    axs[1].set_xlabel('# of Facilities')
    plt.savefig(f'{root}output/cim/state_ts.pdf', bbox_inches='tight')

    # by technology
    var = 'state'
    var2 = 'technology'
    data = df.groupby([var, var2]).agg({'investment_estimated': ['sum', 'count']}).reset_index()
    data = data[data['state'].isin(states_to_keep)]
    fig, axs = plt.subplots(1, 1)
    #plt.set_cmap('tab20')
    categories = df[var2].unique()
    #cum = pd.DataFrame(states_to_keep)
    #cum.loc[:,'cum_value'] = 0
    data.columns = [' '.join(col).strip() for col in data.columns.values]
    cum = data.groupby('state').sum().reset_index()
    cum.columns = ['state', 'cum_value', 'cum_count']

    for i in range(len(categories)):

        data_subset = data[data[var2] == categories[i]]
        #data_subset.columns = [' '.join(col).strip() for col in data_subset.columns.values]

        if i >= 10:
            hatch = '+++'
        else:
            hatch = ''
        axs.barh(cum['state'],cum['cum_value'], label=categories[i],
                 hatch=hatch)
        axs.set_xlabel('$ Billions')
        axs.legend(loc='upper center', bbox_to_anchor=(-0.5, 1))

        cum = cum.merge(data_subset[['state','investment_estimated sum']], how='left', left_on='state',
                            right_on='state')
        cum['cum_value'] = cum['cum_value'] -  cum['investment_estimated sum'].fillna(0)
        cum = cum.drop(columns=['investment_estimated sum'])

    plt.savefig(f'{root}output/cim/state_technology_ts.pdf', bbox_inches='tight')

    # Top companies invested
    var = 'value'
    data = df
    data = pd.melt(data, id_vars=['unique_id','investment_estimated'], value_vars=[f'company{i}' for i in range(1,7)])

    data = data.groupby([var]).agg({'investment_estimated': ['sum', 'count']}).reset_index()
    data = data.sort_values(('investment_estimated','sum'))
    data = data.iloc[-20:]
    fig, axs = plt.subplots(1, 2)
    axs[0].barh(data[(var,'')],data[('investment_estimated','sum')])
    axs[0].set_xlabel('$ Billions')
    axs[1].barh(data[(var,'')],data[('investment_estimated','count')])
    axs[1].set_yticks([])
    axs[1].set_xlabel('# of Facilities')
    plt.savefig(f'{root}output/cim/firm.pdf', bbox_inches='tight')

    # List of all partnerships, and partnership status
    df['n_companies'] = df[[f'company{i}' for i in range(1,7)]].notna().sum(axis=1)
    data = df
    data = data[data['n_companies'] > 1]
    for i in range(1,7):
        data[f'company{i}'] = data[f'company{i}'] + ' (' + data[f'origin{i}'].fillna('') + ')'
    data['companies'] = data[[f'company{i}' for i in range(1,7)]].\
        apply(lambda row: '|'.join([val for val in row if pd.notna(val)]), axis=1)
    var = 'companies'
    data = data.groupby([var]).agg({'investment_estimated': ['sum', 'count']}).reset_index()
    data = data.sort_values(('investment_estimated','sum'))
    data = data.iloc[-20:]
    fig, axs = plt.subplots(1, 2)
    axs[0].barh(data[(var,'')],data[('investment_estimated','sum')])
    axs[0].set_xlabel('$ Billions')
    axs[1].barh(data[(var,'')],data[('investment_estimated','count')])
    axs[1].set_yticks([])
    axs[1].set_xlabel('# of Facilities')
    plt.savefig(f'{root}output/cim/firm_partnerships.pdf', bbox_inches='tight')

    # Other companies that were not in a partnership
    partnership = []
    all_companies = []
    data = df[df['n_companies'] > 1]
    for i in range(1,7):
        partnership.extend(data[f'company{i}'].tolist())
        all_companies.extend(df[f'company{i}'].tolist())

    stand_alone = set(all_companies).difference(partnership)

    data = df[df['company1'].isin(stand_alone)]

    i=1
    var='company1'
    data[f'company{i}'] = data[f'company{i}'] + ' (' + data[f'origin{i}'].fillna('') + ')'
    data = data.groupby([f'company{i}']).agg({'investment_estimated': ['sum', 'count']}).reset_index()
    data = data.sort_values(('investment_estimated','sum'))
    data = data.iloc[-30:]
    fig, axs = plt.subplots(1, 2)
    axs[0].barh(data[(var,'')],data[('investment_estimated','sum')])
    axs[0].set_xlabel('$ Billions')
    axs[1].barh(data[(var,'')],data[('investment_estimated','count')])
    axs[1].set_yticks([])
    axs[1].set_xlabel('# of Facilities')
    plt.savefig(f'{root}output/cim/firm_standalone.pdf', bbox_inches='tight')


def groups():

    '''

    get the treament and control

    '''

def foreign_domestic():

    '''

    ID if foreign or domestic

    '''

def standardize_names():

    '''


    '''

# maybe I just take the biggest investment

def main():


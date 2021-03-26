from requests import Session
from bs4 import BeautifulSoup
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

website = 'https://www.faa.gov/data_research/commercial_space_data/launches/'


def date_to_year(entry):
    entry['Date'] = entry['Date'].year
    return entry


def make_plot(name, label, allv: pd.DataFrame, min=0):
    years = allv['Date'].unique()
    years.sort()
    years = years[:-1]
    df = allv.loc[allv[label] == name][[label, 'Date']].groupby('Date').count()
    l = np.zeros_like(years)
    for i in range(years.shape[0]):
        year = years[i]
        if year not in df[label]:
            pass
        else:
            l[i] = df[label].loc[year]
    if l.sum() > min:
        plt.plot(years, l, label=name)


def fill_under_all(label, allv):
    years = allv['Date'].unique()
    years.sort()
    years = years[:-1]
    df = allv[[label, 'Date']].groupby('Date').count()
    l = np.zeros_like(years)
    for i in range(years.shape[0]):
        year = years[i]
        if year in df[label]:
            l[i] = df[label].loc[year]
    plt.fill_between(years, l, color='lightgray', label='all')


def merge_rocket_families(df: pd.DataFrame):
    families = [
        'Atlas',
        'Delta'
    ]
    for fam in families:
        tdf = pd.DataFrame()
        print(df[df.Vehicle.str.startswith(fam)])
        for idx, value in df[df.Vehicle.str.startswith(fam)].iterrows():
            print(value)
            df = df.drop(index=idx)
            value['Vehicle'] = fam
            tdf = tdf.append(value, ignore_index=True)
        df = df.append(tdf, ignore_index=True)
    return df


if __name__ == "__main__":
    with Session() as s:
        site = s.get(website)
        bs = BeautifulSoup(site.content, 'lxml')

        table = bs.find(id='spaceTable')
        # print(table)
        [x.decompose() for x in table.find_all('span')]

        df = pd.read_html(str(table), parse_dates=['Date'])[0]

    ndf = df.apply(date_to_year, 1)[['Date', 'Company', 'Vehicle']]
    ndf = merge_rocket_families(ndf)
    # print(ndf)

    # by_vehicle = ndf.groupby(['Vehicle','Date']).count()
    # by_company = ndf.groupby(['Company','Date']).count()
    # print(by_vehicle)
    # print(by_company)

    plt.ylabel('Launches per Year')
    plt.xlabel('Year')
    fill_under_all('Company', ndf)
    for company in ndf['Company'].unique():
        make_plot(company, 'Company', ndf, 5)

    # ndf.groupby('Date').count()['Company'].plot(label='all',color='lightgray')
    plt.grid()
    plt.legend()
    plt.show()

    plt.ylabel('Launches per Year')
    plt.xlabel('Year')
    fill_under_all('Vehicle', ndf)
    for vehicle in ndf['Vehicle'].unique():
        make_plot(vehicle, 'Vehicle', ndf, 5)
    # ndf.groupby('Date').count()['Vehicle'].plot(label='all',color='lightgray')
    plt.grid()
    plt.legend()
    plt.show()

    fill_under_all('Company', ndf)
    plt.grid()
    plt.show()

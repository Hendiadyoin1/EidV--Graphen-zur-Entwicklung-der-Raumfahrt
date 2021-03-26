from requests import Session, get
from bs4 import BeautifulSoup
from pandas import DataFrame
from time import time
start = 2020  # 1957
end = 2025

base_url = 'https://nssdc.gsfc.nasa.gov'
tries = 3


def get_launch_site_vehicle_funder(s: Session, entry):
    t_start = time()
    link = base_url + entry.find('a').get('href')
    for _ in range(tries):
        try:
            site = s.get(link)
            break
        except KeyboardInterrupt:
            exit(1)
        except:
            print('retry')
            continue
    else:
        print(
            f'entry:{entry.find("a").text} timed out or closed the connection')
        exit(1)

    t_req = time()
    print('\x1b[2M', end='')
    print(f'\t\trequest: {t_req-t_start:.5}s')
    bs = BeautifulSoup(site.content, 'lxml')
    if bs.find('title').text == 'NASA - NSSDCA - Master Catalog - Errors and Messages':
        print('\x1b[1A', end='')
        print(
            f'''\t\tentry: '{entry.find("a").text}' failed to load''')
        return None, None, None
    side_panel = bs.find(class_='urtwo')
    container_head = side_panel.find('h2', text='Facts in Brief')
    paragraph = container_head.nextSibling
    # no clue why it does not want to use the text argument here
    strongs = paragraph.find_all('strong')
    vehicle_strong = strongs[1]
    site_strong = strongs[2]

    try:
        container_head = side_panel.find('h2', text='Funding Agency')
        funder = container_head.nextSibling.find('li').text
    except AttributeError as e:
        container_head = side_panel.find('h2', text='Funding Agencies')
        if not container_head:
            funder = 'unknown'
        else:
            funder = '; '.join(
                x.text for x in container_head.nextSibling.find_all('li'))

    vehicle = vehicle_strong.nextSibling
    site = site_strong.nextSibling
    t_end = time()
    print(f'\t\tentry: {t_end-t_start:.5}s')
    print('\x1b[2A\x1b[0G', end='')
    return site, vehicle, funder


with Session() as s:
    for i in range(start, end):
        print(i)
        t_start = time()
        req = s.post('https://nssdc.gsfc.nasa.gov/nmc/spacecraft/query',
                     data={
                         'name': "",
                         'discipline': "-1",
                         'launch': str(i)
                     })
        t_req = time()
        print(f'\trequest: {t_req-t_start:.5}s')

        bs = BeautifulSoup(req.text, 'lxml')
        table = bs.find('table')
        colls = [x.text.replace('\xa0', ' ')
                 for x in table.tr]+['Site', 'Vehicle', 'Funder']
        entries = table.find_all('tr')[1:]

        t_find = time()
        print(f'\tparse: {t_find-t_req:.5}s')
        print(f'\t\t{len(entries)} entries')
        # for entry in entries:
        # 	print('\t'.join(x.text for x in entry.find_all('td')))

        df = DataFrame(
            [[x.text for x in entry] +
                list(get_launch_site_vehicle_funder(s, entry)) for entry in entries],
            columns=colls
        )
        print('\x1b[2M', end='')
        t_df = time()
        print(f'\tdataframe: {t_df-t_find:.5}s')
        # drop all duplicates (multiple satelites per launch etc)
        # df = df.drop_duplicates(subset=['Launch Date','Site','Vehicle'])

        # print(df)
        df.to_csv(f'spaceCraftquerys/{i}.csv')
        t_write = time()
        print(f'\twrite: {t_write-t_df:.5}')
        print(f'\tall: {t_write-t_start:.5}s')

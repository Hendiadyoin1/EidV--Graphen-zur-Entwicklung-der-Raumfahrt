import glob
import os
import re

import matplotlib.pyplot as plt
import pandas as pd


def seek_header(file_obj):
    line = file_obj.readline()
    while True:
        if len(line.strip()) > 0 and line.strip().split()[0] == 'Vehicle':
            break
        line = file_obj.readline()
    while True:
        if len(line) > 0 and line[0] == '=':
            break
        line = file_obj.readline()

re_sep = re.compile(r" {2,}")
def split_line(line:str):
    line = re_sep.split(line)
    
    return line

def get_launch_data(parts):
    """
        ret: (attempts,failures)
    """
    parts = parts + ['---'] * max(5 - len(parts),0)
    ret = [parts[0]]
    for part in parts[1:]:
        if re.match(r'\d+\(\d+\)[ *$]*',part):
            attempts, failures = map(int,
                re.match(r'(\d+)\((\d+)\)[ *$]*', part).groups())
                
            ret.append(attempts)
            ret.append(failures)
        elif re.match(r'\d+\/\d+[ *$]*',part):
            successes, attempts = map(int, re.match(r'(\d+)\/(\d+)',part).groups())
            
            ret.append(successes)
            ret.append(attempts-successes)
        else:
            # line = "---" or is empty
            ret.append(0)
            ret.append(0)

    return ret

def parse_line(line):
    parts = split_line(line)
    ret = get_launch_data(parts)
    print(ret)
    return ret




def parse(file):
    print(file)
    index = ['Vehicle',
            'Launches',
             'Failures',
             'LEO',
             'LEO failures',
             '>LEO',
             '>LEO failures',
             'Deep',
             'Deep failures']
    df = pd.DataFrame(columns=index)
    with open(file) as f:
        seek_header(f)
        while (line := f.readline().strip())[0] not in '=-':
            blob = pd.Series(parse_line(line),index=index)
            df = df.append(blob, ignore_index=True)

    df.to_csv(file[:-3]+'csv')


if __name__ == '__main__':
    os.chdir('launch logs')
    for path in glob.glob('*.txt'):
        parse(path)
    # parse('1999.txt')

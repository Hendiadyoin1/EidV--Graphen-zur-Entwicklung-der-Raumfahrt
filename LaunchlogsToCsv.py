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


regex = re.compile(
    r"""^(?P<Vehicle>[^*$\n]*?)(?:[ *$])*(?P<AttemptsOrSuccess>\d+)(?:\((?P<Fails>\d+)\)|\/(?P<Attempts>\d+))(?:[ *$]+(?:(?P<LEO>\d+)|-+)(?:\((?P<LEOFails>\d+)\)|\/(?P<LEOAttempts>\d+)|)[ *$]+(?:(?P<grLEO>\d+)|)(?:(?:\((?P<grLEOFails>\d+)\)|\/(?P<grLEOAttempts>\d+)|)[ *$]+(?:(?:(?P<Deep>\d+)|-+)(?:\((?P<DeepFails>\d+)\)|\/(?P<DeepAttempts>\d+)|))?)?)?"""
)


def parse_line(line):
    match = regex.match(line)
    if match is None:
        return
    groups = match.groupdict()
    vehicle = groups['Vehicle']
    # all
    launches = int(match['Attempts']) if match['Attempts'] is not None \
        else int(match['AttemptsOrSuccess']) if match['AttemptsOrSuccess'] is not None \
        else 0
    fails = int(match['Attempts'])-int(match['AttemptsOrSuccess']) if match['Attempts'] is not None \
        else int(match['Fails']) if match['Fails'] is not None \
        else 0
    # to LEO
    LeoAttempts = int(match['LEOAttempts']) if match['LEOAttempts'] is not None \
        else int(match['LEO']) if match['LEO'] is not None \
        else 0
    LeoFails = int(match['LEOAttempts'])-int(match['LEO']) if match['LEOAttempts'] is not None \
        else int(match['LEOFails']) if match['LEOFails'] is not None \
        else 0
    # to >LEO
    grLeoAttempts = int(match['grLEOAttempts']) if match['grLEOAttempts'] is not None \
        else int(match['grLEO']) if match['grLEO'] is not None \
        else 0
    grLeoFails = int(match['grLEOAttempts'])-int(match['grLEO']) if match['grLEOAttempts'] is not None \
        else int(match['grLEOFails']) if match['grLEOFails'] is not None\
        else 0
    # to DeepSpace
    DeepAttempts = int(match['DeepAttempts']) if match['DeepAttempts'] is not None \
        else int(match['Deep']) if match['Deep'] is not None \
        else 0
    DeepFails = int(match['Deep'])-int(match['DeepAttempts']) if match['DeepAttempts'] is not None \
        else int(match['DeepFails']) if match['DeepFails'] is not None\
        else 0
    ret = {
        'Vehicle': vehicle,
        'Launches': launches,
        'Failures': fails,
        'LEO': LeoAttempts,
        'LEO failures': LeoFails,
        '>LEO': grLeoAttempts,
        '>LEO failures': grLeoFails,
        'Deep': DeepAttempts,
        'Deep failures': DeepFails
    }
    return ret


def parse(file):
    print(file)
    index = ['Launches',
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
        while (line := f.readline())[0] not in '=-':
            blob = parse_line(line)
            if blob:
                df = df.append(blob, ignore_index=True)

    df.to_csv(file[:-3]+'csv')


if __name__ == '__main__':
    os.chdir('launch logs')
    for path in glob.glob('*.txt'):
        parse(path)
    # parse('1999.txt')

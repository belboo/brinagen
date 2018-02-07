#!/usr/bin/python3

from __future__ import print_function
import sys
import os
import re
import json
import argparse
import signal
import shutil

from .tools import unique

def snp_dict_load(dict_path, verb=1):

    """ Read JSON dictionary from file. """

    if os.path.exists(dict_path):
        try:
            with open(dict_path, 'r') as dict_file:
                snp_dict = json.load(dict_file)
        except ValueError:
            if verb > 0:
                print('Error: Failed to read JSON from  [{}].'.format(dict_path), file=sys.stderr)
            raise
        except:
            if verb > 0:
                print('Error: Failed to load dictionary [{}].'.format(dict_path), file=sys.stderr)
            raise
    return snp_dict

def snp_dict_add(id_list, dict_path, mode='update', verb=1):

    """ Update a dictionary or create a new one. """

    if isinstance(id_list, str):
        id_list = [id_list]
    elif not isinstance(id_list, list):
        if verb > 0:
            print('Error: Cannot interpret ID list!', file=sys.stderr)
        raise ValueError('Dictionary update failed!')

    if mode == 'update':
        if os.path.exists(dict_path):
            snp_dict = snp_dict_load(dict_path)
            if not snp_dict:
                return None
                raise
        else:
            snp_dict = {}
            if verb > 0:
                print('Creating a new dictionary [{0}]...'.format(dict_path), file=sys.stderr)
    elif mode == 'new':
        snp_dict = {}
        if verb > 0:
            print('Warning: Dictionary [{0}] shall be overwritten!'.format(dict_path), file=sys.stderr)
    else:
        if verb > 0:
            print('Error: Invalid mode [{0}]!'.format(mode), file=sys.stderr)

    ds = [snp_id for snp_id in id_list if snp_id not in set(snp_dict)]

    if ds:
        ds = unique(ds)

        if snp_dict:
            max_id = max(v[0] for v in snp_dict.values())
        else:
            max_id = 0

        new_snp_dict = dict((e[0],(e[1], e[2])) for e in zip(ds, \
                            [max_id+1+i for i in range(len(ds))], \
                            ['SNP'+'%05d'%(max_id+1+i) for i in range(len(ds))]))
        snp_dict.update(new_snp_dict)

        if os.path.exists(dict_path):
            shutil.copyfile(dict_path, dict_path+'.bak')

        try:
            with open(dict_path, 'w') as f:
                json.dump(snp_dict, f)
        except TypeError:
            if verb > 0:
                print('Error: Unable to serialize the dictionary!', file=sys.stderr)
            raise
        except:
            if verb > 0:
                print('Error: Failed to write dictionary!', file=sys.stderr)
            raise

        return snp_dict

def snp_dict_lookup(id_list, dict_path, mode='ro', verb=1):

    """ Return SNP names corresponding to the list of IDs. """

    if isinstance(id_list, str):
        id_list = [id_list]
    elif not isinstance(id_list, list):
        if verb > 0:
            print('Error: Cannot interpret ID list!')

    if mode == 'new':
        snp_dict = {}
    else:
        snp_dict = snp_dict_load(dict_path)
        if not snp_dict:
            return Null

    ds = [snp_id for snp_id in id_list if snp_id not in set(snp_dict)]

    if ds:
        snp_dict = snp_dict_add(ds, dict_path, mode=mode, verb=verb)
        if not snp_dict:
            raise Exception('Dictionary update failed...')

    return [snp_dict[e][1] for e in id_list]

def snp_dict_list(dict_path, sort='n', fmt='t', verb=1):

    """ List entries in dictionary as formatted list. """

    fmt_set = set('tcINX0123456789<^>')

    snp_dict = snp_dict_load(dict_path)
    if not snp_dict:
        return

    if not set(sort).issubset('nir'):
        if verb > 0:
            print('Error: Wrong sorting key [{0}].'.format(sort), file=sys.stderr)
            return

    if 'i' in sort:
        sort_func = lambda snp_id: snp_id
    else:
        sort_func = lambda snp_id: snp_dict[snp_id][1]

    rev_sort = ('r' in sort)

    if fmt == 'col':
        fmt_str = '{snp_name:<20s} {snp_id:s}'
    elif fmt == 'csv':
        fmt_str = '{snp_name:s},{snp_id:s}'
    elif fmt == 'tab':
        fmt_str = '{snp_name:s}\t{snp_id:s}'
    else:
        fmt_groups = re.findall('([XIN])([<^>]?\d+)?', fmt)
        fmt_str = ''.join('{'+ g[0] + ':' + g[1] + 's}' for g in fmt_groups) \
                    .replace('X', 'n_id') \
                    .replace('I', 'snp_id') \
                    .replace('N', 'snp_name')
        if not fmt_str:
            if verb > 0:
                print('Error: Wrong format key [{0}]!'.format(fmt), file=sys.stderr)
            return

    print(snp_dict)
    for snp_id in sorted(snp_dict, key=sort_func, reverse=rev_sort):
        print(fmt_str.format(snp_id=snp_id, n_id=str(snp_dict[snp_id][0]), snp_name=snp_dict[snp_id][1]))

if __name__ == '__main__':
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    parser = argparse.ArgumentParser(description='SNP MusDictionary Tool')
    parser.add_argument('dict_path', metavar='DICTIONARY',
                        default = 'snpdict.json', nargs='?',
                        help='fragment ID dictionary file [snpdict.json]')
    parser.add_argument('-s', '--sort',
                        dest='sort', default='n',
                        help='sort by (i)d or (n)ame, possibly (r)eversed [name]')
    fmt_group = parser.add_mutually_exclusive_group()
    fmt_group.add_argument('-t', '--tab',
                        dest='fmt', action='store_const', const='tab', default='tab',
                        help='tab separated output')
    fmt_group.add_argument('-c', '--columns',
                        dest='fmt', action='store_const', const='col',
                        help='output in columns')
    fmt_group.add_argument('-csv', '--csv',
                        dest='fmt', action='store_const', const='csv',
                        help='csv output')
    fmt_group.add_argument('-f', '--fmt',
                        dest='custom_fmt',
                        metavar='FMT',
                        help='custom output format as FIELD[align][width]. Fields: X (nid), N (name), I (ID)')
    parser.add_argument('-v', '--verbosity', action='count',
                        dest='verbosity', default=0,
                        help='increase output verbosity')

    args = parser.parse_args()

    dict_path = args.dict_path
    sort = args.sort
    verbosity = args.verbosity

    if args.custom_fmt:
        fmt = args.custom_fmt
    else:
        fmt = args.fmt

    snp_dict_list(dict_path, sort=sort, fmt=fmt, verb=verbosity)

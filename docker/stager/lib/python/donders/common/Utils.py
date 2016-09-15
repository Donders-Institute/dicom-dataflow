#!/usr/bin/env python

import sys
import re 
import getpass 
import textwrap 
import pwd
from terminaltables import SingleTable

def userExist(username):
    '''check if given user name is existing as a system user id'''
    ick = False
    try:
        pwd.getpwnam(username)
        ick = True
    except KeyError,e:
        pass
    return ick

def inputPassword(prompt="password"):

    ## flush any output before prompting for password 
    sys.stdout.write('\n')
    sys.stdout.flush()
    ## try ask for password from the interactive shell
    if sys.stdin.isatty(): ## for interactive password typing
        passwd = getpass.getpass( prompt + ': ')
    else: ## for pipeing-in password
        passwd = sys.stdin.readline().rstrip()

    return passwd

def sizeof_fmt(num, suffix='B'):
    """
    convert bytes into human-readable format
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1000.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1000.0
    return "%.1f%s%s" % (num, 'Y', suffix)

def makeAttributeValueTable(title, data, attrs_to_show=[]):
    """ make a table for attribute-value pairs of a JSON object
    """

    def __show_value__(v):

        v_repr = ''
        if type(v) is type([]):
            v_repr = '\n'.join(map(lambda x:__show_value__(x), v))
        elif type(v) is type({}):
            v_repr = ','.join(map(lambda x:'%s:%s' % (x, __show_value__(v[x])), v.keys()))
        elif v:
            v_repr = v
        else:
            pass

        return v_repr

    if type(data) is not type({}):
        raise TypeError("data not an object")

    tab_data = [['Attribute','Value']]

    data_keys = data.keys()
    if not attrs_to_show:
        attrs_to_show = data_keys
        attrs_to_show.sort()

    for k in attrs_to_show:
        if k in data_keys:
            tab_data.append( [k, __show_value__(data[k])] )
    
    t = SingleTable(tab_data, title)

    t.title = None
    t.inner_heading_row_border = True
    t.inner_row_border = True
    t.justify_columns = {0: 'right', 1: 'left'}

    # wrapping value to fit into terminal
    max_width = t.column_max_width(1)
    for d in t.table_data:
        d[1] = '\n'.join(textwrap.wrap(d[1], max_width, replace_whitespace=False))

    return t

def makeTabular(title, data, d_keys, t_keys, separator):
    """ make a data tabular with specified title and columes
    """ 

    if type(data) is not type([]):
        raise TypeError("data object not a list")

    if type(d_keys) is not type([]):
        raise TypeError("d_keys object not a dictionary")

    if type(t_keys) is not type([]):
        raise TypeError("t_keys object not a dictionary")

    if len(d_keys) != len(t_keys):
        raise ValueError("t_keys and d_keys not equal length")

    tab_data = []
    tab_data.append(map(lambda x:re.sub(r':[0-9]+$','',x), t_keys))

    re_col_width = re.compile('.*:([0-9]+)$')
    for r in data:
        d = []
        for i in xrange(len(d_keys)):

            col_width = -1
            m = re_col_width.match(t_keys[i])
            if m:
                col_width = int(m.group(1))

            ks = d_keys[i].split('.')

            v = ''
            try:
                v = r[ks[0]]
                if not v:
                    v = '' 
                elif type(v) is type([]):
                    dv = v
                    for i in xrange(len(dv)):
                        for k in ks[1:]:
                            dv[i] = dv[i][k]
                    v = separator.join(dv)
                elif type(v) is type(dict()):
                    for k in ks[1:]:
                        v = v[k]
            except KeyError:
                pass

            if col_width > 0:
                d.append(textwrap.fill(v, col_width))
            else:
                d.append(v)

        tab_data.append(d)
    
    t = SingleTable(tab_data, title)
    t.inner_row_border = True

    return t

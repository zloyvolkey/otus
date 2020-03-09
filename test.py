import unittest
import pytest
import os
from time import sleep
from datetime import date, datetime
from log_analyzer import get_last_log, gen_parse_log, Log


def test_get_last_log(tmpdir):

    tmpdir.chdir()

    # no logs in folder
    last_log = get_last_log(tmpdir)
    assert last_log.path == None
    assert last_log.date == date(1970, 1, 1)

    # add .bz2 archive
    open('nginx-access-ui.log-20040101.bz2', 'a').close()

    # check plain files
    test_file_plain = 'nginx-access-ui.log-20010101'
    open(test_file_plain, 'a').close()
    assertion_date = date(2001, 1, 1)
    assertion_path = '{}/{}'.format(tmpdir, test_file_plain)
    last_log = get_last_log(tmpdir)
    assert assertion_date == last_log.date
    assert assertion_path == last_log.path

    # check gzip files
    test_file_gz = 'nginx-access-ui.log-20020101.gz'
    open(test_file_gz, 'a').close()
    assertion_date = date(2002, 1, 1)
    assertion_path = '{}/{}'.format(tmpdir, test_file_gz)
    last_log = get_last_log(tmpdir)
    assert assertion_date == last_log.date
    assert assertion_path == last_log.path


def test_gen_parse_log(tmpdir):
    tmpdir.chdir()

    test_file_plain = 'nginx-access-ui.log-20010101'
    test_file_path = '{}/{}'.format(tmpdir, test_file_plain)
    assertion_date = date(2002, 1, 1)
    with open(test_file_plain, 'a') as file:
        file.write('1.2.3.4 \
            abc \
            - \
            [29/Jun/2017:03:50:34 +0300] \
            \"GET \
            /api/1/campaigns/?id=4703657 HTTP/1.1\" \
            200 \
            660 \
            \"-\" \
            \"-\" \
            \"-\" \
            \"14-88\" \
            \"-\" \
            0.123')

    data = {"count": 1,
            "time_avg": 0.123,
            "time_max": 0.123,
            "time_sum": 0.123,
            "url": "/api/1/campaigns/?id=4703657",
            "time_med": 0.123,
            "time_perc": 100,
            "count_perc": 100}

    log = Log(test_file_path, assertion_date)

    gen_data = list(gen_parse_log(log))

    #url, time, total_count, total_time, url_date, errors_count
    gen_data = gen_data[0]
    assert gen_data[0] == data['url']
    assert gen_data[1] == 0.123
    assert gen_data[2] == 1
    assert gen_data[3] == 0.123
    assert gen_data[4] == assertion_date
    assert gen_data[5] == 0

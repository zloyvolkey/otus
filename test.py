import unittest
import pytest
import os
from time import sleep
from datetime import date, datetime
from log_analyzer import get_last_log, gen_parse_log, calc_time, Log, LogRecord


def test_get_last_log(tmpdir):

    tmpdir.chdir()

    # no logs in folder
    last_log = get_last_log(tmpdir)
    assert last_log.path == None
    assert last_log.date == None

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


def test_calc_time():
    data = {'count': 10,
            'count_perc': 100.0,
            'time_avg': 5.5,
            'time_max': 10.0,
            'time_med': 6.0,
            'time_perc': 100.0,
            'time_sum': 55.0,
            'url': '/test'}

    time = []
    for x in range(1, 11):
        time.append(x)

    assert data == calc_time(data['url'], time, 55, 10)


def test_gen_parse_log(tmpdir):
    tmpdir.chdir()

    test_file_plain = 'nginx-access-ui.log-20010101'
    test_file_path = '{}/{}'.format(tmpdir, test_file_plain)
    with open(test_file_plain, 'a') as file:
        file.write('1.2.3.4 \
            abc \
            - \
            [01/Jan/1970:11:11:11 +0300] \
            \"GET \
            /test HTTP/1.1\" \
            200 \
            660 \
            \"-\" \
            \"-\" \
            \"-\" \
            \"11-22\" \
            \"-\" \
            0.123\n')

    url = "/test"

    assert_record = LogRecord(url, 0.123)
    log_record = list(gen_parse_log(test_file_path))[0]

    assert log_record == assert_record
    

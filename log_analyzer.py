#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Log analyzer """

import os
import re
import gzip
import argparse
import datetime
import json
from collections import namedtuple
from string import Template

from logger_config import setup_logging
logger = setup_logging(__name__)

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "/home/user/OTUS/reports",
    "LOG_DIR": "/home/user/OTUS/log"
}

log_record_pattern = re.compile(r"""
                ^(\d+\.\d+\.\d+\.\d+)\s+            # $remote_addr
                (.+?)\s+                            # $remote_user
                (.+?)\s+                            # $http_x_real_ip
                (\[.+?\])\s+                        # [$time_local]
                (\"\S+\s+(?P<url>\S+)\s+\S+\")\s+   # "$request"
                (\d{1,3})\s+                        # $status
                (\d+)\s+                            # $body_bytes_sent
                (\".+?\")\s+                        # "$http_referer"
                (\".+?\")\s+                        # "$http_user_agent"
                (\".+?\")\s+                        # "$http_x_forwarded_for"
                (\".+?\")\s+                        # "$http_X_REQUEST_ID"
                (\".+?\")\s+                        # "$http_X_RB_USER"
                (?P<request_time>\d+\.?\d*)$        # $request_time
                """, re.VERBOSE)

log_name_pattern = re.compile(
    r"^(nginx-access-ui\.log-)(?P<date>\d{4}\d{2}\d{2})(.gz)?$")


Log = namedtuple('Log', 'path date')
LogRecord = namedtuple('LogRecord', 'url time')


def get_last_log(directory):
    """ Return (path, date) last log in directory
    or (None, default_date) if log not found """

    last_log = Log(None, None)

    for dirpath, _, filenames in os.walk(directory):
        for file in filenames:
            match = log_name_pattern.search(file)
            if match:
                try:
                    current_date = datetime.datetime.strptime(
                        match.group('date'), '%Y%m%d').date()
                    if not last_log.date or current_date > last_log.date:
                        last_log = Log(os.path.abspath(
                            os.path.join(dirpath, file)), current_date)
                except Exception:
                    logger.error('Can\'t parse log file date')

    return last_log


def gen_parse_log(log_path):
    """ Generator, Reading log and return data"""

    if log_path.endswith(".gz"):
        log = gzip.open(log_path, 'rb+')
    else:
        log = open(log_path, 'rb+')

    for line in log:
        line = line.decode('utf-8')
        match = log_record_pattern.search(line)
        if not match:
            yield None
            continue

        yield LogRecord(match.group('url'), float(match.group('request_time')))

    log.close()


def calc_time(url, time, total_time, total_count):
    """ Calculate times """
    count = len(time)
    time_sum = sum(time)
    return {
        "url": url,
        "count": count,
        "time_sum": time_sum,
        "time_avg": time_sum/count,
        "time_max": max(time),
        "time_med": sorted(time)[int((count+1)/2)] if count > 2 else time[0],
        "time_perc": time_sum/total_time*100,
        "count_perc": count/total_count*100}


def generate_report(log_path, error_limit=None):
    """ Parsing log file and return report data """

    logger.info(f'Parsing last log: {log_path}')

    urls = {}
    report = []
    errors_count = 0
    total_count = 0
    total_time = 0

    for record in gen_parse_log(log_path):
        if error_limit and errors_count > error_limit:
            logger.error("Exceeded errors limit!")
            raise Exception
        if not record:
            errors_count += 1
            continue
        if record.url not in urls:
            urls.update({record.url: [record.time, ]})
        else:
            urls[record.url].append(record.time)
        total_time += record.time
        total_count += 1

    if not total_count:
        logger.error('Log is empty')
        raise Exception

    logger.info('Calculating time')

    for url, time in urls.items():
        report.append(calc_time(url, time, total_time, total_count))

    return report


def write_report(cfg, report, report_file):
    """ Write report to file """

    with open(cfg['REPORT_DIR']+'/report.html') as file:
        report_template = file.read()

    table_json = {'table_json': sorted(
        report, key=lambda i: i['time_sum'], reverse=True)[:cfg['REPORT_SIZE']]}

    html_report = Template(report_template).safe_substitute(table_json)

    with open(report_file, 'w+') as file:
        file.write(html_report)


def create_report(cfg):
    """ Creating report """

    logger.info('Getting last log')
    last_log = get_last_log(cfg['LOG_DIR'])
    if not last_log.path:
        logger.error('Logs not found')
        return None

    logger.info('Check existing report')
    report_file = cfg['REPORT_DIR'] + \
        '/report-{}.html'.format(last_log.date.strftime('%Y.%m.%d'))
    if os.path.exists(report_file):
        logger.info(f'Report already have being done {report_file}')
        return None

    logger.info("Generate report")
    report = (generate_report(last_log.path))

    logger.info(f'Writing report to {report_file}')
    write_report(cfg, report, report_file)

    logger.info('Done')


def setup_config():
    """ Read config file from arguments and return config """

    logger.info('Set up config')

    cfg_parser = argparse.ArgumentParser("python3 log_analyzer.py")
    cfg_parser.add_argument('--config', action='store',
                            help='Path to config file')
    cfg_file = cfg_parser.parse_args().config

    try:
        with open(cfg_file) as file:
            cfg = json.loads(file.read())
            config.update(cfg)
    except Exception:
        logger.warning('Can\'t set up config from file. Using default config')

    if not os.path.exists(config['LOG_DIR']):
        logger.error('No such directory {}'.format(config['LOG_DIR']))
        raise FileExistsError

    if not os.path.exists(config['REPORT_DIR']):
        logger.info('Report dir doesn\'t exist. Creating new.')
        os.mkdir(config['REPORT_DIR'])

    return config


def main():
    """ Main """

    try:
        cfg = setup_config()
        create_report(cfg)
    except Exception as exc:
        logger.exception(f'Can\'t create report {exc}')


if __name__ == "__main__":
    main()

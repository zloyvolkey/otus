#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import getopt
import sys
import re
import gzip
import datetime
from datetime import date
import traceback
import json
import errno
from collections import namedtuple
from string import Template


import click

from pprint import pprint

from config import setup_logging
logger = setup_logging(__name__)

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


LOG_NAME_PATTERN = r'^nginx-access-ui\.log-(\d{4}\d{2}\d{2})(.gz)?$'
LOG_PATTERN = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(.+?)\s+(.+?)\s+(\[.+?\])\s+(\".+?\")\s+(\d{1,3})\s+(\d+)\s+(\".+?\")\s+(\".+?\")\s+(\".+?\")\s+(\".+?\")\s+(\".+?\")\s+(\d+\.\d+)$'
Log = namedtuple('Log', 'path date')


def get_last_log(directory):
    """ Return (path, date) last log in directory 
        or (None, default_date) if log not found 
    """
    default_date = date(1970, 1, 1)
    current_date = 0
    last_log = Log(None, default_date)

    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            match = re.search(LOG_NAME_PATTERN, f)
            if match:
                current_date = datetime.datetime.strptime(
                    match.group(1), '%Y%m%d').date()
                if current_date > last_log.date:
                    last_log = Log(os.path.abspath(
                        os.path.join(dirpath, f)), current_date)
   
    return last_log



def check_report(config, last_log):
    """ Check existing report
        return report file name if exist 
        or None 
    """

    report_file = 'report-{}.html'.format(last_log.date.strftime('%Y.%m.%d'))
    if report_file in os.listdir(config['REPORT_DIR']):
        return report_file
    else:
        return None


def gen_parse_log(last_log):
    """ Generator, Reading log and return data"""

    if last_log.path.endswith(".gz"):
        log = gzip.open(last_log.path, 'rb+')
    else:
        log = open(last_log.path, 'rb+')

    total_time = 0
    total_count = 0
    errors_count = 0

    for line in log:
        line = line.decode('utf-8')
        if not re.search(LOG_PATTERN, line):
            errors_count += 1
            logger.warning(f'Log doest match log pattern\n {line}')
            continue

        link = line.split()[6]
        time = line.split()[-1]
        total_count += 1
        total_time += float(time)

        yield (link, time, total_count, total_time, last_log.date, errors_count)
    
    log.close()


def create_report(config):
    """ Creating report """

    logger.info('Getting last log')
    last_log = get_last_log(config['LOG_DIR'])
    if last_log.path:
        logger.info('Check existing report')
        report = check_report(config, last_log)
        if report:
            logger.info(f'Report already have being done {report}')
            return None
    else:
        logger.warning('Logs not found')
        return None

    logger.info(f'Parsing last log: {os.path.basename(last_log.path)}')

    urls = {}
    report = []
    try:
        for link, time, total_count, total_time, date, errors_count in gen_parse_log(last_log):
            if link not in urls:
                urls.update({link: [float(time), ]})
            else:
                urls[link].append(float(time))
    except Exception:
        logger.exception('Error while parsing log')
        raise

    logger.info('Calculating time')

    for url, time in urls.items():
        #report_add(report, url, urls[url], total_time, total_count)
        count = len(time)
        time_sum = sum(time)
        report.append(
            {"url": url,
             "count": count,
             "time_sum": time_sum,
             "time_avg": time_sum/count,
             "time_max": max(time),
             "time_med": sorted(time)[int((count+1)/2)] if count > 2 else time[0],
             "time_perc": time_sum/total_time*100,
             "count_perc": count/total_count*100},)

    try:
        with open(config['REPORT_DIR']+'/report.html') as file:
            html_template = file.read()
    except Exception:
        logger.exception('Can\'t read report.html')
        raise

    table_json = {'table_json': sorted(
        report, key=lambda i: i['time_sum'], reverse=True)[:config['REPORT_SIZE']]}

    html_report = Template(html_template).safe_substitute(table_json)

    report_file = '{}/report-{}.html'.format(
        config['REPORT_DIR'], date.strftime('%Y.%m.%d'))

    logger.info(f'Writing report to {report_file}')

    try:
        with open(report_file, 'w+') as file:
            file.write(html_report)
    except Exception:
        logger.exception('Can\'t write report')
        raise

    logger.info('Done')
    logger.warning(f'Errors count {errors_count/total_count*100}%')


    pprint(sorted(report, key=lambda i: i['count'], reverse=True)[0])


@click.command()
@click.option('-c', '--config', 'config_file', default='./config.json', help='Path to config file')
def main(config_file):

    try:
        with open(config_file) as file:
            cfg = json.loads(file.read())
            for k, _ in config.items():
                if k in cfg:
                    config[k] = cfg[k]
    except Exception as e:
        logger.error(f'{e}')
        logger.warning('Using default config')

    logger.info('Checking config')
    if not os.path.exists(config['LOG_DIR']):
        logger.error('{} {}'.format(
            os.strerror(errno.ENOENT), config['LOG_DIR']))
        sys.exit(2)

    if not os.path.exists(config['REPORT_DIR']):
        logger.error('{} {}'.format(
            os.strerror(errno.ENOENT), config['REPORT_DIR']))
        sys.exit(2)

    logger.info(config)

    try:
        create_report(config)
    except Exception as e:
        logger.error('Can\'t create report')


if __name__ == "__main__":
    main()

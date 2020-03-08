#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import getopt
import sys
import re
import gzip
import datetime
from datetime import date
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
Log = namedtuple('Log' , 'path date') 


def get_last_log(directory): 

    current = 0
    last = Log('',date(1970,1,1))

    for dirpath,_,filenames in os.walk(directory): 
        for f in filenames: 
            match = re.search(LOG_NAME_PATTERN, f)
            if match:
                current = datetime.datetime.strptime(match.group(1), '%Y%m%d').date()
                if current > last.date:
                    last = Log(os.path.abspath(os.path.join(dirpath, f)), current)
    
    if last.path == '':
        logger.warning('No one file match log pattern')
        return None
    else:
        return last


def report_add(report, url, time, total_time, total_count):
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
         "count_perc": count/total_count*100},
    )

def gen_parse_log(config):
    
    last_log = get_last_log(config['LOG_DIR'])

    if last_log:
        if last_log.path.endswith(".gz"):
            log = gzip.open(last_log.path, 'rb+')
        else:
            log = open(last_log.path, 'rb+')
    else:
        logger.info('Logs not found')
        return None

    logger.info(f'Last log: {os.path.basename(last_log.path)}')

    total_time = 0
    total_count = 0

    for line in log:
        line = line.decode('utf-8')
        if not re.search(LOG_PATTERN, line):
            # ошибка ли?
            logger.error(f'Log doest match log pattern\n {line}')
            return None

        link = line.split()[6]
        time = line.split()[-1]
        total_count += 1
        total_time += float(time)

        yield (link, time, total_count, total_time, last_log.date)

def create_report(config):

    urls = {}
    report = []
    for link, time, total_count, total_time, date in gen_parse_log(config):
        if link not in urls:
            urls.update({link: [float(time), ]})
        else:
            urls[link].append(float(time))
        
    for url, time in urls.items():
        report_add(report, url, urls[url], total_time, total_count)

    with open('./reports/report.html') as file:
        html_template = file.read()

    table_json = {'table_json': sorted(
        report, key=lambda i: i['time_sum'], reverse=True)[:config['REPORT_SIZE']]}

    html_report = Template(html_template).safe_substitute(table_json)

    report_file = '{}/report-{}.html'.format(config['REPORT_DIR'], date.strftime('%Y.%m.%d'))
    with open(report_file, 'w+') as file:
        file.write(html_report)
    
    pprint(sorted(report, key=lambda i: i['count'], reverse=True)[0])

 
@click.command()
@click.option('-c','--config', 'config_file', default='./config.json', help='Path to config file')
def main(config_file):

    try:
        with open(config_file) as file:
            cfg = json.loads(file.read())
            for k, v in config.items():
                if k in cfg:
                    config[k] = cfg[k]
    except Exception as e:
        logger.error(f'{e}')
        logger.warning('Using default config')
    
    if not os.path.exists(config['LOG_DIR']):
        logger.error('{} {}'.format(
            os.strerror(errno.ENOENT), config['LOG_DIR']))
        sys.exit(2)

    if not os.path.exists(config['REPORT_DIR']):
        logger.error('{} {}'.format(
            os.strerror(errno.ENOENT), config['REPORT_DIR']))
        sys.exit(2)

    create_report(config)

if __name__ == "__main__":
    main()

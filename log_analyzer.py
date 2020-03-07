#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def calc_time_avg(time: list, count: int):
    return sum(time)/count


def calc_time_max(time: list):
    return max(time)


def calc_time_sum(time: list):
    return sum(time)


def calc_time_med(time: list, count: int):
    if count > 2:
        return sorted(time)[int((count+1)/2)]
    else:
        return time[0]


def calc_time_perc(time_sum: float, total_time: float):
    return time_sum/total_time*100


def calc_perc(count: int, total_count: int):
    return count/total_count*100


def report_add(report, url, time, total_time, total_count):
    count = len(time)
    time_avg = calc_time_avg(time, count)
    time_max = calc_time_max(time)
    time_sum = calc_time_sum(time)
    time_med = calc_time_med(time, count)
    time_perc = calc_time_perc(time_sum, total_time)
    count_perc = calc_perc(count, total_count)

    report.append(
        {"count": count,
         "time_avg": time_avg,
         "time_max": time_max,
         "time_sum": time_sum,
         "url": url,
         "time_med": time_med,
         "time_perc": time_perc,
         "count_perc": count_perc}
    )


def main():
    with open('nginx-access-ui.log-20170630', 'r') as logfile:
        log = logfile.readlines()

    total_time = 0
    total_count = 0
    urls = {}
    for line in log:
        link = line.split()[6]
        time = line.split()[-1]
        if link not in urls:
            urls.update({link: [float(time), ]})
        else:
            urls[link].append(float(time))
        total_count += 1
        total_time += float(time)

    report = []

    for url, time in urls.items():
        report_add(report, url, urls[url], total_time, total_count)

    for i in report:
        if i['count'] > 1000:
            pprint(i)


if __name__ == "__main__":
    main()

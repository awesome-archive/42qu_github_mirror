#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time, mktime, strptime, strftime, timezone
import datetime

ONE_DAY = 3600 * 24
ONE_DAY_MINUTE = 60*24
TIMEZONE_OFFSET = mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))
DATE_BEGIN = datetime.date(1970, 1, 1)
DATETIME_BEGIN = datetime.datetime(1970, 1, 1)


def today_days():
    return (time() + timezone) // ONE_DAY

def today_seconds():
    return today_days() * ONE_DAY - timezone

def today_ymd_int():
    t = datetime.date.today()
    return t.year*10000 + t.month*100 + t.day

def yesterday_seconds():
    return today_days() - ONE_DAY

def date_to_days(s):
    n = strptime(s, '%Y%m%d')
    seconds = mktime(n) - TIMEZONE_OFFSET
    return seconds // ONE_DAY

def ymd2days(ymd):
    return (datetime.date(ymd//10000, (ymd%10000)//100, ymd%100) - DATE_BEGIN).days


def minute2date(minute):
    return datetime.timedelta(minute/ONE_DAY_MINUTE)+DATE_BEGIN

def minute2hour(minute):
    minute = minute % ONE_DAY_MINUTE
    return '%d:%02d' % (minute//60, minute % 60)

def minute2datetime(minute):
    return datetime.timedelta(minutes=minute) + DATETIME_BEGIN

def minute2ymd(minute):
    d = minute2date(minute)
    return d.year*10000+d.month*100+d.day

def minute2ymd2(minute):
    d = minute2date(minute)
    return d.strftime('%Y.%m.%d')

def cn_date(dt):
    return dt.strftime('%Y年%m月%d日')

CN_WEEKDAY = (
     '一',
     '二',
     '三',
     '四',
     '五',
     '六',
     '日',
)

def cn_weekday(dt):
    return '周%s' % CN_WEEKDAY[dt.weekday()]

def ymd2minute(ymd):
    return ymd2days(ymd)*ONE_DAY_MINUTE

def yesterday():
    r = datetime.date.today() - datetime.timedelta(1)
    return r.strftime('%Y%m%d')


def today_year():
    return datetime.date.today().year


def year_month_str(date):
    year = date//10000
    result = [year]
    month = date%10000//100
    if month:
        result.append(month)
    return '.'.join(map(str, result))


def year_month_begin_end(begin, end):
    r = []
    if begin:
        r.append(begin)
    if end and end != begin:
        r.append(end)

    return ' - '.join(map(year_month_str, r))


TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

def epoch_seconds(timestr):
    return int(mktime(strptime(timestr, TIMESTAMP_FORMAT)))

def cn_diff_weekday(dt):
    today = datetime.date.today()
    diff_week = ((dt - today).days + today.weekday()) / 7
    cn_week_day = cn_weekday(dt)
    if diff_week == -1:
        return '上%s' % cn_week_day
    elif diff_week == 0:
        return '本%s' % cn_week_day
    elif diff_week == 1:
        return '下%s' % cn_week_day

def begin_end_by_minute(begin_time, end_time):
    begin_date = minute2date(begin_time)
    end_date = minute2date(end_time)

    row1 = [cn_date(begin_date)]
    weekday = cn_diff_weekday(begin_date)
    if weekday:
        row1.append(weekday)

    diff_day = (begin_date != end_date)

    begin_hour = minute2hour(begin_time)
    end_hour = minute2hour(end_time)

    if diff_day:
        row1.append(begin_hour)
        weekday = cn_diff_weekday(end_date)
        if weekday:
            weekday = ' %s' % weekday
        row2 = "%s%s %s"%(
            cn_date(end_date), weekday, end_hour
        )
    else:
        if begin_time == end_time:
            row2 = begin_hour
        else:
            row2 = '%s - %s'%(begin_hour, end_hour)

    return ' '.join(row1), row2, diff_day


if __name__ == '__main__':
    print today_days()

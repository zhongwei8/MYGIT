"""
strptime VS strftime

p 表示 parse 分析，将一个时间 字符串 和分析模式，返回一个 时间对象
f 表示 format，表示格式化，和 strptime 正好相反，要求给一个 时间对象 和 输出格式，返回一个时间字符串

Lib/datetime.py

-- datetime:    Basic date and time types
---- timedelta Objects
---- date Objects
---- datetime Objects
---- time Objects
---- strftime() and strptime() Behavior
        %Y:     年，带 0 填充
        %m:     月，带 0 填充
        %d:     日，带 0 填充
        %H:     时，带 0 填充
        %M:     分，带 0
        %S:     秒，带 0

推荐标准格式：  '%Y-%m-%d %H:%M:%S', 如 '2020-01-07 09:08:32'

date Objects
    .date(year, month, day)
    .today()
    .fromtimestamp(timestamp)
    .fromiosformat(date_string)     date.fromisoformat('2018-12-08'), only supports the format YYYY-MM-DD
    .year, .month, .day
    .isoformat()                    date(2002, 12, 4).isoformat()   ->  '2002-12-04'
    .strftime(format)               date(2002, 12, 4).strftime('%Y-%m-%d')  -> '2002-12-04'

datetime Objects
    .datetime(year, month, day, hour = 0, minute = 0, second = 0, microsecond = 0, tzinfo = None, *, fold = 0)
    .today(), .now(), .utcnow()
    .fromtimestamp(timestamp, tz = None)
    .fromiosformat(date_string)
    .strptime(date_string, format)
    .year, .month, .day, .hour, .second, .microsecond
    .date(), .date()
    .timestamp()
    .iosformat()
    .strftime(format)

strftime() and strptime() Behavior
    date, datetime, and time objects all support a strftime(format) method, to create a string representing the time under the control of explicit format string.
    IOSFORMAT = '%Y-%m-%d %H:%M:%S'
"""

from datetime import datetime, time, date

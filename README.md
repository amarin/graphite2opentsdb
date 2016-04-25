# graphite2opentsdb
Very simple Graphite to OpenTSDB data loader with Python2.7

## Compatibility

Only Python2.7 tested
        
## Install

    pip install -r requirements.txt
 
## Use

Usage: python graphite2opentsdb.py <command> <args>

Supported commands:

- list:
    Simply lists available metrics

- get <graphite.metric.name> [as \<target_name\>] [from \<timeperiod\>] [until \<timeperiod\>] tag1=value1 [tagN=valueN]:
    Get Graphite metric <graphite.metric.name> data and return it in OpenTSDB import format, i.e:
        <graphite.metric.name> <unix_time> <value> <tags>
    if used with "as <target_name>", graphite metric name will replaced
    
    By default If "from" is omitted, it defaults to 24 hours ago.
    If "until" is omitted, it defaults to the current time (now).

    Timeperiod can be either in absolute or relative format,
    described in Graphite data api description at http://graphite.readthedocs.org/en/latest/render_api.html

    Absolute values can be set in the format HH:MM_YYMMDD, YYYYMMDD, MM/DD/YY, or any other at(1)-compatible time format.

    Relative values is a length of time since the current time. It is always preceded by a minus sign ( - )
    and followed by a unit of time. Valid units of time:

    Abbreviation	| Unit
    ----------------|--------------
    s	            | Seconds
    min	            | Minutes
    h	            | Hours
    d	            | Days
    w	            | Weeks
    mon	            | 30 Days (month)
    y	            | 365 Days (year)


    Example:
    > get server.temperature.temp1 as temp1 from -7d entity=Obj100
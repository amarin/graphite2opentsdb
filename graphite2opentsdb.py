import copy
import time
import requests
import sys
from requests.exceptions import ConnectionError

import settings

USAGE = '''
Usage: %s <cmd> <args>

    Supported commands:

    - list:
        Simply lists available metrics

    - get <graphite.metric.name> [as <target_name>] [from <timeperiod>] [until <timeperiod>] tag1=value1 [tagN=valueN]:
        Get Graphite metric <graphite.metric.name> data and return it in OpenTSDB import format, i.e:
            <graphite.metric.name> <unix_time> <value> <tags>
        if used with "as <target_name>", graphite metric name will replaced.

        By default If "from" is omitted, it defaults to 24 hours ago.
        If "until" is omitted, it defaults to the current time (now).


        Timeperiod can be either in absolute or relative format,
        described in Graphite data api description at http://graphite.readthedocs.org/en/latest/render_api.html

        Absolute values can be set in the format HH:MM_YYMMDD, YYYYMMDD, MM/DD/YY, or any other at(1)-compatible time format.

        Relative values is a length of time since the current time. It is always preceded by a minus sign ( - )
        and followed by a unit of time. Valid units of time:

        Abbreviation	Unit
        s	            Seconds
        min	            Minutes
        h	            Hours
        d	            Days
        w	            Weeks
        mon	            30 Days (month)
        y	            365 Days (year)


        Example:
        > get server.temperature.temp1 as temp1 from -7d entity=Obj100


''' % sys.argv[0]


def make_graphite_url(path):
    graphite_host = settings.GRAPHITE_PORT == 80 and settings.GRAPHITE_HOST or "%s:%s" % (
        settings.GRAPHITE_HOST, settings.GRAPHITE_PORT
    )
    return "%s://%s/%s" % (
        settings.GRAPHITE_SCHEMA,
        graphite_host,
        path
    )


def list_metrics(*args):
    if args:
        print("Arguments not needed here")
        exit(64)

    metrics_url = make_graphite_url("metrics/index.json")
    try:
        response = requests.get(metrics_url)
        if 200 == response.status_code:
            metrics_json = response.json()
            if isinstance(metrics_json, list):
                for m in metrics_json:
                    print(m)
            else:
                print("Unexpected response body")
        else:
            print("Unexpected response code\n: GET %s\n RESULT %s %s" % (
                metrics_url,
                response.status_code,
                response.reason
            ))
    except ConnectionError as exc:
        print("Connection failed to %s: %s" % (metrics_url, exc.message))


def metric_data(*args):

    parse_args = list()
    parse_args.extend(args)
    source_name = parse_args.pop(0)

    target_name = "%s" % source_name
    opt = None
    from_spec = None
    until_spec = None
    tags = []

    if 1 < len(parse_args):
        print("parsing tags: {}".format(parse_args))
        if "as" == parse_args[0]:
            opt = parse_args.pop(0)
            target_name = parse_args.pop(0)
            print("Parsed {} {}, rest ones {}".format(opt.upper(), target_name, parse_args))
        if "from" == parse_args[0]:
            opt = parse_args.pop(0)
            from_spec = parse_args.pop(0)
            print("Parsed {} {}, rest ones {}".format(opt.upper(), from_spec, parse_args))
        if "until" == parse_args[0]:
            opt = parse_args.pop(0)
            until_spec = parse_args.pop(0)
            print("Parsed {} {}, rest ones {}".format(opt.upper(), from_spec, parse_args))

        print("the rest should be tags {}".format(parse_args))
        tags = parse_args[:]
    else:
        pass

    url = "render/?"
    url += "format=json"
    url += "&_salt={}".format(time.time())
    url += "&target={}".format(source_name)
    if from_spec:
        url += "&from={}".format(from_spec)
    if until_spec:
        url += "&until={}".format(until_spec)

    metric_data_url = make_graphite_url(url)
    try:
        response = requests.get(metric_data_url)
        if 200 == response.status_code:
            metrics_json = response.json()
            if not len(metrics_json):
                print("Unexpected response body: no data")
                exit(64)
            if 'datapoints' in metrics_json[0]:
                datapoints = metrics_json[0]["datapoints"]
                for dp in datapoints:
                    print("%s %s %s %s" % (
                        target_name, dp[1], dp[0], " ".join(tags)
                    ))
            else:
                print("Unexpected response body: no datapoints key")
                exit(64)
        else:
            print("Unexpected response code\n: GET %s\n RESULT %s %s" % (
                metric_data_url,
                response.status_code,
                response.reason
            ))
            exit(64)
    except ConnectionError as exc:
        print("Connection failed to %s: %s" % (metric_data_url, exc.message))
        exit(64)

if len(sys.argv) == 1:
    print(USAGE)
    exit(0)
else:
    cmd = sys.argv[1]
    commands = {
        "list": list_metrics,
        "get": metric_data
    }
    if cmd in commands:
        func_args = [x for x in sys.argv[2:]]
        commands[cmd](*func_args)

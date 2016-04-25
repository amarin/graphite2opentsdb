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

    - get <graphite.metric.name> [as <target_name>] tag1=value1 [tagN=valueN]:
        Get Graphite metric <graphite.metric.name> data and return it in OpenTSDB import format, i.e:
            <graphite.metric.name> <unix_time> <value> <tags>
        if used with "as <target_name>", graphite metric name will replaced

        Example:
        > get server.temperature.temp1 as temp1 entity=Obj100
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
    source_name = args[0]
    target_name = "%s" % source_name
    tags = []
    if 1 < len(args):
        tags = args[1:]
        if "as" == args[1]:
            target_name = args[2]
            tags = args[3:]
    else:
        pass

    metric_data_url = make_graphite_url("render/?&_salt=%s&target=%s&format=json" % (
        time.time(),
        source_name
    ))
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

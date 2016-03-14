import time
import requests
import sys
from requests.exceptions import ConnectionError

import saymon.settings

USAGE='''
Usage: %s <cmd> <args>

    Supported commands:

    - list:
        Simply lists avalilable metrics

    - get <graphite.metrica.name> [as <opentsdb_name>] tag1=value1 [tagN=valueN]:
        Get Graphite metrica <graphite.metrica.name> data and return it in opentsdb format, i.e:
            <opentsdb_name> <unixtime> <value> <tags>
        if used with "as <opentsdb_name>", graphite metrica name will replaced

        Example:
        > get server.temperature.temp1 as temp1 entiry=Obj100

''' % sys.argv[0]


def make_graphite_url(path):
    graphite_host = saymon.settings.GRAPHITE_PORT == 80 and saymon.settings.GRAPHITE_HOST or "%s:%s" % (
        saymon.settings.GRAPHITE_HOST, saymon.settings.GRAPHITE_PORT
    )
    return "%s://%s/%s" % (
        saymon.settings.GRAPHITE_SCHEMA,
        graphite_host,
        path
    )


def list_metrics(*args):
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
        print("Connection failed to %s: %s" %(metrics_url, exc.message))


def metrica_data(*args):
    metrica_name = args[0]
    opentsdb_name = "%s" % metrica_name
    tags = []
    if 1<len(args):
        tags=args[1:]
        if "as"==args[1]:
            opentsdb_name=args[2]
            tags = args[3:]
    else:
        pass

    metrica_data_url = make_graphite_url("render/?&_salt=%s&target=%s&format=json" % (
        time.time(),
        metrica_name
    ))
    try:
        response = requests.get(metrica_data_url)
        if 200 == response.status_code:
            metrics_json = response.json()
            if "datapoints" in metrics_json[0]:
                datapoints = metrics_json[0]["datapoints"]
                for dp in datapoints:
                    print("%s %s %s %s" % (
                        opentsdb_name, dp[1], dp[0], " ".join(tags)
                    ))
            else:
                print("Unexpected response body: no datapoints key")
                exit(64)
        else:
            print("Unexpected response code\n: GET %s\n RESULT %s %s" % (
                metrica_data_url,
                response.status_code,
                response.reason
            ))
            exit(64)
    except ConnectionError as exc:
        print("Connection failed to %s: %s" %(metrica_data_url, exc.message))
        exit(64)

if len(sys.argv) == 1:
    print(USAGE)
    exit(0)
else:
    cmd = sys.argv[1]
    commands = dict(
        list = list_metrics,
        get = metrica_data,
    )
    if cmd in commands:
        args = [x for x in sys.argv[2:]]
        commands[cmd](*args)




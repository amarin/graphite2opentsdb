# graphite2opentsdb
Very simple Graphite to OpenTSDB data loader
        
## Install

    pip install -r requirements.txt
 
## Use

Usage: graphite2opentsdb.py <command> <args>

    Supported commands:

    - list:
        Simply lists available metrics

    - get <graphite.metric.name> [as <target_name>] tag1=value1 [tagN=valueN]:
        Get Graphite metric <graphite.metric.name> data and return it in OpenTSDB import format, i.e:
            <graphite.metric.name> <unix_time> <value> <tags>
        if used with "as <target_name>", graphite metric name will replaced

        Example:
        > get server.temperature.temp1 as temp1 entity=Obj100
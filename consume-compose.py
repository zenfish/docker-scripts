#!/usr/bin/env python

#
# takes a compose file, hunts for connection statements, and tries 
# to create dot vis output for graphing out the various lines of 
# communication.
#
# Currently it looks for:
#
#   links
#   external_links
#   volumes
#   ports
#
# it ignores lots of things that I don't understand or haven't used yet.
#

# requires pygraphviz & docker-compose python libs

import sys
import yaml
import pygraphviz as pgv
from collections import defaultdict
# seemingly undocumented magic that might prove useful
from compose.config.config import ConfigFile

# arg sanity check
try:
    dcompose = ConfigFile.from_filename(sys.argv[1])

except IndexError as e:
    print "Usage: file.yml"
    sys.exit(1)
except Exception as e:
    print "Error: %s" % e
    sys.exit(2)

filename      = sys.argv[1]
# assume it's a foo.bar kinda file
filebase      = filename.split('.')[0]

# this is where we draw the relationships
compose       = defaultdict(lambda : defaultdict(list))
# various things to look for inside compose file
compose_items = ["links", "external_links", "volumes", "ports"]

# graph object
dvis          = pgv.AGraph(strict=False,directed=True)

# print ConfigFile.get_service_dicts(dcompose)

# only know of 2 versions so far... assume it's one unless proven otherwise
containers = dcompose.config

try:
    dcompose.config['services']
    assert dcompose.config['version'] == '2'
    containers = dcompose.config['services']
    # print "Looks like V2!\n\n"

except Exception as e:
    pass

# for container, config in dcompose.config.iteritems():
for container, config in containers.iteritems():

    # print config.keys()

    # first add any nodes
    dvis.add_node(container, style="filled", fillcolor="lightblue", fontsize="10")

    ports = ''
    # use this to add to links or other connectors if applicable
    if 'ports' in config.keys():
        if type(config['ports']) is list:
            ports = 'port(s):' + ','.join(config['ports'])
        else:
            ports = config['ports']

    # treating links and external links the same
    if 'links' in config.keys():
        for link in config['links']:
            link = link.split(':')[0]
            if ports:
                dvis.add_edge(container, link, label=ports, style="filled", fontsize="10", fillcolor="lightgray")
            else:
                dvis.add_edge(container, link, style="filled", fontsize="10", fillcolor="lightgray")

    if 'external_links' in config.keys():
        for link in config['external_links']:
            if ports:
                dvis.add_edge(container, link, label=ports, style="filled", fontsize="10", fillcolor="lightgray")
            else:
                dvis.add_edge(container, link, style="filled", fontsize="10", fillcolor="lightgray")

    # if just have ports and no links
    if ports and not 'links' in config.keys() and not 'external_links' in config.keys():
        dvis.add_node('EXTERNAL', fillcolor="red", style="filled")
        dvis.add_edge(container, 'EXTERNAL', label=ports, style="filled", fontsize="8", fillcolor="red")


    # goes... to somewhere!
    if 'networks' in config.keys():
        for network in config['networks']:
            network = network.split(':')[0]
            dvis.add_node(network, style="filled", fillcolor="firebrick1", shape="doublecircle", fontsize="10")
            dvis.add_edge(container, network)


    # drives/files/whatever
    if 'volumes' in config.keys():
        for volume in config['volumes']:
            dvis.add_node(volume, style="filled", fillcolor="lightgrey", shape="box", fontsize="8")
#           print "V"
            # print container, link
            dvis.add_edge(container, volume, style="dashed")


# a little header to remind me how to us this
print """
//
// Create a PNG file from the output using:
//
//     dot -Tpng -o %s.png < %s.dot
//

""" % (filebase, filebase)

print dvis.string()


# print "\n".join('"{}" -> "{}"'.format(s, format_dest(d)) for s, d in iter_links(dcompose))


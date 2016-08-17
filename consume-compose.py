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

#
# nodes are colored according to colorbrew patterns. They repeat after a 
# dozen nodes.
#

# requires pygraphviz & docker-compose python libs

#
# Possible values - LR, RL, BT, TB... for left->right, bottom->top, etc.
DIRECTION="TB"

import os
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
filebase      = os.path.splitext(filename)[0]

# this is where we draw the relationships
compose       = defaultdict(lambda : defaultdict(list))
# various things to look for inside compose file
compose_items = ["links", "external_links", "volumes", "ports"]

# graph object
dvis          = pgv.AGraph(strict=False,directed=True,rankdir=DIRECTION,colorscheme='set312')


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


node_color = -1

# only twelve allowed! ;)   From color brewer
colors = ["#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd", "#ccebc5", "#ffed6f"]


# for container, config in dcompose.config.iteritems():
for container, config in containers.iteritems():

    node_color = node_color + 1
    if node_color == 12:
        node_color = 1

    ports = ''

    # print config.keys()

    # first add any nodes
    dvis.add_node(container, style="filled", fillcolor=colors[node_color], fontsize="10")

    # treating links and external links the same
    if 'links' in config.keys():
        for link in config['links']:
            link = link.split(':')[0]
            dvis.add_edge(container, link, style="filled", fontsize="10", fillcolor=colors[node_color])

    if 'external_links' in config.keys():
        for link in config['external_links']:
            dvis.add_edge(container, link, style="filled", fontsize="10", fillcolor="lightgray")

    # any ports specified
    if 'ports' in config.keys():
        # print ports
        if type(config['ports']) is list:
            ports = 'port(s):' + ','.join(config['ports'])
        else:
            ports = config['ports']

    # if has ports... external inbound to....
    if ports:
        dvis.add_node('EXTERNAL', fillcolor="red", style="filled")
        dvis.add_edge('EXTERNAL', container, style="filled", fontsize="8", fillcolor="red", label=ports)

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
//  Larger graph with:
//
//     dot -Tpng -Gsize=8,8\! -o %s.png < %s.dot
//

""" % (filebase, filebase, filebase, filebase)

print dvis.string()


# print "\n".join('"{}" -> "{}"'.format(s, format_dest(d)) for s, d in iter_links(dcompose))


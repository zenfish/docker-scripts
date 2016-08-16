#!/usr/bin/env python

# create an issue in jira

#
# Usage below - assignee, description, summary are REQUIRED
#
# -a dan.farmer     who issue is assigned to
#
# -d 'foo bar'      description of issue
# -D filename       read description from file
#
# -i issue-type     issue type - default is "Task"
#
# -l labels         label(s) for issue - default "devops"; comma sep'd
#
# -n days           task is due N days from now. Default = 1 day
#
# -p projectname    name of project - default is "DEVOPS"
#
# -P priority       priority - default is "Medium"
#
# -s summary        summary of issue
#
# -w watcher        somebody's watching you... cue men at work... default = "devops"
#

from jira               import JIRA
from distutils.version  import StrictVersion
from datetime           import datetime, timedelta
from threading          import Lock, Thread

import jira
import optparse
import sys
import time

#
# requires a somewhat modern version of python jira lib (1+?)
#

# min version required
min_jversion = '1.0.0'

# check it out
if StrictVersion(min_jversion) > StrictVersion(jira.__version__):
    print "This requires at least version %s of the python jira library" % jversion

# default time to close issue
N_DAYS = 4

#
# aarrrghs
#
parser = optparse.OptionParser(usage='usage: %s [options] -a assignee -d description -s summary')

parser.add_option('-a', '--assignee',    dest="assignee")
parser.add_option('-d', '--description', dest="description")
parser.add_option('-D', '--dfile',       dest="dfile")
parser.add_option('-i', '--issue-type',  dest="issueType",      default="Task")
parser.add_option('-l', '--labels',      dest="labels",         default="devops")
parser.add_option('-n', '--days',        dest="days",           default=N_DAYS)
parser.add_option('-p', '--project',     dest="project",        default="DEVOPS")
parser.add_option('-P', '--priority',    dest="priority",       default="Medium")
parser.add_option('-s', '--summary',     dest="summary")
parser.add_option('-w', '--watcher',     dest="watcher",        default="devops")
# parser.add_option('-w', '--watcher',     dest="watcher",        default="dan.farmer")


# some defaults

(opts, args) = parser.parse_args()

# if -D, read file
try:
    with open(opts.dfile) as f:
        # hack for multilines... need to put a "\\ " -> newline
        opts.description = f.read().replace('\n','\\\\ ')
except:
    pass

# print opts.description

# mandatory options
if not opts.assignee or not opts.description or not opts.summary:
    print('usage: %prog [options] -a assignee -d description -s summary')
    sys.exit(2)

# some fluff to help
LOCK = Lock()
uri  = 'https://jira.multiscalehn.com'
auth = ('jsvc', '')

jira = JIRA(uri, basic_auth=auth)

#
# when is this due to be resolved?
#
now      = datetime.now()
n_days   = timedelta(N_DAYS)
due_date = datetime.strftime(now + n_days, '%Y-%m-%d')

# to avoid ... issues
with LOCK:
    issue = jira.create_issue(project=opts.project,
                              summary=opts.summary,
                              description=opts.description,
                              issuetype={'name':opts.issueType},
                              assignee={'name':opts.assignee},
                              priority={'name': opts.priority},
                              labels=[opts.labels],
                              duedate=due_date)

# add watcher... I don't think it can be done in the above step, but...?
jira.add_watcher(issue, opts.watcher)

#print('issue %s created successfully' % jira.issue)
print('issue created successfully')

# import pdb
# pdb.set_trace()

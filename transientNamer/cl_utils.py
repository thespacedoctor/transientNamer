#!/usr/local/bin/python
# encoding: utf-8
"""
Documentation for transientNamer can be found here: http://transientNamer.readthedocs.org/en/stable

Usage:
    transientNamer [-c] cone <ra> <dec> <arcsecRadius> [<render> | mysql <tableNamePrefix>] [-o directory]
    transientNamer [-c] search <name> [<render> | mysql <tableNamePrefix>] [-o directory]
    transientNamer [-c] new <discInLastDays> [<render> | mysql <tableNamePrefix>] [-o directory]

Commands:
    cone                  perform a conesearch on the TNS
    search                perform a name search on the TNS
    new                   list newly discovered TNS objects

Arguments:
    ra
    dec
    arcsecRadius
    name                  the name of the object the search for (TNS or survey name)
    render                output format for results. Options include json, csv, table, markdown, yaml
    tableNamePrefix       the prefix for the tables to write the mysql insert statements for
    dirPath               path to the directory to save the output to

Options:
    -h, --help                           show this help message
    -v, --version                        show version
    -s, --settings                       the settings file
    -c, --withComments                   return TNS comments in result sets
    -o directory, --output=directory     output to files in the directory path
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import pickle
from docopt import docopt
from fundamentals import tools, times
import transientNamer
# from ..__init__ import *


def tab_complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


def main(arguments=None):
    """
    *The main function used when ``cl_utils.py`` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="WARNING",
        options_first=False,
        projectName="transientNamer"
    )
    arguments, settings, log, dbConn = su.setup()

    # tab completion for raw_input
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(tab_complete)

    # unpack remaining cl arguments using `exec` to setup the variable names
    # automatically
    for arg, val in arguments.iteritems():
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        if isinstance(val, str) or isinstance(val, unicode):
            exec(varname + " = '%s'" % (val,))
        else:
            exec(varname + " = %s" % (val,))
        if arg == "--dbConn":
            dbConn = val
        log.debug('%s = %s' % (varname, val,))

    ## START LOGGING ##
    startTime = times.get_now_sql_datetime()
    log.info(
        '--- STARTING TO RUN THE cl_utils.py AT %s' %
        (startTime,))

    if search or new or cone:
        if ra:
            tns = transientNamer.search(
                log=log,
                ra=ra,
                dec=dec,
                radiusArcsec=arcsecRadius,
                comments=withCommentsFlag
            )
        if name:
            tns = transientNamer.search(
                log=log,
                name=name,
                comments=withCommentsFlag
            )
        if discInLastDays:
            tns = transientNamer.search(
                log=log,
                discInLastDays=discInLastDays,
                comments=withCommentsFlag
            )

        # Recursively create missing directories
        if outputFlag and not os.path.exists(outputFlag):
            os.makedirs(outputFlag)

        if tableNamePrefix:
            sources, phot, spec, files = tns.mysql(
                tableNamePrefix=tableNamePrefix, dirPath=outputFlag)
            numSources = len(sources.split("\n")) - 1
        elif not render or render == "table":
            sources, phot, spec, files = tns.table(dirPath=outputFlag)
            numSources = len(sources.split("\n")) - 4
        elif render == "csv":
            sources, phot, spec, files = tns.csv(dirPath=outputFlag)
            numSources = len(sources.split("\n")) - 1
        elif render == "json":
            sources, phot, spec, files = tns.json(dirPath=outputFlag)
            numSources = len(sources.split("{")) - 1
        elif render == "yaml":
            sources, phot, spec, files = tns.yaml(dirPath=outputFlag)
            numSources = len(sources.split("\n-"))
        elif render == "markdown":
            sources, phot, spec, files = tns.markdown(dirPath=outputFlag)
            numSources = len(sources.split("\n")) - 2

        if numSources == 1:
            print "%(numSources)s transient found" % locals()
        elif numSources > 1:
            print "%(numSources)s transients found" % locals()

        if not outputFlag:
            print "\n# Matched Transients"
            print sources
            print "\n# Transient Photometry"
            print phot
            print "\n# Transient Spectra"
            print spec
            print "\n# Transient Supplementary Files"
            print files
            print "\n# Original TNS Search URL"
            print tns.url
        # CALL FUNCTIONS/OBJECTS

    if "dbConn" in locals() and dbConn:
        dbConn.commit()
        dbConn.close()
    ## FINISH LOGGING ##
    endTime = times.get_now_sql_datetime()
    runningTime = times.calculate_time_difference(startTime, endTime)
    log.info('-- FINISHED ATTEMPT TO RUN THE cl_utils.py AT %s (RUNTIME: %s) --' %
             (endTime, runningTime, ))

    return


if __name__ == '__main__':
    main()

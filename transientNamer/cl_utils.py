#!/usr/bin/env python
# encoding: utf-8
"""
Documentation for transientNamer can be found here: http://transientNamer.readthedocs.org/en/stable

Usage:
    transientNamer [-c] cone <ra> <dec> <arcsecRadius> [<render> | mysql <tableNamePrefix>] [-o directory]
    transientNamer [-c] search <name> [<render> | mysql <tableNamePrefix>] [-o directory]
    transientNamer [-c] new <reportedInLastDays> [<render> | mysql <tableNamePrefix>] [-o directory]
    transientNamer [-i] notes <reportedInLastDays> 

Commands:
    cone                  perform a conesearch on the TNS
    search                perform a name search on the TNS
    new                   list newly reported TNS objects
    notes                 download astronotes amd cache in local directory
    
Arguments:
    ra
    dec
    arcsecRadius
    name                  the name of the object the search for (TNS or survey name)
    render                output format for results. Options include json, csv, table, markdown, yaml
    tableNamePrefix       the prefix for the tables to write the mysql insert statements for
    directory             path to the directory to save the output to
    reportedInLastDays    download and parse data reported within the last <n> days
    mysql                 generate mysql insert scripts

Options:
    -h, --help                           show this help message
    -v, --version                        show version
    -s, --settings                       the settings file
    -c, --withComments                   return TNS comments in result sets
    -i, --import                         parse and import the content of the astronotes into a MySQL database
    -o directory, --output=directory     output to files in the directory path
"""
from __future__ import print_function
import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import pickle
from docopt import docopt
from fundamentals import tools, times
from subprocess import Popen, PIPE, STDOUT
import transientNamer
from transientNamer import astronotes


def tab_complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


def main(arguments=None):
    """
    *The main function used when `cl_utils.py` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="WARNING",
        options_first=False,
        projectName="transientNamer",
        defaultSettingsFile=True
    )
    arguments, settings, log, dbConn = su.setup()

    # tab completion for raw_input
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(tab_complete)

    # UNPACK REMAINING CL ARGUMENTS USING `EXEC` TO SETUP THE VARIABLE NAMES
    # AUTOMATICALLY
    a = {}
    for arg, val in list(arguments.items()):
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        a[varname] = val
        if arg == "--dbConn":
            dbConn = val
            a["dbConn"] = val
        log.debug('%s = %s' % (varname, val,))

    ## START LOGGING ##
    startTime = times.get_now_sql_datetime()
    log.info(
        '--- STARTING TO RUN THE cl_utils.py AT %s' %
        (startTime,))

    cone = a["cone"]
    search = a["search"]
    new = a["new"]
    ra = a["ra"]
    dec = a["dec"]
    arcsecRadius = a["arcsecRadius"]
    name = a["name"]
    render = a["render"]
    tableNamePrefix = a["tableNamePrefix"]
    notes = a["notes"]

    parse = a["importFlag"]
    mysql = a["mysql"]
    reportedInLastDays = a["reportedInLastDays"]
    withCommentsFlag = a["withCommentsFlag"]
    outputFlag = a["outputFlag"]

    # set options interactively if user requests
    if "interactiveFlag" in a and a["interactiveFlag"]:

        # load previous settings
        moduleDirectory = os.path.dirname(__file__) + "/resources"
        pathToPickleFile = "%(moduleDirectory)s/previousSettings.p" % locals()
        try:
            with open(pathToPickleFile):
                pass
            previousSettingsExist = True
        except:
            previousSettingsExist = False
        previousSettings = {}
        if previousSettingsExist:
            previousSettings = pickle.load(open(pathToPickleFile, "rb"))

        # x-raw-input
        # x-boolean-raw-input
        # x-raw-input-with-default-value-from-previous-settings

        # save the most recently used requests
        pickleMeObjects = []
        pickleMe = {}
        theseLocals = locals()
        for k in pickleMeObjects:
            pickleMe[k] = theseLocals[k]
        pickle.dump(pickleMe, open(pathToPickleFile, "wb"))

    if "init" in a and a["init"]:
        from os.path import expanduser
        home = expanduser("~")
        filepath = home + "/.config/transientNamer/transientNamer.yaml"
        try:
            cmd = """open %(filepath)s""" % locals()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except:
            pass
        try:
            cmd = """start %(filepath)s""" % locals()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except:
            pass
        return

    # CALL FUNCTIONS/OBJECTS
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
        if reportedInLastDays:
            tns = transientNamer.search(
                log=log,
                discInLastDays=reportedInLastDays,
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
            print("%(numSources)s transient found" % locals())
        elif numSources > 1:
            print("%(numSources)s transients found" % locals())

        if not outputFlag:
            print("\n# Matched Transients")
            print(sources)
            print("\n# Transient Photometry")
            print(phot)
            print("\n# Transient Spectra")
            print(spec)
            print("\n# Transient Supplementary Files")
            print(files)
            print("\n# Original TNS Search URL")
            print(tns.url)

    if notes:
        an = astronotes.astronotes(
            log=log,
            dbConn=dbConn,
            settings=settings
        )
        downloadCount = an.download(
            cache_dir=settings["astronote-cache"], inLastDays=reportedInLastDays)
        print(f"{downloadCount} new astronotes downloaded and cached")

        if parse:
            print(f"importing notes into database tables")
            an.notes_to_database()

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

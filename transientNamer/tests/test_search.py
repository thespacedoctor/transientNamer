from __future__ import print_function
from builtins import str
import os
import unittest
import shutil
import yaml
from transientNamer.utKit import utKit
from fundamentals import tools
from os.path import expanduser
home = expanduser("~")

packageDirectory = utKit("").get_project_root()
settingsFile = packageDirectory + "/test_settings.yaml"

su = tools(
    arguments={"settingsFile": settingsFile},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName=None,
    defaultSettingsFile=False
)
arguments, settings, log, dbConn = su.setup()

# SETUP PATHS TO COMMON DIRECTORIES FOR TEST DATA
moduleDirectory = os.path.dirname(__file__)
pathToInputDir = moduleDirectory + "/input/"
pathToOutputDir = moduleDirectory + "/output/"

try:
    shutil.rmtree(pathToOutputDir)
except:
    pass
# COPY INPUT TO OUTPUT DIR
shutil.copytree(pathToInputDir, pathToOutputDir)

# Recursively create missing directories
if not os.path.exists(pathToOutputDir):
    os.makedirs(pathToOutputDir)

class test_search(unittest.TestCase):

    def test_search_function01(self):
        kwargs = {}
        kwargs["log"] = log
        kwargs["settings"] = settings
        kwargs["ra"] = "06:50:36.74"
        kwargs["dec"] = "+31:06:44.7"
        kwargs["radiusArcsec"] = 5.0
        # xt-kwarg_key_and_value
        from transientNamer import search
        tns = search(**kwargs)
        print(tns.sources)
        print(tns.spectra)
        print(tns.photometry)
        print(tns.files)
        print(tns.url)
        csvSources, csvPhot, csvSpec, csvFiles = tns.csv()
        print(csvSources)
        jsonSources, jsonPhot, jsonSpec, jsonFiles = tns.json()
        print(jsonSources)
        yamlSources, yamlPhot, yamlSpec, yamlFiles = tns.yaml()
        print(yamlSources)
        markdownSources, markdownPhot, markdownSpec, markdownFiles = tns.markdown()
        print(markdownSources)
        tableSources, tablePhot, tableSpec, tableFiles = tns.table()
        print(tableSources)
        mysqlSources, mysqlPhot, mysqlSpec, mysqlFiles = tns.mysql("TNS")
        print(mysqlSources)
        print(tablePhot)
        print(tableFiles)

        tns.csv(dirPath=pathToOutputDir)
        tns.table(dirPath=pathToOutputDir)
        tns.mysql(tableNamePrefix="TNS", dirPath=pathToOutputDir)
        tns.json(dirPath=pathToOutputDir)
        tns.yaml(dirPath=pathToOutputDir)
        tns.markdown(dirPath=pathToOutputDir)

    def test_search_function02(self):
        kwargs = {}
        kwargs["log"] = log
        kwargs["settings"] = settings
        kwargs["ra"] = "06:45:03.36"
        kwargs["dec"] = "+35:44:29.8"
        kwargs["radiusArcsec"] = 5.0

        from transientNamer import search
        tns = search(**kwargs)
        print(tns.url)
        tns.csv(dirPath=pathToOutputDir)
        tns.table(dirPath=pathToOutputDir)
        tns.mysql(tableNamePrefix="fs_tns", dirPath=pathToOutputDir)
        tns.json(dirPath=pathToOutputDir)
        tns.yaml(dirPath=pathToOutputDir)
        tns.markdown(dirPath=pathToOutputDir)

    def test_search_function03(self):
        # A TEST FOR MUPTIPLE RESULTS
        kwargs = {}
        kwargs["log"] = log
        kwargs["settings"] = settings
        kwargs["ra"] = "00:00:00.00"
        kwargs["dec"] = "+00:00:00.00"
        kwargs["radiusArcsec"] = 5.0
        # xt-kwarg_key_and_value
        from transientNamer import search
        tns = search(**kwargs)

        print(tns.url)
        tns.csv(dirPath=pathToOutputDir)
        tns.table(dirPath=pathToOutputDir)
        tns.mysql(tableNamePrefix="fs_tns", dirPath=pathToOutputDir)
        tns.json(dirPath=pathToOutputDir)
        tns.yaml(dirPath=pathToOutputDir)
        tns.markdown(dirPath=pathToOutputDir)

    def test_search_function04(self):
        # A TEST FOR MUPTIPLE RESULTS
        kwargs = {}
        kwargs["log"] = log
        kwargs["settings"] = settings
        kwargs["name"] = "2016fbz"

        # xt-kwarg_key_and_value
        from transientNamer import search
        tns = search(**kwargs)
        print(tns.url)
        tns.csv(dirPath=pathToOutputDir)
        tns.table(dirPath=pathToOutputDir)
        tns.mysql(tableNamePrefix="fs_tns", dirPath=pathToOutputDir)
        tns.json(dirPath=pathToOutputDir)
        tns.yaml(dirPath=pathToOutputDir)
        tns.markdown(dirPath=pathToOutputDir)

    def test_search_function05(self):
        # A TEST FOR MUPTIPLE RESULTS
        kwargs = {}
        kwargs["log"] = log
        kwargs["settings"] = settings
        kwargs["name"] = "Gaia16bbi"

        # xt-kwarg_key_and_value
        from transientNamer import search
        tns = search(**kwargs)

        print(tns.url)
        tns.csv(dirPath=pathToOutputDir)
        tns.table(dirPath=pathToOutputDir)
        tns.mysql(tableNamePrefix="fs_tns", dirPath=pathToOutputDir)
        tns.json(dirPath=pathToOutputDir)
        tns.yaml(dirPath=pathToOutputDir)
        tns.markdown(dirPath=pathToOutputDir)

    def test_search_function06(self):
        # A TEST FOR MUPTIPLE RESULTS
        kwargs = {}
        kwargs["log"] = log
        kwargs["settings"] = settings
        kwargs["discInLastDays"] = 3

        # xt-kwarg_key_and_value
        from transientNamer import search
        tns = search(**kwargs)

        print(tns.url)
        tns.csv(dirPath=pathToOutputDir)
        tns.table(dirPath=pathToOutputDir)
        tns.mysql(tableNamePrefix="fs_tns", dirPath=pathToOutputDir)
        tns.json(dirPath=pathToOutputDir)
        tns.yaml(dirPath=pathToOutputDir)
        tns.markdown(dirPath=pathToOutputDir)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function

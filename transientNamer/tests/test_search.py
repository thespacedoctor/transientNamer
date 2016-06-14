import os
import nose
import shutil
import yaml
from transientNamer import search, cl_utils
from transientNamer.utKit import utKit

from fundamentals import tools

su = tools(
    arguments={"settingsFile": None},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="transientNamer",
    tunnel=False
)
arguments, settings, log, dbConn = su.setup()

# load settings
stream = file(
    "/Users/Dave/.config/transientNamer/transientNamer.yaml", 'r')
settings = yaml.load(stream)
stream.close()

# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()


class test_search():

    def test_search_function(self):
        kwargs = {}
        kwargs["log"] = log
        kwargs["settings"] = settings
        kwargs["ra"] = "06:50:36.74"
        kwargs["dec"] = "+31:06:44.7"
        kwargs["radiusArcsec"] = 5.0
        # xt-kwarg_key_and_value

        testObject = search(**kwargs)
        testObject.get()

    def test_search_function(self):
        kwargs = {}
        kwargs["log"] = log
        kwargs["settings"] = settings
        kwargs["ra"] = "06:45:03.36"
        kwargs["dec"] = "+35:44:29.8"
        kwargs["radiusArcsec"] = 5.0
        # xt-kwarg_key_and_value

        testObject = search(**kwargs)
        testObject.get()

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function

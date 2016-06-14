import os
import nose
import shutil
import yaml
from transientNamer import namer, cl_utils
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


class test_namer():

    def test_namer_function(self):
        kwargs = {}
        kwargs["log"] = log
        kwargs["settings"] = settings
        kwargs["ra"] = "12:20:38.72"
        kwargs["dec"] = "+28:38:17.3"
        kwargs["name"] = "ATLAS16aen"
        kwargs["discoveryMJD"] = 57450.51
        kwargs["discoveryMag"] = 18.71
        kwargs["discoveryFilter"] = "c"
        kwargs["settings"] = settings
        testObject = namer(**kwargs)
        testObject.get()

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function

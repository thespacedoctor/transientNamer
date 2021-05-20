from __future__ import print_function
from builtins import str
import os
import unittest
import shutil
import yaml
from transientNamer.utKit import utKit
from fundamentals import tools
from os.path import expanduser
from docopt import docopt
from transientNamer import cl_utils
doc = cl_utils.__doc__
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

# transientNamer [-c] cone <ra> <dec> <arcsecRadius> [<render> | mysql <tableNamePrefix>] [-o directory]
# transientNamer [-c] search <name> [<render> | mysql <tableNamePrefix>] [-o directory]
# transientNamer [-c] new <discInLastDays> [<render> | mysql
# <tableNamePrefix>] [-o directory]


class test_cl_utils(unittest.TestCase):

    def test_cone_search(self):
        # TEST CL-OPTIONS
        command = f"transientNamer cone 06:45:03.36 +35:44:29.8 5. -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)
        return

    def test_cone_search_comments(self):
        # TEST CL-OPTIONS
        command = f"transientNamer -c cone 06:45:03.36 +35:44:29.8 5. -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)
        return

    def test_cone_search_render(self):
        # TEST CL-OPTIONS
        command = f"transientNamer -c cone 06:45:03.36 +35:44:29.8 5. json -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

        # TEST CL-OPTIONS
        command = f"transientNamer -c cone 06:45:03.36 +35:44:29.8 5. csv -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

        # TEST CL-OPTIONS
        command = f"transientNamer -c cone 06:45:03.36 +35:44:29.8 5. table -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

        # TEST CL-OPTIONS
        command = f"transientNamer -c cone 06:45:03.36 +35:44:29.8 5. markdown -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

        # TEST CL-OPTIONS
        command = f"transientNamer -c cone 06:45:03.36 +35:44:29.8 5. yaml -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)
        return

    def test_cone_search_mysql(self):
        # TEST CL-OPTIONS
        command = f"transientNamer cone 06:45:03.36 +35:44:29.8 5. mysql test_table -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)
        return

    def test_cone_search_mysql_to_file(self):
        # TEST CL-OPTIONS
        thisDir = pathToOutputDir
        command = f"transientNamer cone 06:45:03.36 +35:44:29.8 5. mysql test_table -o %(thisDir)s/cl_output/ -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)
        return

    def test_name_search(self):
        # TEST CL-OPTIONS
        command = f"transientNamer search 2016fbz -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)
        return

    def test_name_search_render(self):
        # TEST CL-OPTIONS
        command = f"transientNamer search 2016fbz json -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

        # TEST CL-OPTIONS
        command = f"transientNamer search 2016fbz json -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

        # TEST CL-OPTIONS
        command = f"transientNamer search 2016fbz csv -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

        # TEST CL-OPTIONS
        command = f"transientNamer search 2016fbz table -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

        # TEST CL-OPTIONS
        command = f"transientNamer search 2016fbz yaml -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

        # TEST CL-OPTIONS
        command = f"transientNamer search 2016fbz markdown -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)
        return

    def test_name_search_mysql(self):
        # TEST CL-OPTIONS
        command = f"transientNamer search 2016fbz mysql test_search -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

    def test_name_search_output_to_file(self):
        # TEST CL-OPTIONS
        thisDir = pathToOutputDir
        command = f"transientNamer search 2016fbz markdown -o %(thisDir)s/cl_output -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

    def test_name_new(self):
        # TEST CL-OPTIONS
        thisDir = pathToOutputDir
        command = f"transientNamer new 2 markdown -o %(thisDir)s/cl_output -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

    def test_name_new_render(self):
        # TEST CL-OPTIONS
        thisDir = pathToOutputDir
        command = f"transientNamer new 2 markdown -o %(thisDir)s/cl_output -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

    def test_name_new_mysql(self):
        # TEST CL-OPTIONS
        thisDir = pathToOutputDir
        command = f"transientNamer new 2 mysql test_new -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

    def test_name_new_to_file(self):
        # TEST CL-OPTIONS
        thisDir = pathToOutputDir
        command = f"transientNamer new 2 markdown -o %(thisDir)s/cl_output -s {settingsFile}"
        args = docopt(doc, command.split(" ")[1:])
        cl_utils.main(args)

    # x-class-to-test-named-worker-function

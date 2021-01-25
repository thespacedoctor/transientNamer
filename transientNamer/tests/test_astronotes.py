from __future__ import print_function
from builtins import str
import os
import unittest
import shutil
import unittest
import yaml
from transientNamer.utKit import utKit
from fundamentals import tools
from os.path import expanduser
home = expanduser("~")

packageDirectory = utKit("").get_project_root()
settingsFile = packageDirectory + "/test_settings.yaml"
# settingsFile = home + \
#     "/git_repos/_misc_/settings/transientNamer/test_settings.yaml"

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


try:
    shutil.rmtree(settings["astronote-cache"])
except:
    pass

# xt-setup-unit-testing-files-and-folders
# xt-utkit-refresh-database


class test_astronotes(unittest.TestCase):

    def test_astronotes_create_tables_function(self):

        from fundamentals.mysql import writequery
        sqlQueries = [
            f"""DROP table astronotes_content""",
            f"""DROP table astronotes_transients""",
            f"""DROP table astronotes_keywords"""
        ]

        for sqlQuery in sqlQueries:
            try:
                writequery(
                    log=log,
                    sqlQuery=sqlQuery,
                    dbConn=dbConn
                )
            except:
                pass

        from transientNamer import astronotes
        an = astronotes(
            log=log,
            dbConn=dbConn,
            settings=settings
        )
        an._create_db_tables()
        # print(noteIds)

    def test_astronotes_function(self):

        from transientNamer import astronotes
        an = astronotes(
            log=log,
            settings=settings
        )
        noteIds = an.get_all_noteids(inLastDays=30)
        # print(noteIds)

        from transientNamer import astronotes
        an = astronotes(
            log=log,
            dbConn=dbConn,
            settings=settings
        )
        downloadCount = an.download(
            cache_dir=settings["astronote-cache"], inLastDays=30)
        print(f"{downloadCount} new astronotes downloaded and cached")

        an.notes_to_database()

    def test_astronotes_function_exception(self):

        from transientNamer import astronotes
        try:
            this = astronotes(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.get()
            assert False
        except Exception as e:
            assert True
            print(str(e))

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function

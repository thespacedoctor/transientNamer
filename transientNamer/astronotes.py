#!/usr/bin/env python
# encoding: utf-8
"""
*Tools to download, parse and ingest astronote content into a MySQL database*

:Author:
    David Young

:Date Created:
    January 15, 2021
"""
from builtins import object
import sys
import re
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
import requests
import json
from pprint import pprint
from fundamentals.mysql import insert_list_of_dictionaries_into_database_tables
from fundamentals.mysql import convert_dictionary_to_mysql_table
from fundamentals.mysql import readquery
import time
import codecs
from bs4 import BeautifulSoup


class astronotes(object):
    """
    *Tools to download, parse and ingest astronote content into a MySQL database*

    **Key Arguments:**
        - ``log`` -- logger
        - ``dbConn`` -- database connection. Default *False*
        - ``settings`` -- the settings dictionary

    **Usage:**

    To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

    To initiate a astronotes object, use the following:

    ```python
    from transientNamer import astronotes
    an = astronotes(
        log=log,
        dbConn=dbConn,
        settings=settings
    )
    ```
    """

    def __init__(
            self,
            log,
            dbConn=False,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'astronotes' object")
        self.settings = settings
        self.dbConn = dbConn

        return None

    def download(
            self,
            cache_dir,
            inLastDays=False):
        """*Download astronotes reported in the lasy N days. Check cache for notes alreaedy downloaded.*

        **Key Arguments:**
            - `cache_dir` -- the directory to cache the json notes to.
            - `inLastDays` -- download only notes reported in the last N days. Default *False*. (Download all)

        **Return:**
            - `downloadCount` -- number of new files cached

        **Usage:**

        ```python
        from transientNamer import astronotes
        an = astronotes(
            log=log,
            dbConn=dbConn,
            settings=settings
        )
        downloadCount = an.download(
            cache_dir=settings["astronote-cache"], inLastDays=30)
        print(f"{downloadCount} new astronotes downloaded anc cached")
        ```
        """
        self.log.debug('starting the ``download`` method')

        paginationSets = 50
        page = 0
        allNotes = {}
        noteCount = paginationSets + 1
        if not inLastDays:
            inLastDays = 30000

        # PAGINATE THROUGH RESULTS UNTIL WE HIT THE END
        while noteCount >= paginationSets:
            try:
                response = requests.get(
                    url="https://www.wis-tns.org/astronotes",
                    params={
                        "posted_period_value": inLastDays,
                        "posted_period_units": "days",
                        "num_page": paginationSets,
                        "page": page,
                        "format": "json"
                    },
                )
                searchPage = response.content.decode("utf-8")
            except requests.exceptions.RequestException:
                print('HTTP Request failed')
            page += 1
            data = json.loads(searchPage)
            noteCount = len(data)
            if noteCount:
                allNotes = dict(list(allNotes.items()) + list(data.items()))

        # RECURSIVELY CREATE MISSING DIRECTORIES FOR CACHE
        if not os.path.exists(self.settings["astronote-cache"]):
            os.makedirs(self.settings["astronote-cache"])

        # DOWNLOAD ONE NOTE PER FILE
        downloadCount = 0
        noteIds = []
        for k, v in allNotes.items():
            noteIds.append(k)
            filepath = self.settings["astronote-cache"] + f"/{k}.json"
            vJson = json.dumps(
                v,
                separators=(',', ': '),
                sort_keys=True,
                indent=4
            )
            if not os.path.exists(filepath):
                myFile = open(filepath, 'w')
                myFile.write(vJson)
                myFile.close()
                downloadCount += 1

        # NOW DOWNLOAD REQUIRED HTML NOTES
        for n in noteIds:
            filepath = self.settings["astronote-cache"] + f"/{n}.html"
            if not os.path.exists(filepath):
                time.sleep(1)
                try:
                    response = requests.get(
                        url=f"https://www.wis-tns.org/astronotes/astronote/{n}",
                    )
                    noteContent = response.content.decode("utf-8")
                except requests.exceptions.RequestException:
                    print('HTTP Request failed')
                myFile = open(filepath, 'w')
                myFile.write(noteContent)
                myFile.close()

        self.log.debug('completed the ``download`` method')
        return downloadCount

    def get_all_noteids(
            self,
            inLastDays=False):
        """*get the noteids of those notes released in the last N days*

        **Key Arguments:**
            - ``inLastDays`` -- report only notesIds released in the last N days. Default *False*. (Report all)

        **Return:**
            - `noteIds` -- list of all reported noteIds

        **Usage:**

        ```python
        from transientNamer import astronotes
        an = astronotes(
            log=log,
            settings=settings
        )
        noteIds = an.get_all_noteid(inLastDays=3000)
        print(f"Astronote IDs: {noteIds}")
        ```
        """
        self.log.debug('starting the ``get_all_noteids`` method')

        paginationSets = 100
        page = 0
        noteIds = []
        noteCount = paginationSets + 1
        if not inLastDays:
            inLastDays = 30000

        # PAGINATE THROUGH RESULTS UNTIL WE HIT THE END
        while noteCount >= paginationSets:
            try:
                response = requests.get(
                    url="https://www.wis-tns.org/astronotes",
                    params={
                        "posted_period_value": inLastDays,
                        "posted_period_units": "days",
                        "num_page": paginationSets,
                        "page": page
                    },
                )
                searchPage = response.content.decode("utf-8")
            except requests.exceptions.RequestException:
                print('HTTP Request failed')
            page += 1

            # GET NOTES WRAPPER

            getpage = requests.get('http://www.learningaboutelectronics.com')
            getpage_soup = BeautifulSoup(searchPage, 'html.parser')
            noteswrapper = getpage_soup.find(
                'div', {'id': 'notes-wrapper'})

            # NOW GET INDIVIDUAL NOTES
            notelinks = noteswrapper.findAll('a', {'class': 'note-link'})
            noteCount = len(notelinks)

            for link in notelinks:
                noteId = link.attrs['href'].split("/astronote/")[-1]
                noteIds.append(noteId)

        self.log.debug('completed the ``get_all_noteids`` method')
        return noteIds

    def notes_to_database(
            self):
        """*read the notes and import them into indexed MySQL database tables*

        **Usage:**

        ```python
        from transientNamer import astronotes
        an = astronotes(
            log=log,
            dbConn=dbConn,
            settings=settings
        )
        an.notes_to_database()
        ```
        """
        self.log.debug('starting the ``notes_to_database`` method')

        # CREATE THE DATABASE TABLES IF THEY DON'T EXIST
        self._create_db_tables()

        # WHICH ASTRONOTES ARE ALREADY IN THE DATABASE
        sqlQuery = u"""
            select astronote FROM astronotes_content;
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.dbConn
        )
        astronoteIds = []
        astronoteIds[:] = [l["astronote"] for l in rows]

        self._parse_json_to_database(skipAstronoteIds=astronoteIds)
        astronoteIds = []
        self._parse_html_to_database(skipAstronoteIds=astronoteIds)

        self.log.debug('completed the ``notes_to_database`` method')
        return None

    def _create_db_tables(
            self):
        """*create the astronote database tables if they don't yet exist*

        **Usage:**

        ```python
        from transientNamer import astronotes
        an = astronotes(
            log=log,
            dbConn=dbConn,
            settings=settings
        )
        an._create_db_tables()
        ```
        """
        self.log.debug('starting the ``_create_db_tables`` method')

        from fundamentals.mysql import writequery
        sqlQueries = []
        sqlQueries.append(f"""CREATE TABLE IF NOT EXISTS `astronotes_content` (
              `primaryId` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'An internal counter',
              `dateCreated` datetime DEFAULT CURRENT_TIMESTAMP,
              `dateLastModified` datetime DEFAULT CURRENT_TIMESTAMP,
              `updated` tinyint(4) DEFAULT '0',
              `abstract` text,
              `astronote` varchar(30) NOT NULL,
              `authors` text,
              `public_timestamp` datetime DEFAULT NULL,
              `source_group` varchar(100) DEFAULT NULL,
              `title` text,
              `type` varchar(100) DEFAULT NULL,
              `html_parsed_flag` TINYINT NULL DEFAULT 0,
              PRIMARY KEY (`primaryId`),
              UNIQUE KEY `astronote` (`astronote`)
            ) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;
        """)

        sqlQueries.append(f"""CREATE TABLE IF NOT EXISTS `astronotes_keywords` (
              `primaryId` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'An internal counter',
              `dateCreated` datetime DEFAULT CURRENT_TIMESTAMP,
              `dateLastModified` datetime DEFAULT CURRENT_TIMESTAMP,
              `updated` tinyint(4) DEFAULT '0',
              `astronote` varchar(30) NOT NULL,
              `keyword` varchar(30) NOT NULL,
              PRIMARY KEY (`primaryId`),
              UNIQUE KEY `astronote_keyword` (`astronote`,`keyword`)
            ) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;
        """)

        sqlQueries.append(f"""CREATE TABLE IF NOT EXISTS `astronotes_transients` (
              `primaryId` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'An internal counter',
              `dateCreated` datetime DEFAULT CURRENT_TIMESTAMP,
              `dateLastModified` datetime DEFAULT CURRENT_TIMESTAMP,
              `updated` tinyint(4) DEFAULT '0',
              `alt_name` varchar(100) DEFAULT NULL,
              `astronote` varchar(30) NOT NULL,
              `decdeg` double DEFAULT NULL,
              `iauname` varchar(30) DEFAULT NULL,
              `iauname_prefix` varchar(10) DEFAULT NULL,
              `objtype` varchar(30) DEFAULT NULL,
              `radeg` double DEFAULT NULL,
              `redshift` double DEFAULT NULL,
              `catalog` varchar(100) DEFAULT NULL,
              `host_name` varchar(100) DEFAULT NULL,
              `host_redshift` double DEFAULT NULL,
              `phase` varchar(100) DEFAULT NULL,
              `remarks` varchar(100) DEFAULT NULL,
              `source` varchar(100) DEFAULT NULL,
              `date_observed` varchar(100) DEFAULT NULL,
              `fluxdensity_mu_jy` double DEFAULT NULL,
              `mean_obs_freq_ghz` double DEFAULT NULL,
              `time_observed_ut` varchar(100) DEFAULT NULL,
              `uncertainty_mu_jy` double DEFAULT NULL,
              PRIMARY KEY (`primaryId`),
              UNIQUE KEY `astronote_iauname` (`astronote`,`iauname`),
              UNIQUE KEY `astronote_alt_name` (`alt_name`,`astronote`)
            ) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;
        """)

        for sqlQuery in sqlQueries:
            writequery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn
            )

        self.log.debug('completed the ``_create_db_tables`` method')
        return None

    def _parse_json_to_database(
            self,
            skipAstronoteIds):
        """*parse the cached json files and add content to mysql database tables*

        **Key Arguments:**
            - `skipAstronoteIds` -- the astronote IDs already present in the database - do not reparse
        """
        self.log.debug('starting the ``_parse_json_to_database`` method')

        # GENERATE A LIST OF FILE PATHS
        jsonNotes = []
        cache = self.settings["astronote-cache"]
        for d in os.listdir(cache):
            if d.split(".")[0] in skipAstronoteIds:
                continue
            filepath = os.path.join(cache, d)
            if os.path.isfile(filepath) and os.path.splitext(filepath)[1] == ".json":
                jsonNotes.append(filepath)

        # NOW READ THE JSON FILES AND WRITE DICTIONARIES NEEDED FOR MYSQL
        # TABLES
        astronotes_content = []
        astronotes_keywords = []
        astronotes_transients = []
        for file in jsonNotes:
            with open(file) as data_file:
                data = json.load(data_file)
            for k, v in data.items():
                if not len(v):
                    data[k] = None
            for k in data['keywords']:
                astronotes_keywords.append(
                    {"astronote": data['astronote'], "keyword": k})
            del data['keywords']
            if 'related_objects' in data and data['related_objects']:
                for dict in data['related_objects']:
                    try:
                        del dict['ra']
                        del dict['dec']
                    except:
                        pass
                    dict['astronote'] = data['astronote']
                    for k, v in dict.items():
                        if not len(v):
                            dict[k] = None

                    astronotes_transients.append(dict)
            del data['related_objects']
            del data['related_astronotes']

            astronotes_content.append(data)

        print(f"{len(astronotes_transients)} transients")

        # INSERT LIST OF
        # DICTIONARIES INTO DATABASE
        insert_list_of_dictionaries_into_database_tables(
            dbConn=self.dbConn,
            log=self.log,
            dictList=astronotes_keywords,
            dbTableName="astronotes_keywords",
            uniqueKeyList=["astronote", "keyword"],
            dateModified=True,
            dateCreated=True,
            batchSize=2500,
            replace=True,
            dbSettings=self.settings["database settings"]
        )

        insert_list_of_dictionaries_into_database_tables(
            dbConn=self.dbConn,
            log=self.log,
            dictList=astronotes_transients,
            dbTableName="astronotes_transients",
            uniqueKeyList=["astronote", "iauname"],
            dateModified=True,
            dateCreated=True,
            batchSize=2500,
            replace=True,
            dbSettings=self.settings["database settings"]
        )

        insert_list_of_dictionaries_into_database_tables(
            dbConn=self.dbConn,
            log=self.log,
            dictList=astronotes_content,
            dbTableName="astronotes_content",
            uniqueKeyList=["astronote"],
            dateModified=True,
            dateCreated=True,
            batchSize=2500,
            replace=True,
            dbSettings=self.settings["database settings"]
        )

        self.log.debug('completed the ``_parse_json_to_database`` method')
        return None

    def _parse_html_to_database(
            self,
            skipAstronoteIds):
        """*parse the HTML versions of the astronotes to database tables*

        **Key Arguments:**
            - `skipAstronoteIds` -- the astronote IDs already present in the database - do not reparse
        """
        self.log.debug('starting the ``_parse_html_to_database`` method')

        # GENERATE A LIST OF FILE PATHS
        htmlNotes = []
        noteIds = []
        cache = self.settings["astronote-cache"]
        for d in os.listdir(cache):
            if d.split(".")[0] in skipAstronoteIds:
                continue
            filepath = os.path.join(cache, d)
            if os.path.isfile(filepath) and os.path.splitext(filepath)[1] == ".html":
                htmlNotes.append(filepath)
                noteIds.append(d.split(".")[0])

        for note, noteId in zip(htmlNotes, noteIds):
            with codecs.open(note, encoding='utf-8', mode='r') as readFile:
                content = readFile.read()

                getpage_soup = BeautifulSoup(content, 'html.parser')
                table = getpage_soup.find(
                    'table', {'class': 'objects-table'})
                if not table:
                    continue
                thead = table.find('thead')

                # print(table)
                remove = re.compile(r'[\(\)\.]')
                underscore = re.compile(r'[ &;-]+')
                headerKeys = []
                headerKeys[:] = [th.string.lower()
                                 for th in thead.findAll('th')]
                # print(headerKeys)
                headerKeys[:] = [remove.sub('', h) for h in headerKeys]
                headerKeys[:] = [underscore.sub('_', h) for h in headerKeys]
                headerKeys.append("alt_name")
                headerKeys[:] = [
                    h if (h != "name") else "iauname" for h in headerKeys]
                headerKeys[:] = [
                    h if (h != "phase_days") else "phase" for h in headerKeys]
                nameIndex = headerKeys.index("iauname")
                headerKeys.append("astronote")

                results = []
                for row in table.findAll('tr'):
                    # print(row)
                    cells = row.findAll('td')
                    cellValues = []
                    cellValues[:] = [l.string for l in cells]
                    if len(cellValues):
                        try:
                            cellValues.append(cellValues[nameIndex].split(" ")[
                                              1].replace("[", "").replace("]", ""))
                        except:
                            cellValues.append(None)
                        cellValues[nameIndex] = cellValues[nameIndex].split()[
                            0]
                        cellValues.append(noteId)
                    if len(headerKeys) == len(cellValues):
                        transient = dict(zip(headerKeys, cellValues))
                        for h in headerKeys:
                            if "reported_" in h or "tns_" in h:
                                try:
                                    del transient[h]
                                except:
                                    pass
                        results.append(transient)

                insert_list_of_dictionaries_into_database_tables(
                    dbConn=self.dbConn,
                    log=self.log,
                    dictList=results,
                    dbTableName="astronotes_transients",
                    uniqueKeyList=["astronote", "iauname"],
                    dateModified=True,
                    dateCreated=True,
                    batchSize=2500,
                    replace=True,
                    # dbSettings=self.settings["database settings"]
                )

        self.log.debug('completed the ``_parse_html_to_database`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method

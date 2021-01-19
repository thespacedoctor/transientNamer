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


class astronotes(object):
    """
    *The worker class for the astronotes module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``dbConn`` -- database connection. Default *False*
        - ``settings`` -- the settings dictionary

    **Usage:**

    To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

    To initiate a astronotes object, use the following:

    ```eval_rst
    .. todo::

        - add usage info
        - create a sublime snippet for usage
        - create cl-util for this class
        - add a tutorial about ``astronotes`` to documentation
        - create a blog post about what ``astronotes`` does
    ```

    ```python
    usage code 
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
            settings=settings
        )
        downloadCount = an.download(
            cache_dir=settings["astronote-cache"], inLastDays=30)
        print(f"{downloadCount} new astronotes downloaded anc cached")
        ```

        ---

        ```eval_rst
        .. todo::

            - write a command-line tool for this method
            - update package tutorial with command-line tool info if needed
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
        for k, v in allNotes.items():
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

        ---

        ```eval_rst
        .. todo::

            - write a command-line tool for this method
            - update package tutorial with command-line tool info if needed
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
            from bs4 import BeautifulSoup
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

        **Key Arguments:**
            # -

        **Return:**
            - None

        **Usage:**

        ```python
        usage code 
        ```

        ---

        ```eval_rst
        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - write a command-line tool for this method
            - update package tutorial with command-line tool info if needed
        ```
        """
        self.log.debug('starting the ``notes_to_database`` method')

        # CREATE THE DATABASE TABLES IF THEY DON'T EXIST
        self._create_db_tables()

        # GENERATE A LIST OF FILE PATHS
        jsonNotes = []
        cache = self.settings["astronote-cache"]
        for d in os.listdir(cache):
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

        ---

        ```eval_rst
        .. todo::

            - write a command-line tool for this method
            - update package tutorial with command-line tool info if needed
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
            ) ENGINE=MyISAM AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;
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
            ) ENGINE=MyISAM AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;
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
              PRIMARY KEY (`primaryId`),
              UNIQUE KEY `astronote_iauname` (`astronote`,`iauname`),
              UNIQUE KEY `astronote_alt_name` (`alt_name`,`astronote`)
            ) ENGINE=MyISAM AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;

        """)

        for sqlQuery in sqlQueries:
            writequery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn
            )

        self.log.debug('completed the ``_create_db_tables`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method

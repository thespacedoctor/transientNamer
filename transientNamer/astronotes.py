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


class astronotes(object):
    """
    *The worker class for the astronotes module*

    **Key Arguments:**
        - ``log`` -- logger
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
    # Initialisation
    # 1. @flagged: what are the unique attrributes for each object? Add them
    # to __init__

    def __init__(
            self,
            log,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'astronotes' object")
        self.settings = settings
        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

        # Initial Actions

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
            - None

        **Usage:**

        ```python
        from transientNamer import astronotes
        an = astronotes(
            log=log,
            settings=settings
        )
        an.download(
            cache_dir=settings["astronote-cache"], inLastDays=30)
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

        self.log.debug('completed the ``download`` method')
        return None

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

    # use the tab-trigger below for new method
    # xt-class-method

#!/usr/local/bin/python
# encoding: utf-8
"""
*Search the Transient Name Server with various search constraints*

:Author:
    David Young
"""
from __future__ import print_function
from builtins import str
from builtins import object
import sys
import os
import re
import requests
requests.packages.urllib3.disable_warnings()
import copy
import collections
from operator import itemgetter
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from datetime import datetime, date, time, timedelta
import time as timesleep
from fundamentals.files import list_of_dictionaries_to_mysql_inserts
from fundamentals.renderer import list_of_dictionaries
from astrocalc.coords import unit_conversion
import time


class search(object):
    """
    *Search the Transient Name Server with various search constraints*

    **Key Arguments**

    - ``log`` -- logger
    - ``settings`` -- the settings dictionary
    - ``ra`` -- RA of the location being checked
    - ``dec`` -- DEC of the location being searched
    - ``radiusArcsec`` - the radius of the conesearch to perform against the TNS
    - ``name`` -- name of the object to search the TNS for
    - ``discInLastDays`` -- search the TNS for transient reported in the last X days
    - ``comments`` -- print the comments from the TNS, note these can be long making table outputs somewhat unreadable. Default *False*


    **Usage**

    To initiate a search object to search the TNS via an object name (either TNS or survey names accepted):

    ```python
    from transientNamer import search
    tns = search(
        log=log,
        name="Gaia16bbi"
    )
    ```

    or for a conesearch use something similar to:

    ```python
    from transientNamer import search
    tns = search(
        log=log,
        ra="06:50:36.74",
        dec="+31:06:44.7",
        radiusArcsec=5
    )
    ```

    Note the search method can accept coordinates in sexagesimal or decimal defree formats.

    To list all new objects reported in the last three weeks, then use:

    ```python
    from transientNamer import search
    tns = search(
        log=log,
        discInLastDays=21
    )
    ```

    """
    # Initialisation

    def __init__(
            self,
            log,
            ra="",
            dec="",
            radiusArcsec="",
            name="",
            discInLastDays="",
            settings=False,
            comments=False
    ):
        self.log = log
        log.debug("instansiating a new 'search' object")
        self.settings = settings
        self.ra = ra
        self.dec = dec
        self.radiusArcsec = radiusArcsec
        self.comments = comments
        self.name = name
        self.internal_name = ""
        self.discInLastDays = discInLastDays
        self.page = 0
        self.batchSize = 500

        # CREATE THE TIME-RANGE WINDOW TO SEARCH TNS
        if not discInLastDays:
            self.discInLastDays = ""
            self.period_units = ""
        else:
            self.discInLastDays = int(discInLastDays)
            self.period_units = "days"

        # DETERMINE IF WE HAVE A TNS OR INTERAL SURVEY NAME
        if self.name:
            matchObject = re.match(r'^((SN|AT) ?)?(\d{4}\w{1,6})', self.name)
            if matchObject:
                self.name = matchObject.group(3)
            else:
                self.internal_name = self.name
                self.name = ""

        # DO THE SEARCH OF THE TNS AND COMPILE THE RESULTS INTO SEPARATE RESULT
        # SETS
        self.sourceResultsList, self.photResultsList, self.specResultsList, self.relatedFilesResultsList = self._query_tns()
        self.sourceResults = list_of_dictionaries(
            log=log,
            listOfDictionaries=self.sourceResultsList
        )
        self.photResults = list_of_dictionaries(
            log=log,
            listOfDictionaries=self.photResultsList
        )
        self.specResults = list_of_dictionaries(
            log=log,
            listOfDictionaries=self.specResultsList
        )
        self.relatedFilesResults = list_of_dictionaries(
            log=log,
            listOfDictionaries=self.relatedFilesResultsList
        )

        return None

    @property
    def sources(
            self):
        """*The results of the search returned as a python list of dictionaries*

        **Usage**

        ```python
        sources = tns.sources
        ```

        """
        sourceResultsList = []
        sourceResultsList[:] = [dict(l) for l in self.sourceResultsList]
        return sourceResultsList

    @property
    def spectra(
            self):
        """*The associated source spectral data*

        **Usage**

        ```python
        sourceSpectra = tns.spectra
        ```

        """
        specResultsList = []
        specResultsList[:] = [dict(l) for l in self.specResultsList]
        return specResultsList

    @property
    def files(
            self):
        """*The associated source files*

        **Usage**

        ```python
        sourceFiles = tns.files
        ```

        """
        relatedFilesResultsList = []
        relatedFilesResultsList[:] = [dict(l)
                                      for l in self.relatedFilesResultsList]
        return relatedFilesResultsList

    @property
    def photometry(
            self):
        """*The associated source photometry*

        **Usage**

        ```python
        sourcePhotometry = tns.photometry
        ```

        """
        photResultsList = []
        photResultsList[:] = [dict(l) for l in self.photResultsList]
        return photResultsList

    @property
    def url(
            self):
        """*The generated URL used for searching of the TNS*

        **Usage**

        ```python
        searchURL = tns.url
        ```

        """

        return self._searchURL

    def csv(
            self,
            dirPath=None):
        """*Render the results in csv format*

        **Key Arguments**

        - ``dirPath`` -- the path to the directory to save the rendered results to. Default *None*


        **Return**

        - `csvSources` -- the top-level transient data
        - `csvPhot` -- all photometry associated with the transients
        - `csvSpec` -- all spectral data associated with the transients
        - `csvFiles`  -- all files associated with the matched transients found on the tns


        **Usage**

        To render the results in csv format:

        ```python
        csvSources, csvPhot, csvSpec, csvFiles  = tns.csv()
        print(csvSources)
        ```

        ```text
        TNSId,TNSName,discoveryName,discSurvey,raSex,decSex,raDeg,decDeg,transRedshift,specType,discMag,discMagFilter,discDate,objectUrl,hostName,hostRedshift,separationArcsec,separationNorthArcsec,separationEastArcsec
        2016asf,SN2016asf,ASASSN-16cs,ASAS-SN,06:50:36.73,+31:06:45.36,102.6530,31.1126,0.021,SN Ia,17.1,V-Johnson,2016-03-06 08:09:36,https://www.wis-tns.org/object/2016asf,KUG 0647+311,,0.66,0.65,-0.13
        ```

        You can save the results to file by passing in a directory path within which to save the files to. The four flavours of data (sources, photometry, spectra and files) are saved to separate files but all data can be assoicated with its transient source using the transient's unique `TNSId`.

        ```python
        tns.csv("~/tns")
        ```

        .. image:: https://i.imgur.com/BwwqMBg.png
            :width: 800px
            :alt: csv output

        """

        if dirPath:
            p = self._file_prefix()
            csvSources = self.sourceResults.csv(
                filepath=dirPath + "/" + p + "sources.csv")
            csvPhot = self.photResults.csv(
                filepath=dirPath + "/" + p + "phot.csv")
            csvSpec = self.specResults.csv(
                filepath=dirPath + "/" + p + "spec.csv")
            csvFiles = self.relatedFilesResults.csv(
                filepath=dirPath + "/" + p + "relatedFiles.csv")
        else:
            csvSources = self.sourceResults.csv()
            csvPhot = self.photResults.csv()
            csvSpec = self.specResults.csv()
            csvFiles = self.relatedFilesResults.csv()
        return csvSources, csvPhot, csvSpec, csvFiles

    def json(
            self,
            dirPath=None):
        """*Render the results in json format*

        **Key Arguments**

        - ``dirPath`` -- the path to the directory to save the rendered results to. Default *None*


        **Return**

        - `jsonSources` -- the top-level transient data
        - `jsonPhot` -- all photometry associated with the transients
        - `jsonSpec` -- all spectral data associated with the transients
        - `jsonFiles`  -- all files associated with the matched transients found on the tns


        **Usage**

        To render the results in json format:

        ```python
        jsonSources, jsonPhot, jsonSpec, jsonFiles  = tns.json()
        print(jsonSources)
        ```

        ```text
        [
            {
                "TNSId": "2016asf",
                "TNSName": "SN2016asf",
                "decDeg": 31.1126,
                "decSex": "+31:06:45.36",
                "discDate": "2016-03-06 08:09:36",
                "discMag": "17.1",
                "discMagFilter": "V-Johnson",
                "discSurvey": "ASAS-SN",
                "discoveryName": "ASASSN-16cs",
                "hostName": "KUG 0647+311",
                "hostRedshift": null,
                "objectUrl": "https://www.wis-tns.org/object/2016asf",
                "raDeg": 102.65304166666667,
                "raSex": "06:50:36.73",
                "separationArcsec": "0.66",
                "separationEastArcsec": "-0.13",
                "separationNorthArcsec": "0.65",
                "specType": "SN Ia",
                "transRedshift": "0.021"
            }
        ]
        ```

        You can save the results to file by passing in a directory path within which to save the files to. The four flavours of data (sources, photometry, spectra and files) are saved to separate files but all data can be assoicated with its transient source using the transient's unique `TNSId`.

        ```python
        tns.json("~/tns")
        ```

        .. image:: https://i.imgur.com/wAHqARI.png
            :width: 800px
            :alt: json output

        """

        if dirPath:
            p = self._file_prefix()
            jsonSources = self.sourceResults.json(
                filepath=dirPath + "/" + p + "sources.json")
            jsonPhot = self.photResults.json(
                filepath=dirPath + "/" + p + "phot.json")
            jsonSpec = self.specResults.json(
                filepath=dirPath + "/" + p + "spec.json")
            jsonFiles = self.relatedFilesResults.json(
                filepath=dirPath + "/" + p + "relatedFiles.json")
        else:
            jsonSources = self.sourceResults.json()
            jsonPhot = self.photResults.json()
            jsonSpec = self.specResults.json()
            jsonFiles = self.relatedFilesResults.json()
        return jsonSources, jsonPhot, jsonSpec, jsonFiles

    def yaml(
            self,
            dirPath=None):
        """*Render the results in yaml format*

        **Key Arguments**

        - ``dirPath`` -- the path to the directory to save the rendered results to. Default *None*


        **Return**

        - `yamlSources` -- the top-level transient data
        - `yamlPhot` -- all photometry associated with the transients
        - `yamlSpec` -- all spectral data associated with the transients
        - `yamlFiles`  -- all files associated with the matched transients found on the tns


        **Usage**

        To render the results in yaml format:

        ```python
        yamlSources, yamlPhot, yamlSpec, yamlFiles  = tns.yaml()
        print(yamlSources)
        ```

        ```text
        - TNSId: 2016asf
          TNSName: SN2016asf
          decDeg: 31.1126
          decSex: '+31:06:45.36'
          discDate: '2016-03-06 08:09:36'
          discMag: '17.1'
          discMagFilter: V-Johnson
          discSurvey: ASAS-SN
          discoveryName: ASASSN-16cs
          hostName: KUG 0647+311
          hostRedshift: null
          objectUrl: https://www.wis-tns.org/object/2016asf
          raDeg: 102.65304166666667
          raSex: '06:50:36.73'
          separationArcsec: '0.66'
          separationEastArcsec: '-0.13'
          separationNorthArcsec: '0.65'
          specType: SN Ia
          transRedshift: '0.021'
        ```

        You can save the results to file by passing in a directory path within which to save the files to. The four flavours of data (sources, photometry, spectra and files) are saved to separate files but all data can be assoicated with its transient source using the transient's unique `TNSId`.

        ```python
        tns.yaml("~/tns")
        ```

        .. image:: https://i.imgur.com/ZpJIC6p.png
            :width: 800px
            :alt: yaml output

        """

        if dirPath:
            p = self._file_prefix()
            yamlSources = self.sourceResults.yaml(
                filepath=dirPath + "/" + p + "sources.yaml")
            yamlPhot = self.photResults.yaml(
                filepath=dirPath + "/" + p + "phot.yaml")
            yamlSpec = self.specResults.yaml(
                filepath=dirPath + "/" + p + "spec.yaml")
            yamlFiles = self.relatedFilesResults.yaml(
                filepath=dirPath + "/" + p + "relatedFiles.yaml")
        else:
            yamlSources = self.sourceResults.yaml()
            yamlPhot = self.photResults.yaml()
            yamlSpec = self.specResults.yaml()
            yamlFiles = self.relatedFilesResults.yaml()
        return yamlSources, yamlPhot, yamlSpec, yamlFiles

    def markdown(
            self,
            dirPath=None):
        """*Render the results in markdown format*

        **Key Arguments**

        - ``dirPath`` -- the path to the directory to save the rendered results to. Default *None*


        **Return**

        - `markdownSources` -- the top-level transient data
        - `markdownPhot` -- all photometry associated with the transients
        - `markdownSpec` -- all spectral data associated with the transients
        - `markdownFiles`  -- all files associated with the matched transients found on the tns


        **Usage**

        To render the results in markdown table format:

        ```python
        markdownSources, markdownPhot, markdownSpec, markdownFiles  = tns.markdown()
        print(markdownSources)
        ```

        ```text
        | TNSId    | TNSName    | discoveryName  | discSurvey  | raSex        | decSex        | raDeg     | decDeg   | transRedshift  | specType  | discMag  | discMagFilter  | discDate             | objectUrl                                     | hostName      | hostRedshift  | separationArcsec  | separationNorthArcsec  | separationEastArcsec  |
        |:---------|:-----------|:---------------|:------------|:-------------|:--------------|:----------|:---------|:---------------|:----------|:---------|:---------------|:---------------------|:----------------------------------------------|:--------------|:--------------|:------------------|:-----------------------|:----------------------|
        | 2016asf  | SN2016asf  | ASASSN-16cs    | ASAS-SN     | 06:50:36.73  | +31:06:45.36  | 102.6530  | 31.1126  | 0.021          | SN Ia     | 17.1     | V-Johnson      | 2016-03-06 08:09:36  | https://www.wis-tns.org/object/2016asf  | KUG 0647+311  |               | 0.66              | 0.65                   | -0.13                 |
        ```

        You can save the results to file by passing in a directory path within which to save the files to. The four flavours of data (sources, photometry, spectra and files) are saved to separate files but all data can be assoicated with its transient source using the transient's unique `TNSId`.

        ```python
        tns.markdown("~/tns")
        ```

        .. image:: https://i.imgur.com/AYLBQoJ.png
            :width: 800px
            :alt: markdown output

        """

        if dirPath:
            p = self._file_prefix()
            markdownSources = self.sourceResults.markdown(
                filepath=dirPath + "/" + p + "sources.md")
            markdownPhot = self.photResults.markdown(
                filepath=dirPath + "/" + p + "phot.md")
            markdownSpec = self.specResults.markdown(
                filepath=dirPath + "/" + p + "spec.md")
            markdownFiles = self.relatedFilesResults.markdown(
                filepath=dirPath + "/" + p + "relatedFiles.md")
        else:
            markdownSources = self.sourceResults.markdown()
            markdownPhot = self.photResults.markdown()
            markdownSpec = self.specResults.markdown()
            markdownFiles = self.relatedFilesResults.markdown()
        return markdownSources, markdownPhot, markdownSpec, markdownFiles

    def table(
            self,
            dirPath=None):
        """*Render the results as an ascii table*

        **Key Arguments**

        - ``dirPath`` -- the path to the directory to save the rendered results to. Default *None*


        **Return**

        - `tableSources` -- the top-level transient data
        - `tablePhot` -- all photometry associated with the transients
        - `tableSpec` -- all spectral data associated with the transients
        - `tableFiles`  -- all files associated with the matched transients found on the tns


        **Usage**

        To render the results in ascii table format:

        ```python
        tableSources, tablePhot, tableSpec, tableFiles  = tns.table()
        print(tableSources)
        ```

        ```text
        +----------+------------+----------------+-------------+--------------+---------------+-----------+----------+----------------+-----------+----------+----------------+----------------------+-----------------------------------------------+---------------+---------------+-------------------+------------------------+-----------------------+
        | TNSId    | TNSName    | discoveryName  | discSurvey  | raSex        | decSex        | raDeg     | decDeg   | transRedshift  | specType  | discMag  | discMagFilter  | discDate             | objectUrl                                     | hostName      | hostRedshift  | separationArcsec  | separationNorthArcsec  | separationEastArcsec  |
        +----------+------------+----------------+-------------+--------------+---------------+-----------+----------+----------------+-----------+----------+----------------+----------------------+-----------------------------------------------+---------------+---------------+-------------------+------------------------+-----------------------+
        | 2016asf  | SN2016asf  | ASASSN-16cs    | ASAS-SN     | 06:50:36.73  | +31:06:45.36  | 102.6530  | 31.1126  | 0.021          | SN Ia     | 17.1     | V-Johnson      | 2016-03-06 08:09:36  | https://www.wis-tns.org/object/2016asf  | KUG 0647+311  |               | 0.66              | 0.65                   | -0.13                 |
        +----------+------------+----------------+-------------+--------------+---------------+-----------+----------+----------------+-----------+----------+----------------+----------------------+-----------------------------------------------+---------------+---------------+-------------------+------------------------+-----------------------+
        ```

        You can save the results to file by passing in a directory path within which to save the files to. The four flavours of data (sources, photometry, spectra and files) are saved to separate files but all data can be assoicated with its transient source using the transient's unique `TNSId`.

        ```python
        tns.table("~/tns")
        ```

        .. image:: https://i.imgur.com/m09M0ho.png
            :width: 800px
            :alt: ascii files

        """

        if dirPath:
            p = self._file_prefix()
            tableSources = self.sourceResults.table(
                filepath=dirPath + "/" + p + "sources.ascii")
            tablePhot = self.photResults.table(
                filepath=dirPath + "/" + p + "phot.ascii")
            tableSpec = self.specResults.table(
                filepath=dirPath + "/" + p + "spec.ascii")
            tableFiles = self.relatedFilesResults.table(
                filepath=dirPath + "/" + p + "relatedFiles.ascii")
        else:
            tableSources = self.sourceResults.table()
            tablePhot = self.photResults.table()
            tableSpec = self.specResults.table()
            tableFiles = self.relatedFilesResults.table()
        return tableSources, tablePhot, tableSpec, tableFiles

    def mysql(
            self,
            tableNamePrefix="TNS",
            dirPath=None):
        """*Render the results as MySQL Insert statements*

        **Key Arguments**

        - ``tableNamePrefix`` -- the prefix for the database table names to assign the insert statements to. Default *TNS*.
        - ``dirPath`` -- the path to the directory to save the rendered results to. Default *None*


        **Return**

        - `mysqlSources` -- the top-level transient data
        - `mysqlPhot` -- all photometry associated with the transients
        - `mysqlSpec` -- all spectral data associated with the transients
        - `mysqlFiles`  -- all files associated with the matched transients found on the tns


        **Usage**

        To render the results in mysql insert format:

        ```python
        mysqlSources, mysqlPhot, mysqlSpec, mysqlFiles  = tns.mysql("TNS")
        print(mysqlSources)
        ```

        ```text
        INSERT INTO `TNS_sources` (TNSId,TNSName,dateCreated,decDeg,decSex,discDate,discMag,discMagFilter,discSurvey,discoveryName,hostName,hostRedshift,objectUrl,raDeg,raSex,separationArcsec,separationEastArcsec,separationNorthArcsec,specType,transRedshift) VALUES ("2016asf" ,"SN2016asf" ,"2016-09-20T11:22:13" ,"31.1126" ,"+31:06:45.36" ,"2016-03-06 08:09:36" ,"17.1" ,"V-Johnson" ,"ASAS-SN" ,"ASASSN-16cs" ,"KUG 0647+311" ,null ,"https://www.wis-tns.org/object/2016asf" ,"102.653041667" ,"06:50:36.73" ,"0.66" ,"-0.13" ,"0.65" ,"SN Ia" ,"0.021")  ON DUPLICATE KEY UPDATE  TNSId="2016asf", TNSName="SN2016asf", dateCreated="2016-09-20T11:22:13", decDeg="31.1126", decSex="+31:06:45.36", discDate="2016-03-06 08:09:36", discMag="17.1", discMagFilter="V-Johnson", discSurvey="ASAS-SN", discoveryName="ASASSN-16cs", hostName="KUG 0647+311", hostRedshift=null, objectUrl="https://www.wis-tns.org/object/2016asf", raDeg="102.653041667", raSex="06:50:36.73", separationArcsec="0.66", separationEastArcsec="-0.13", separationNorthArcsec="0.65", specType="SN Ia", transRedshift="0.021", updated=1, dateLastModified=NOW() ;
        ```

        You can save the results to file by passing in a directory path within which to save the files to. The four flavours of data (sources, photometry, spectra and files) are saved to separate files but all data can be assoicated with its transient source using the transient's unique `TNSId`.

        ```python
        tns.mysql("TNS", "~/tns")
        ```

        .. image:: https://i.imgur.com/CozySPW.png
            :width: 800px
            :alt: mysql output

        """
        if dirPath:
            p = self._file_prefix()

            createStatement = """
CREATE TABLE `%(tableNamePrefix)s_sources` (
  `primaryId` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'An internal counter',
  `TNSId` varchar(20) NOT NULL,
  `TNSName` varchar(20) DEFAULT NULL,
  `dateCreated` datetime DEFAULT NULL,
  `decDeg` double DEFAULT NULL,
  `decSex` varchar(45) DEFAULT NULL,
  `discDate` datetime DEFAULT NULL,
  `discMag` double DEFAULT NULL,
  `discMagFilter` varchar(45) DEFAULT NULL,
  `discSurvey` varchar(100) DEFAULT NULL,
  `discoveryName` varchar(100) DEFAULT NULL,
  `objectUrl` varchar(200) DEFAULT NULL,
  `raDeg` double DEFAULT NULL,
  `raSex` varchar(45) DEFAULT NULL,
  `specType` varchar(100) DEFAULT NULL,
  `transRedshift` double DEFAULT NULL,
  `updated` tinyint(4) DEFAULT '0',
  `dateLastModified` datetime DEFAULT NULL,
  `hostName` VARCHAR(100) NULL DEFAULT NULL,
  `hostRedshift` DOUBLE NULL DEFAULT NULL, 
  `survey` VARCHAR(100) NULL DEFAULT NULL,
  PRIMARY KEY (`primaryId`),
  UNIQUE KEY `tnsid` (`TNSId`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=latin1;
            """ % locals()

            mysqlSources = self.sourceResults.mysql(
                tableNamePrefix + "_sources", filepath=dirPath + "/" + p + "sources.sql", createStatement=createStatement)

            createStatement = """
CREATE TABLE `%(tableNamePrefix)s_photometry` (
  `primaryId` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'An internal counter',
  `TNSId` varchar(20) NOT NULL,
  `dateCreated` datetime DEFAULT CURRENT_TIMESTAMP,
  `exptime` double DEFAULT NULL,
  `filter` varchar(100) DEFAULT NULL,
  `limitingMag` tinyint(4) DEFAULT NULL,
  `mag` double DEFAULT NULL,
  `magErr` double DEFAULT NULL,
  `magUnit` varchar(100) DEFAULT NULL,
  `objectName` varchar(100) DEFAULT NULL,
  `obsdate` datetime DEFAULT NULL,
  `reportAddedDate` datetime DEFAULT NULL,
  `suggestedType` varchar(100) DEFAULT NULL,
  `survey` varchar(100) DEFAULT NULL,
  `telescope` varchar(100) DEFAULT NULL,
  `updated` tinyint(4) DEFAULT '0',
  `dateLastModified` datetime DEFAULT NULL,
  `remarks` VARCHAR(800) NULL DEFAULT NULL,
  `sourceComment` VARCHAR(800) NULL DEFAULT NULL,
  PRIMARY KEY (`primaryId`),
  UNIQUE KEY `tnsid_survey_obsdate` (`TNSId`,`survey`,`obsdate`),
  UNIQUE INDEX `u_tnsid_survey_obsdate` (`TNSId` ASC, `survey` ASC, `obsdate` ASC),
  UNIQUE INDEX `u_tnsid_obsdate_objname` (`TNSId` ASC, `obsdate` ASC, `objectName` ASC)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=latin1;
            """ % locals()

            mysqlPhot = self.photResults.mysql(
                tableNamePrefix + "_photometry", filepath=dirPath + "/" + p + "phot.sql", createStatement=createStatement)

            createStatement = """
CREATE TABLE `%(tableNamePrefix)s_spectra` (
  `primaryId` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'An internal counter',
  `TNSId` varchar(45) NOT NULL,
  `TNSuser` varchar(45) DEFAULT NULL,
  `dateCreated` datetime DEFAULT CURRENT_TIMESTAMP,
  `exptime` double DEFAULT NULL,
  `obsdate` datetime DEFAULT NULL,
  `reportAddedDate` datetime DEFAULT NULL,
  `specType` varchar(100) DEFAULT NULL,
  `survey` varchar(100) DEFAULT NULL,
  `telescope` varchar(100) DEFAULT NULL,
  `transRedshift` double DEFAULT NULL,
  `updated` tinyint(4) DEFAULT '0',
  `dateLastModified` datetime DEFAULT NULL,
  `remarks` VARCHAR(800) NULL DEFAULT NULL,
  `sourceComment` VARCHAR(800) NULL DEFAULT NULL,
  PRIMARY KEY (`primaryId`),
  UNIQUE KEY `u_tnsid_survey_obsdate` (`TNSId`,`survey`,`obsdate`),
  UNIQUE KEY `u_id_user_obsdate` (`TNSId`,`TNSuser`,`obsdate`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=latin1;
            """ % locals()

            mysqlSpec = self.specResults.mysql(
                tableNamePrefix + "_spectra", filepath=dirPath + "/" + p + "spec.sql", createStatement=createStatement)

            createStatement = """
CREATE TABLE `%(tableNamePrefix)s_files` (
  `primaryId` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'An internal counter',
  `TNSId` varchar(100) NOT NULL,
  `dateCreated` datetime DEFAULT CURRENT_TIMESTAMP,
  `dateObs` datetime DEFAULT NULL,
  `filename` varchar(200) DEFAULT NULL,
  `spec1phot2` tinyint(4) DEFAULT NULL,
  `url` varchar(800) DEFAULT NULL,
  `updated` tinyint(4) DEFAULT '0',
  `dateLastModified` datetime DEFAULT NULL,
  `comment` VARCHAR(800) NULL DEFAULT NULL,
  PRIMARY KEY (`primaryId`),
  UNIQUE KEY `tnsid_url` (`TNSId`,`url`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=latin1;
            """ % locals()

            mysqlFiles = self.relatedFilesResults.mysql(
                tableNamePrefix + "_files", filepath=dirPath + "/" + p + "relatedFiles.sql", createStatement=createStatement)
        else:
            mysqlSources = self.sourceResults.mysql(
                tableNamePrefix + "_sources")
            mysqlPhot = self.photResults.mysql(tableNamePrefix + "_photometry")
            mysqlSpec = self.specResults.mysql(tableNamePrefix + "_spectra")
            mysqlFiles = self.relatedFilesResults.mysql(
                tableNamePrefix + "_files")
        return mysqlSources, mysqlPhot, mysqlSpec, mysqlFiles

    def _query_tns(self):
        """
        *determine how to query the TNS, send query and parse the results*

        **Return**

        - ``results`` -- a list of dictionaries (one dictionary for each result set returned from the TNS)

        """
        self.log.debug('starting the ``get`` method')

        sourceTable = []
        photoTable = []
        specTable = []
        relatedFilesTable = []

        # THIS stop IS TO KEEP TRACK OF THE TNS PAGINATION IF MANY RESULT PAGES
        # ARE RETURNED
        stop = False

        sourceCount = 0
        failedCount = 0
        while not stop:

            status_code, content, self._searchURL = self._get_tns_search_results()

            if status_code != 200:
                self.log.error(
                    'cound not get the search reuslts from the TNS, HTML error code %(status_code)s ' % locals())
                # IF FAILED TOO MANY TIME - RETURN WHAT WE HAVE
                if failedCount > 1:
                    return sourceTable, photoTable, specTable, relatedFilesTable
                failedCount += 1

                time.sleep(2)
                continue

            if "No results found" in content:
                print("No results found")
                return sourceTable, photoTable, specTable, relatedFilesTable

            if self._parse_transient_rows(content, True) < self.batchSize:
                stop = True
            else:
                self.page += 1
                thisPage = self.page
                print(
                    "Downloaded %(thisPage)s page(s) from the TNS. %(sourceCount)s transients parsed so far." % locals())
                sourceCount += self.batchSize
                # print "\t" + self._searchURL
                timesleep.sleep(1)

            # PARSE ALL ROWS RETURNED
            for transientRow in self._parse_transient_rows(content):

                # TOP LEVEL DISCOVERY CONTENT
                sourceContent = transientRow.group()
                discInfo, TNSId = self._parse_discovery_information(
                    sourceContent)
                sourceTable.append(discInfo)

                # PHOTOMETERY
                phot, relatedFiles = self._parse_photometry_data(
                    sourceContent, TNSId)
                photoTable += phot
                relatedFilesTable += relatedFiles

                # SPECTRA
                spec, relatedFiles = self._parse_spectral_data(
                    sourceContent, TNSId)
                specTable += spec
                relatedFilesTable += relatedFiles

        # SORT BY SEPARATION FROM THE SEARCH COORDINATES
        try:
            sourceTable = sorted(sourceTable, key=itemgetter(
                'separationArcsec'), reverse=False)
        except:
            pass

        self.log.debug('completed the ``get`` method')
        return sourceTable, photoTable, specTable, relatedFilesTable

    def _get_tns_search_results(
            self):
        """
        *query the tns and result the response*
        """
        self.log.debug('starting the ``_get_tns_search_results`` method')

        try:
            response = requests.get(
                url="https://www.wis-tns.org/search",
                params={
                    "page": self.page,
                    "ra": self.ra,
                    "decl": self.dec,
                    "radius": self.radiusArcsec,
                    "name": self.name,
                    "internal_name": self.internal_name,
                    "discovered_period_units": self.period_units,
                    "discovered_period_value": self.discInLastDays,
                    "num_page": self.batchSize,
                    "display[redshift]": "1",
                    "display[hostname]": "1",
                    "display[host_redshift]": "1",
                    "display[source_group_name]": "1",
                    "display[internal_name]": "1",
                    "display[spectra_count]": "1",
                    "display[discoverymag]": "1",
                    "display[discmagfilter]": "1",
                    "display[discoverydate]": "1",
                    "display[discoverer]": "1",
                    "display[sources]": "1",
                    "display[bibcode]": "1",
                },
            )

        except requests.exceptions.RequestException:
            print('HTTP Request failed')

        self.log.debug('completed the ``_get_tns_search_results`` method')
        try:
            # PYTHON 3
            return response.status_code, str(response.content, 'utf-8'), response.url
        except:
            # PYTHON 2
            return response.status_code, response.content, response.url

    def _file_prefix(
            self):
        """*Generate a file prefix based on the type of search for saving files to disk*

        **Return**

        - ``prefix`` -- the file prefix

        """
        self.log.debug('starting the ``_file_prefix`` method')

        if self.ra:
            now = datetime.now()
            prefix = now.strftime("%Y%m%dt%H%M%S%f_tns_conesearch_")
        elif self.name:
            prefix = self.name + "_tns_conesearch_"
        elif self.internal_name:
            prefix = self.internal_name + "_tns_conesearch_"
        elif self.discInLastDays:
            discInLastDays = str(self.discInLastDays)
            now = datetime.now()
            prefix = now.strftime(
                discInLastDays + "d_since_%Y%m%d_tns_conesearch_")

        self.log.debug('completed the ``_file_prefix`` method')
        return prefix

    def _parse_transient_rows(
            self,
            content,
            count=False):
        """* parse transient rows from the TNS result page content*

        **Key Arguments**

        - ``content`` -- the content from the TNS results page.
        - ``count`` -- return only the number of rows


        **Return**

        - ``transientRows``

        """
        self.log.debug('starting the ``_parse_transient_rows`` method')

        regexForRow = r"""\n([^\n]*?<a href="/object/.*?)(?=\n[^\n]*?<a href="/object/|<\!\-\- /\.section, /#content \-\->)"""

        if count:
            # A SINGLE SOURCE BLOCK
            matchedSources = re.findall(
                regexForRow,
                content,
                flags=re.S  # re.S
            )
            return len(matchedSources)

        # A SINGLE SOURCE BLOCK
        matchedSources = re.finditer(
            regexForRow,
            content,
            flags=re.S  # re.S
        )

        self.log.debug('completed the ``_parse_transient_rows`` method')
        return matchedSources

    def _parse_discovery_information(
            self,
            content):
        """* parse discovery information from one row on the TNS results page*

        **Key Arguments**

        - ``content`` -- a table row from the TNS results page.


        **Return**

        - ``discoveryData`` -- dictionary of results
        - ``TNSId`` -- the unique TNS id for the transient

        """
        self.log.debug('starting the ``_parse_discovery_information`` method')

        # ASTROCALC UNIT CONVERTER OBJECT
        converter = unit_conversion(
            log=self.log
        )

        matches = re.finditer(
            r"""<tr class="row-.*?"><td class="cell-id">(?P<tnsId>\d*?)</td><td class="cell-name"><a href="(?P<objectUrl>.*?)">(?P<TNSName>.*?)</a></td><td class="cell-.*?<td class="cell-ra">(?P<raSex>.*?)</td><td class="cell-decl">(?P<decSex>.*?)</td><td class="cell-ot_name">(?P<specType>.*?)</td><td class="cell-redshift">(?P<transRedshift>.*?)</td><td class="cell-hostname">(?P<hostName>.*?)</td><td class="cell-host_redshift">(?P<hostRedshift>.*?)</td><td class="cell-reporting_group_name">(?P<reportingSurvey>.*?)</td><td class="cell-source_group_name">(?P<discSurvey>.*?)</td>.*?<td class="cell-internal_name">(<a.*?>)?(?P<discoveryName>.*?)(</a>)?</td>.*?<td class="cell-discoverymag">(?P<discMag>.*?)</td><td class="cell-disc_filter_name">(?P<discMagFilter>.*?)</td><td class="cell-discoverydate">(?P<discDate>.*?)</td><td class="cell-discoverer">(?P<sender>.*?)</td>.*?</tr>""",
            content,
            flags=0  # re.S
        )
        discoveryData = []
        for match in matches:
            row = match.groupdict()
            for k, v in list(row.items()):
                row[k] = v.strip()
                if len(v) == 0:
                    row[k] = None
            if row["transRedshift"] == 0:
                row["transRedshift"] = None
            if row["TNSName"][0] in ["1", "2"]:
                row["TNSName"] = "SN" + row["TNSName"]
            row["objectUrl"] = "https://www.wis-tns.org" + \
                row["objectUrl"]

            # CONVERT COORDINATES TO DECIMAL DEGREES
            row["raDeg"] = converter.ra_sexegesimal_to_decimal(
                ra=row["raSex"]
            )
            row["decDeg"] = converter.dec_sexegesimal_to_decimal(
                dec=row["decSex"]
            )

            # IF THIS IS A COORDINATE SEARCH, ADD SEPARATION FROM
            # ORIGINAL QUERY COORDINATES
            if self.ra:
                # CALCULATE SEPARATION IN ARCSEC
                from astrocalc.coords import separations
                calculator = separations(
                    log=self.log,
                    ra1=self.ra,
                    dec1=self.dec,
                    ra2=row["raDeg"],
                    dec2=row["decDeg"],
                )
                angularSeparation, north, east = calculator.get()
                row["separationArcsec"] = angularSeparation
                row["separationNorthArcsec"] = north
                row["separationEastArcsec"] = east

            if not row["discSurvey"]:
                row["survey"] = row["sender"]

            del row["sender"]
            del row["tnsId"]
            row["TNSName"] = row["TNSName"].replace(" ", "")
            row["TNSId"] = row["TNSName"].replace(
                "SN", "").replace("AT", "")
            TNSId = row["TNSId"]

            # ORDER THE DICTIONARY FOR THIS ROW OF RESULTS
            orow = collections.OrderedDict()
            keyOrder = ["TNSId", "TNSName", "discoveryName", "discSurvey", "raSex", "decSex", "raDeg", "decDeg",
                        "transRedshift", "specType", "discMag", "discMagFilter", "discDate", "objectUrl", "hostName", "hostRedshift", "separationArcsec", "separationNorthArcsec", "separationEastArcsec"]
            for k, v in list(row.items()):
                if k not in keyOrder:
                    keyOrder.append(k)
            for k in keyOrder:
                try:
                    orow[k] = row[k]
                except:
                    self.log.info(
                        "`%(k)s` not found in the source data for %(TNSId)s" % locals())
                    pass
            discoveryData.append(row)

        self.log.debug('completed the ``_parse_discovery_information`` method')
        return discoveryData[0], TNSId

    def _parse_photometry_data(
            self,
            content,
            TNSId):
        """*parse photometry data from a row in the tns results content*

        **Key Arguments**

         - ``content`` -- a table row from the TNS results page
         - ``TNSId`` -- the tns id of the transient


        **Return**

        - ``photData`` -- a list of dictionaries of the photometry data
        - ``relatedFilesTable`` -- a list of dictionaries of transient photometry related files 

        """
        self.log.debug('starting the ``_parse_photometry_data`` method')

        photData = []
        relatedFilesTable = []

        # AT REPORT BLOCK
        ATBlock = re.search(
            r"""<tr class=[^\n]*?AT reports.*?(?=<tr class=[^\n]*?Classification reports|$)""",
            content,
            flags=re.S  # re.S
        )

        if ATBlock:
            ATBlock = ATBlock.group()
            reports = re.finditer(
                r"""<tr class="row-[^"]*"><td class="cell-id">.*?</table>""",
                ATBlock,
                flags=re.S  # re.S
            )

            relatedFiles = self._parse_related_files(ATBlock)

            for r in reports:
                header = re.search(
                    r"""<tr class="row[^"]*".*?time_received">(?P<reportAddedDate>[^<]*).*?user_name">(?P<sender>[^<]*).*?reporter_name">(?P<reporters>[^<]*).*?reporting_group_name">(?P<reportingGroup>[^<]*).*?source_group_name">(?P<surveyGroup>[^<]*).*?ra">(?P<ra>[^<]*).*?decl">(?P<dec>[^<]*).*?discovery_date">(?P<obsDate>[^<]*).*?flux">(?P<mag>[^<]*).*?filter_name">(?P<magFilter>[^<]*).*?related_files">(?P<relatedFiles>[^<]*).*?type_name">(?P<suggestedType>[^<]*).*?hostname">(?P<hostName>[^<]*).*?host_redshift">(?P<hostRedshift>[^<]*).*?internal_name">(?P<objectName>[^<]*).*?groups">(?P<survey>[^<]*).*?remarks">(?P<sourceComment>[^<]*)""",
                    r.group(),
                    flags=0  # re.S
                )
                try:
                    header = header.groupdict()
                except:
                    print(r.group())
                header["TNSId"] = TNSId

                del header["reporters"]
                del header["surveyGroup"]
                del header["hostName"]
                del header["hostRedshift"]
                del header["mag"]
                del header["magFilter"]
                del header["obsDate"]
                del header["ra"]
                del header["dec"]

                if not self.comments:
                    del header['sourceComment']
                else:
                    theseComments = header[
                        "sourceComment"].split("\n")
                    header["sourceComment"] = ""
                    for c in theseComments:
                        header["sourceComment"] += " " + c.strip()
                    header["sourceComment"] = header[
                        "sourceComment"].strip()[0:750]

                phot = re.finditer(
                    r"""<tr class="row\-[^"]*".*?obsdate">(?P<obsdate>[^<]*).*?flux">(?P<mag>[^<]*).*?fluxerr">(?P<magErr>[^<]*).*?limflux">(?P<limitingMag>[^<]*).*?unit_name">(?P<magUnit>[^<]*).*?filter_name">(?P<filter>[^<]*).*?tel_inst">(?P<telescope>[^<]*).*?exptime">(?P<exptime>[^<]*).*?observer">(?P<observer>[^<]*).*?-remarks">(?P<remarks>[^<]*)""",
                    r.group(),
                    flags=0  # re.S
                )
                filesAppended = False
                for p in phot:
                    p = p.groupdict()
                    del p["observer"]

                    if p["limitingMag"] and not p["mag"]:
                        p["mag"] = p["limitingMag"]
                        p["limitingMag"] = 1
                        p["remarks"] = p["remarks"].replace(
                            "[Last non detection]", "")
                    else:
                        p["limitingMag"] = 0

                    if not self.comments:
                        del p["remarks"]

                    p.update(header)

                    if p["relatedFiles"] and filesAppended == False:
                        filesAppended = True
                        for f in relatedFiles:
                            # ORDER THE DICTIONARY FOR THIS ROW OF
                            # RESULTS
                            thisFile = collections.OrderedDict()
                            thisFile["TNSId"] = TNSId
                            thisFile["filename"] = f[
                                "filepath"].split("/")[-1]
                            thisFile["url"] = f["filepath"]
                            if self.comments:
                                thisFile["comment"] = f[
                                    "fileComment"].replace("\n", " ")[0:750]
                            thisFile["dateObs"] = p["obsdate"]
                            thisFile["spec1phot2"] = 2
                            relatedFilesTable.append(thisFile)

                    if not p["survey"] and not p["objectName"]:
                        p["survey"] = p["sender"]

                    del p["relatedFiles"]
                    del p["sender"]

                    # ORDER THE DICTIONARY FOR THIS ROW OF RESULTS
                    orow = collections.OrderedDict()
                    keyOrder = ["TNSId", "survey", "obsdate", "filter", "limitingMag", "mag", "magErr",
                                "magUnit", "suggestedType", "telescope", "exptime", "reportAddedDate"]
                    for k, v in list(p.items()):
                        if k not in keyOrder:
                            keyOrder.append(k)
                    for k in keyOrder:
                        try:
                            orow[k] = p[k]
                        except:
                            self.log.info(
                                "`%(k)s` not found in the source data for %(TNSId)s" % locals())
                            pass

                    photData.append(orow)

        self.log.debug('completed the ``_parse_photometry_data`` method')
        return photData, relatedFilesTable

    def _parse_related_files(
            self,
            content):
        """*parse the contents for related files URLs and comments*

        **Key Arguments**

        - ``content`` -- the content to parse.


        **Return**

        - ``relatedFiles`` -- a list of dictionaries of transient related files 

        """
        self.log.debug('starting the ``_parse_related_files`` method')

        relatedFilesList = re.finditer(
            r"""<td class="cell-filename">.*?href="(?P<filepath>[^"]*).*?remarks">(?P<fileComment>[^<]*)""",
            content,
            flags=0  # re.S
        )

        relatedFiles = []
        for f in relatedFilesList:
            f = f.groupdict()
            relatedFiles.append(f)

        self.log.debug('completed the ``_parse_related_files`` method')
        return relatedFiles

    def _parse_spectral_data(
            self,
            content,
            TNSId):
        """*parse spectra data from a row in the tns results content*

        **Key Arguments**

         - ``content`` -- a table row from the TNS results page
         - ``TNSId`` -- the tns id of the transient


        **Return**

        - ``specData`` -- a list of dictionaries of the spectral data
        - ``relatedFilesTable`` -- a list of dictionaries of transient spectrum related files 

        """
        self.log.debug('starting the ``_parse_spectral_data`` method')

        specData = []
        relatedFilesTable = []

        # CLASSIFICATION BLOCK
        classBlock = re.search(
            r"""<tr class=[^\n]*?Classification reports.*$""",
            content,
            flags=re.S  # re.S
        )

        if classBlock:
            classBlock = classBlock.group()

            reports = re.finditer(
                r"""<tr class="row-[^"]*"><td class="cell-id">.*?</tbody>\s*</table>\s*</div></td> </tr>\s*</tbody>\s*</table>\s*</div></td> </tr>""",
                classBlock,
                flags=re.S  #
            )

            relatedFiles = self._parse_related_files(classBlock)

            for r in reports:

                header = re.search(
                    r"""<tr class="row.*?time_received">(?P<reportAddedDate>[^<]*).*?user_name">(?P<TNSuser>[^<]*).*?classifier_name">(?P<reporters>[^<]*).*?source_group_name">(?P<survey>[^<]*).*?-type">(?P<specType>[^<]*).*?-redshift">(?P<transRedshift>[^<]*).*?-related_files">(?P<relatedFiles>[^<]*).*?-groups">(?P<surveyGroup>[^<]*).*?-remarks">(?P<sourceComment>[^<]*)</td>""",
                    r.group(),
                    flags=re.S  # re.S
                )
                if not header:
                    continue

                header = header.groupdict()
                header["TNSId"] = TNSId

                del header["reporters"]
                del header["surveyGroup"]
                del header["survey"]

                if not self.comments:
                    del header['sourceComment']
                else:
                    theseComments = header[
                        "sourceComment"].split("\n")
                    header["sourceComment"] = ""
                    for c in theseComments:
                        header["sourceComment"] += " " + c.strip()
                    header["sourceComment"] = header[
                        "sourceComment"]

                spec = re.finditer(
                    r"""<tr class="row-.*?-obsdate">(?P<obsdate>[^<]*).*?-tel_inst">(?P<telescope>[^<]*).*?-exptime">(?P<exptime>[^<]*).*?-observer">(?P<sender>[^<]*).*?-reducer">(?P<reducer>[^<]*).*?-source_group_name">(?P<survey>[^<]*).*?-asciifile">(.*?<a href="(?P<filepath>[^"]*)".*?</a>)?.*?-fitsfile">(.*?<a href="(?P<fitsFilepath>[^"]*)".*?</a>)?.*?-groups">(?P<surveyGroup>[^<]*).*?-remarks">(?P<remarks>[^<]*)""",
                    r.group(),
                    flags=0  # re.S
                )
                filesAppended = False
                for s in spec:

                    s = s.groupdict()
                    del s["sender"]
                    del s["surveyGroup"]
                    del s["reducer"]

                    if not self.comments:
                        del s["remarks"]
                    else:
                        s["remarks"] = s["remarks"].replace('"', "'")[0:750]

                    s.update(header)

                    if s["relatedFiles"] and filesAppended == False:
                        filesAppended = True
                        for f in relatedFiles:
                            # ORDER THE DICTIONARY FOR THIS ROW OF
                            # RESULTS
                            thisFile = collections.OrderedDict()
                            thisFile["TNSId"] = TNSId
                            thisFile["filename"] = f[
                                "filepath"].split("/")[-1]
                            thisFile["url"] = f["filepath"]
                            if self.comments:
                                thisFile["comment"] = f[
                                    "fileComment"].replace("\n", " ").strip()
                            thisFile["dateObs"] = s["obsdate"]
                            thisFile["spec1phot2"] = 1
                            relatedFilesTable.append(thisFile)

                    for ffile in [s["filepath"], s["fitsFilepath"]]:
                        if ffile:
                            # ORDER THE DICTIONARY FOR THIS ROW OF
                            # RESULTS
                            thisFile = collections.OrderedDict()
                            thisFile["TNSId"] = TNSId
                            thisFile["filename"] = ffile.split(
                                "/")[-1]
                            thisFile["url"] = ffile
                            if self.comments:
                                thisFile["comment"] = ""
                            thisFile["dateObs"] = s["obsdate"]
                            thisFile["spec1phot2"] = 1
                            relatedFilesTable.append(thisFile)

                    del s["filepath"]
                    del s["fitsFilepath"]
                    del s["relatedFiles"]

                    # ORDER THE DICTIONARY FOR THIS ROW OF RESULTS
                    orow = collections.OrderedDict()
                    keyOrder = ["TNSId", "survey", "obsdate", "specType", "transRedshift",
                                "telescope", "exptime", "reportAddedDate", "TNSuser"]
                    for k, v in list(s.items()):
                        if k not in keyOrder:
                            keyOrder.append(k)
                    for k in keyOrder:
                        try:
                            orow[k] = s[k]
                        except:
                            self.log.info(
                                "`%(k)s` not found in the source data for %(TNSId)s" % locals())
                            pass

                    specData.append(orow)

        self.log.debug('completed the ``_parse_spectral_data`` method')
        return specData, relatedFilesTable

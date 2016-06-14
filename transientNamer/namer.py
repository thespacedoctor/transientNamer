#!/usr/local/bin/python
# encoding: utf-8
"""
*Add transients to the Transient Name Server. A check is first performed to make sure the object has not already been added by another survey.*

:Author:
    David Young

:Date Created:
    March 11, 2016

.. todo::
    
    @review: when complete pull all general functions and classes into dryxPython
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import mechanize
from fundamentals import tools


class namer():
    """
    *The worker class for the namer module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``ra`` -- RA of the object to add to the TNS
        - ``dec`` -- DEC of the object to add to the TNS
        - ``name`` -- Name of the object to add to the TNS
        - ``discoveryMJD`` -- the discovery MJD for the object
        - ``discoveryMag`` -- the discovery magnitude for the object
        - ``discoveryFilter`` -- the filter of the discovery magnitude

    .. todo::

        - @review: when complete, clean namer class
        - @review: when complete add logging
        - @review: when complete, decide whether to abstract class to another module
    """
    # Initialisation
    # 1. @flagged: what are the unique attrributes for each object? Add them
    # to __init__

    def __init__(
            self,
            log,
            ra,
            dec,
            name,
            discoveryMJD,
            discoveryMag,
            discoveryFilter,
            settings=False
    ):
        self.log = log
        log.debug("instansiating a new 'namer' object")
        self.settings = settings
        self.ra = ra
        self.dec = dec
        self.name = name
        self.discoveryMJD = discoveryMJD
        self.discoveryMag = discoveryMag
        self.discoveryFilter = discoveryFilter
        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes
        self.discoveryJD = discoveryMJD + 2400000.5

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

        # Initial Actions

        return None

    # 4. @flagged: what actions does each object have to be able to perform? Add them here
    # Method Attributes
    def get(self):
        """
        *get the namer object*

        **Return:**
            - ``namer``

        .. todo::

            - @review: when complete, clean get method
            - @review: when complete add logging
        """
        self.log.info('starting the ``get`` method')

        search = self._preliminary_search()
        if "No result" not in search:
            return

        self._submit_reports_to_tns()

        self.log.info('completed the ``get`` method')
        return namer

    def _preliminary_search(
            self):
        """
        *preliminary search*

        **Key Arguments:**
            # -

        **Return:**
            - None

        .. todo::

            - @review: when complete, clean _preliminary_search method
            - @review: when complete add logging
        """
        self.log.info('starting the ``_preliminary_search`` method')

        from transientNamer import search

        result = search(
            log=self.log,
            ra=self.ra,
            dec=self.dec,
            radiusArcsec=5,
            settings=self.settings
        ).get()

        self.log.info('completed the ``_preliminary_search`` method')
        return result

    # use the tab-trigger below for new method
    def _submit_reports_to_tns(
            self):
        """
        *submit reports to tns*
        """
        self.log.info('starting the ``_submit_reports_to_tns`` method')

        # WISEMAN RECORD SUBMISSION PARAMETERS
        url = "http://wis-tns.weizmann.ac.il/reports"
        # url = "http://sandbox-tns.weizmann.ac.il/reports"
        headers = [
            ("Referer", url),
            ("Cookie", self.settings["tns_cookie"]),
            ("Connection", "keep-alive"),
        ]

        # CREATE BROWSER
        br = mechanize.Browser()
        br.addheaders = headers

        r = br.open(url)
        br.select_form(nr=0)

        # CHOOSE ARCHIVAL INFO
        if self.dec > -29:
            sdss = ['1', ]  # SDSS
        else:
            sdss = ['2', ]  # DSS

        filterCode = None
        fluxUnits = None
        # CHOOSE THE GROUP AND ATTRIBUTES
        if "ps1" in self.name.lower():
            groupId = ['4', ]  # PANSTARRS
            reporters = """K. C. Chambers, M. E. Huber, H. Flewelling, E. A. Magnier, N. Primak, A. Schultz, (IfA, University of Hawaii), S. J. Smartt, K. W. Smith, (Queen's University Belfast), J. Tonry, C. Waters, (IfA, University of Hawaii) D. E. Wright, D. R. Young (Queen's University Belfast)"""
            fluxUnits = ['1', ]  # ABMAG
            filters = {
                "u": "20",
                "g": "21",
                "r": "22",
                "i": "23",
                "z": "24",
                "y": "25",
                "w": "26"
            }
            filterCode = [
                filters[self.discoveryFilter.lower()], ]
            inst = ["155", ]
            br.form["non_detection[archiveid]"] = sdss
        elif "lsq" in self.name.lower():
            groupId = ['20', ]  # LSQ
            reporters = """C. Baltay, N. Ellman, E. Hadjiyska, R. McKinnon, D. Rabinowitz, S. Rostami (Yale University), U. Feindt, M. Kowalski (Universitat Bonn), P. Nugent (LBL Berkeley)"""
            fluxUnits = ['1', ]  # ABMAG
            filters = {
                "gr-LSQ": "70",
            }
            filterCode = ["70", ]
            inst = [
                "158", ]
            # if row["lastNonDetectionDate"] and str(row["lastNonDetectionDate"])[0] == "2":
            #     br.form["non_detection[obsdate]"] = str(
            #         row["lastNonDetectionDate"])
            #     br.form["non_detection[limiting_flux]"] = "21.5"
            #     br.form["non_detection[flux_units]"] = fluxUnits
            #     br.form["non_detection[filter_value]"] = filterCode
            #     br.form["non_detection[instrument_value]"] = inst
            # else:
            #     br.form["non_detection[archiveid]"] = sdss
        elif "atlas" in self.name.lower():
            groupId = ['18', ]  # ATLAS
            reporters = """J. Tonry, L. Denneau, B. Stalder, A. Heinze, A. Sherstyuk (IfA, University of Hawaii), A. Rest (STScI), K. W. Smith, S. J. Smartt (Queen's University Belfast)"""
            fluxUnits = ['1', ]  # ABMAG
            filters = {
                "c": "71",
                "o": "72"
            }
            filterCode = [
                filters[self.discoveryFilter.lower()], ]
            inst = [
                "159", ]
            br.form["non_detection[archiveid]"] = sdss
        else:
            print "choose a survey"
            sys.exit(0)

        br.form["ra[value]"] = self.ra
        br.form["decl[value]"] = self.dec
        br.form["groupid"] = groupId
        br.form["proprietary_period_groups[]"] = groupId
        br.form["discovery_datetime"] = str(self.discoveryJD)
        br.form["internal_name"] = self.name

        br.form["photometry[photometry_group][0][obsdate]"] = str(
            self.discoveryJD)
        br.form["photometry[photometry_group][0][flux]"] = str(
            self.discoveryMag)
        br.form[
            "reporter"] = reporters
        br.form["photometry[photometry_group][0][flux_units]"] = fluxUnits
        br.form["photometry[photometry_group][0][filter_value]"] = filterCode
        br.form["photometry[photometry_group][0][instrument_value]"] = inst
        r = br.submit("op")

        self.log.info('completed the ``_submit_reports_to_tns`` method')
        return None

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx

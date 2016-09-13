#!/usr/local/bin/python
# encoding: utf-8
"""
*Search the Transient Name Server given a set of coordinates and a search radius*

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
import re
os.environ['TERM'] = 'vt100'
from fundamentals import tools


class search():
    """
    *The worker class for the search module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``ra`` -- RA of the location being checked
        - ``dec`` -- DEC of the location being searched
         - ``radiusArcsec`` - the radius of the conesearch to perform against the TNS. Default * 5 arcsec*

    .. todo::

        - @review: when complete, clean search class
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
            radiusArcsec=5,
            settings=False,


    ):
        self.log = log
        log.debug("instansiating a new 'search' object")
        self.settings = settings
        self.ra = ra
        self.dec = dec
        self.radiusArcsec = radiusArcsec
        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

        # Initial Actions

        return None

    # 4. @flagged: what actions does each object have to be able to perform? Add them here
    # Method Attributes
    def get(self):
        """
        *get the search object*

        **Return:**
            - ``search``

        .. todo::

            - @review: when complete, clean get method
            - @review: when complete add logging
        """
        self.log.info('starting the ``get`` method')

        status_code, content = self._query_the_tns()
        if status_code != 200:
            self.log.error(
                'cound not get the search reuslts from the TNS, HTML error code %(status_code)s ' % locals())
            return None

        if "No results found" in content:
            print "No results found"
            return "No results found"
        else:
            matchObject = re.search(
                r"""<td class="cell-internal_name">(.*?)</td""", content, re.S)
            match = matchObject.group(1)
            print "Match found: %(match)s" % locals()
            return "Match found: %(match)s" % locals()

        self.log.info('completed the ``get`` method')
        return search

    def _query_the_tns(
            self):
        """
        *query the tns*

        **Key Arguments:**
            # -

        **Return:**
            - None

        .. todo::

            - @review: when complete, clean _query_the_tns method
            - @review: when complete add logging
        """
        self.log.info('starting the ``_query_the_tns`` method')

        # Install the Python Requests library:
        # `pip install requests`

        import requests

        try:
            response = requests.get(
                url="http://wis-tns.weizmann.ac.il/search",
                params={
                    "name": "",
                    "name_like": "0",
                    "isTNS_AT": "all",
                    "public": "all",
                    "unclassified_at": "0",
                    "classified_sne": "0",
                    "ra": self.ra,
                    "decl": self.dec,
                    "radius": self.radiusArcsec,
                    "coords_unit": "arcsec",
                    "groupid[]": "null",
                    "type[]": "null",
                    "date_start[date]": "",
                    "date_end[date]": "",
                    "discovery_mag_min": "",
                    "discovery_mag_max": "",
                    "discoverer": "",
                    "redshift_min": "",
                    "redshift_max": "",
                    "spectra_count": "",
                    "internal_name": "",
                    "hostname": "",
                    "associated_groups[]": "null",
                    "num_page": "50",
                    "display[redshift]": "1",
                    "display[hostname]": "1",
                    "display[host_redshift]": "1",
                    "display[source_group_name]": "1",
                    "display[programs_name]": "0",
                    "display[internal_name]": "1",
                    "display[isTNS_AT]": "0",
                    "display[public]": "1",
                    "display[end_pop_period]": "0",
                    "display[spectra_count]": "1",
                    "display[discoverymag]": "1",
                    "display[discmagfilter]": "1",
                    "display[discoverydate]": "1",
                    "display[discoverer]": "1",
                    "display[sources]": "0",
                    "display[bibcode]": "0",
                },
            )
        except requests.exceptions.RequestException:
            print('HTTP Request failed')

        self.log.info('completed the ``_query_the_tns`` method')
        return response.status_code, response.content

    # use the tab-trigger below for new method
    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx

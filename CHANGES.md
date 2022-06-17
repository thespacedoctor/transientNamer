
## Release Notes

**v0.4.4 - June 17, 2022**

* **FIXED**: unit-tests failing due to throttling from TNS

**v0.4.3 - January 25, 2021**

* **FIXED**: call to settings file now explicit from command-line (was not required until tns-marker added)

**v0.4.2 - January 25, 2021**

* **REFACTOR:** requests will fail if TNS responds with any status other than 200
* **REFACTOR:** added user-agent header now required by TNS (needs added in the settings file)

**v0.4.1 - January 25, 2021**

* **FEATURE**:** you can now download and parse astronotes (including ability to add to MySQL database tables)
* **REFACTOR:** Updated URL to the new TNS URL <https://www.wis-tns.org>  

**v0.3.2 - December 21, 2020**

* **ENHANCEMENT**: now using discovered_period_value for discInLastDays. More efficient than adding range of obsdate.

**v0.3.1 - October 25, 2020**

* **FIXED:** bytes to string with utf-8 encoding bug stopping regexes from passing

**v0.3.0 - May 22, 2020**

* Now compatible with Python 3.*

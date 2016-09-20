transientNamer
==============

*Command-line tools for working with and interacting with the Transient
Naming Server*.

Usage
=====

    Documentation for transientNamer can be found here: http://transientNamer.readthedocs.org/en/stable

    Usage:
        transientNamer [-c] search <ra> <dec> <arcsecRadius> [<render> | mysql <tableNamePrefix>] [-o directory]
        transientNamer [-c] search <name> [<render> | mysql <tableNamePrefix>] [-o directory]
        transientNamer [-c] new <discInLastDays> [<render> | mysql <tableNamePrefix>] [-o directory]

    Commands:
        search                search the TNS and return the results
        new                   list newly discovered TNS objects

    Arguments:
        ra
        dec
        arcsecRadius
        name                  the name of the object the search for (TNS or survey name)
        render                output format for results. Options include json, csv, table, markdown, yaml
        tableNamePrefix       the prefix for the tables to write the mysql insert statements for
        dirPath               path to the directory to save the output to

    Options:
        -h, --help                           show this help message
        -v, --version                        show version
        -s, --settings                       the settings file
        -c, --withComments                   return TNS comments in result sets
        -o directory --output=directory      output to files in the directory path

Documentation
=============

Documentation for transientNamer is hosted by [Read the
Docs](http://transientNamer.readthedocs.org/en/stable/) (last [stable
version](http://transientNamer.readthedocs.org/en/stable/) and [latest
version](http://transientNamer.readthedocs.org/en/latest/)).

Installation
============

The easiest way to install transientNamer us to use `pip`:

    pip install transientNamer

Or you can clone the [github
repo](https://github.com/thespacedoctor/transientNamer) and install from
a local version of the code:

    git clone git@github.com:thespacedoctor/transientNamer.git
    cd transientNamer
    python setup.py install

To upgrade to the latest version of transientNamer use the command:

    pip install transientNamer --upgrade

Development
-----------

If you want to tinker with the code, then install in development mode.
This means you can modify the code from your cloned repo:

    git clone git@github.com:thespacedoctor/transientNamer.git
    cd transientNamer
    python setup.py develop

[Pull requests](https://github.com/thespacedoctor/transientNamer/pulls)
are welcomed!

Issues
------

Please report any issues
[here](https://github.com/thespacedoctor/transientNamer/issues).

License
=======

Copyright (c) 2016 David Young

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

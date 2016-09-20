Usage
======

.. code-block:: bash 
   
    
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
    

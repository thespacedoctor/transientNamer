

```bash 
    
    Documentation for transientNamer can be found here: http://transientNamer.readthedocs.org/en/stable
    
    Usage:
        transientNamer [-c] cone <ra> <dec> <arcsecRadius> [<render> | mysql <tableNamePrefix>] [-o directory]
        transientNamer [-c] search <name> [<render> | mysql <tableNamePrefix>] [-o directory]
        transientNamer [-c] new <reportedInLastDays> [<render> | mysql <tableNamePrefix>] [-o directory]
    
    Commands:
        cone                  perform a conesearch on the TNS
        search                perform a name search on the TNS
        new                   list newly reported TNS objects
        
    Arguments:
        ra
        dec
        arcsecRadius
        name                  the name of the object the search for (TNS or survey name)
        render                output format for results. Options include json, csv, table, markdown, yaml
        tableNamePrefix       the prefix for the tables to write the mysql insert statements for
        directory             path to the directory to save the output to
        reportedInLastDays    download and parse data reported within the last <n> days
        mysql                 generate mysql insert scripts
    
    Options:
        -h, --help                           show this help message
        -v, --version                        show version
        -s, --settings                       the settings file
        -c, --withComments                   return TNS comments in result sets
        -o directory, --output=directory     output to files in the directory path
    

```

# Caching and Parsing Astronotes

Before parsing the Astronote contents it's necessary to download the notes into a local cache to avoid redownloading every time you wish to parse them and (reduces strain placed on the TNS). Before you begin make sure you have set up the `astronote-cache` setting in the settings file (see [`initalisation`](../initalisation.md) instructions).

In the spirit of fair-usage the downloader will pause for 1 second in-between each individual note download.

## From the Command-Line

To cache the notes run the command:

```bash
transientNamer notes <reportedInLastDays>
```

So to cache notes from the last 10 days run `transientNamer notes 10`.

To also parse and import the cached notes into 3 MySQL database tables (`astronotes_content`, `astronotes_keywords`, `astronotes_transients`) run the same command but with the `--import` flag:

```bash
transientNamer --import notes <reportedInLastDays>
```

This will cause all unseen notes in the cache directory to be parsed and added to the database.

## From Python Script

To [`download`](./_api/transientNamer.astronotes.html#transientNamer.astronotes.astronotes.download) the notes from the last 30 days use the following snippet. 

```python
from transientNamer import astronotes
an = astronotes(
    log=log,
    dbConn=dbConn,
    settings=settings
)
downloadCount = an.download(
    cache_dir=settings["astronote-cache"], inLastDays=30)
print(f"{downloadCount} new astronotes downloaded and cached")
```

And to then parse the notes to the database tables add:

```python
an.notes_to_database()
```

parsefec
========

Parser for pulling data out of FEC Filings.  Open sourced for Transparency Camp 2014


#Usage

####Command Line:

    > python parsefec.py -i=<inputdir> -s=<schema.csv> -d=t -o=<outputdir> --logdir <logdir>
    # Defaults directories and Schema 8.1 are included in the repo.

####As a library (in development 5/31/14):

```python
import parsefec

parsefec.parseFile(<fname or handle>)
parsefec.downloadRange(datefrom, dateto)

```

ParseFEC is one of several FEC Electronic Filing Parsers available from the [NYT](https://github.com/NYTimes/Fech), [USA Today](https://github.com/cschnaars/FEC-Scraper), and [The Sunlight Foundation](https://github.com/jsfenfen/read_FEC).




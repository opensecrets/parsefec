parsefec
========

Parser for pulling data out of FEC Filings.  Open sourced for Transparency Camp 2014


#Usage

####Command Line:

    # Text output using all defaults.  Uses directories and schema included in repo.
    > python parsefec.py --mode=TEXT -d='\t'
    # Help
    > python parserfec.py --help
    
```
usage: parsefec.py [-h] [--outdir OUTDIR] [--inputdir INPUTDIR] [--mode MODE]
                   [--delimiter DELIMITER]

Parser for FEC Electronic Filing data from OpenSecrets.org

optional arguments:
  -h, --help            show this help message and exit
  --inputdir INPUTDIR, -i INPUTDIR
                        Directory of zip files from
                        ftp://ftp.fec.gov/FEC/electronic/
  --mode MODE, -m MODE  Mode of output: DB, INSERTS (insert statements), TEXT
  --delimiter DELIMITER, -d DELIMITER
                        Delimiter for text output. Use python escapes:
                        --delimiter='\t'
```



####As a library (in development):

```python
import parsefec

parsefec.parseDir('input')

```

ParseFEC is one of several FEC Electronic Filing Parsers available from the [NYT](https://github.com/NYTimes/Fech), [USA Today](https://github.com/cschnaars/FEC-Scraper), and [The Sunlight Foundation](https://github.com/jsfenfen/read_FEC).




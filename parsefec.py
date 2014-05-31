'''

parsefec is a command line tool and python library for downloading, parsing FEC Electronic filings.

Usage: parsefec.py [-h] [--outdir OUTDIR] [--inputdir INPUTDIR] [--mode MODE]
                   [--delimiter DELIMITER]

Parser for FEC Electronic Filing data from OpenSecrets.org

optional arguments:
  -h, --help            show this help message and exit
  --inputdir INPUTDIR, -i INPUTDIR
                        Directory of zip files from
                        ftp://ftp.fec.gov/FEC/electronic/
  --mode MODE, -m MODE  Mode of output: db, inserts (insert statements), text
  --delimiter DELIMITER, -d DELIMITER
                        Delimiter for text output. Use python escapes:
                        --delimiter='\t'

Or:

parsefec | csvkit | psql


As a library: 

import parsefec

parsefec.parseFile()
parsefec.downloadRange()



'''

import zipfile
import os.path
import csv
import sqlite3
import datetime
import sys
from getpass import getpass

import argparse

from collections import OrderedDict

from settings import *

FS = '\x1C' # File separator character, used for delimiter in input[


def writeOut(statement, dbcursor=None):

    if args.mode == 'db':
        try:
            dbcursor.execute(statement)
            dbcursor.commit()
        except Exception, e:
            log.write('-- Insert Error:\n%s\n\n--%s%s' % (statement, e, errSep))
    else:
        print statement


def parseFile(fname):

    f = open(input_dirname + fname, 'r')

    dbcursor = None

    if args.mode == 'db': 
        dbconnection = pyodbc.connect(DBCONNECTION)
        dbcursor = dbconnection.cursor()
    elif args.mode == 'inserts':
        writeOut('INSERT INTO {}.{}.[{}] VALUES (\'{}\', \'{}\')'.format(database, schema, 'FilesProcessed', fname, datetime.date.today().strftime("%m/%d/%y")))    
    else:
        writeOut(args.delimiter.join(['FilesProcessed', fname, datetime.date.today().strftime("%m/%d/%y")]))    
    
    textmode = False
    
    for line in f:
        if line.strip() == '[ENDTEXT]':
            clog.write('%s\n\n%s' % (line, errSep))
            textmode = False
            continue 
        elif line.strip() == '[BEGINTEXT]':
            clog.write('-- Filename: %s\n%s\n' %(fname, line))
            clog.write('http://docquery.fec.gov/dcdev/fectxt/' + fname + '\n')
            textmode = True
            continue
        elif textmode:
            clog.write(line)
            continue

        
        if line[-1] == FS:
            line = line[:-1]
          
        # la (line array): Array of the current fields
        la = line.strip().split(FS)

        # Remove double quotes from double quote enclosed fields
        # TODO: Remove only first and last quotes.
        la = [x.replace('"', '') if len(x) > 0 and (x[0] == '"' and x[-1] == '"') else x for x in la]

        # Check first to see if no match will be found.
        matchFound = False
        for matchLine in orderedFormCodes.keys():
            if la[0][:len(matchLine)] == matchLine:            
                matchFound = True

        if matchFound is False:
            if la != ['']:
                log.write('-- No Form Match Error: %s\n' % la)
            continue

        for matchLine, formName in orderedFormCodes.iteritems():
            
            # Use lines that match a form name.
            if la[0][:len(matchLine)] == matchLine:                
                
                la.insert(0, fname.upper())

                # Insert row into table based on form_name
                if formName != 'NotProcessed':
                    insertClause = ''
                    schemaInfo = schemas[formName]

                    if len(schemaInfo) + 1 < len(la):
                        log.write('-- Schema does not match input line: %s\n%\n--%s%s' % (formName, la, schemaInfo, errSep))
                        break
                    # If columns are missing from end of input add 
                    # same number of None elements to end of Array.
                    # These will be replaced by Null in insert statement.
                    elif len(schemaInfo) > len(la):
                        la = la + [None] * (len(schemaInfo) - len(la))
                        # TODO: Log exception
                    
                    try:
                        for order, coltype in enumerate(schemaInfo):
                            # None is Null, 'NULL' is Null
                            if la[order] is None or la[order].strip().lower() == 'null':
                                insertClause += ', Null'
                                continue
                                
                            # Truncate varchar and chars to length
                            # TODO: Log exception
                            if coltype[0] in ['varchar', 'char'] and len(la[order]) > coltype[1]:

                                la[order] = la[order][:coltype[1]]

                                insertClause += ', \'' + la[order].replace('\'', '\'\'') + '\''
                                log.write('-- Truncation: %s Value: %s Truncated to: %s\n\n--%s%s' % (formName, la[order], coltype[1], la, errSep))

                            # If type is numerical and empty, use Null
                            elif coltype[0] == 'decimal' and la[order].strip() == '':
                                insertClause += ', Null'
                            else:
                                # TODO: Truncation is because current process overflows the variable after 
                                # escaped quotes are put in.
                                insertClause += ', \'' + la[order].replace('\'', '\'\'')  + '\''
                             
                    except Exception, e:
                        log.write('-- Error: %s\n\n--%s\n--%s\n--%s\n\n--%s%s' % (formName, la, schemaInfo, insertClause, e, errSep))

                    insertClause = insertClause[2:]

                    tableName = 'EF_Sch' + formName 
 
                    if args.mode == 'inserts':
                        output = 'INSERT INTO {}.{}.[{}] VALUES ({})'.format(database, schema, tableName, insertClause)
                    else:
                        fullout = [tableName] + [s if s is not None else '' for s in la]
                        output = args.delimiter.join(fullout)

                    writeOut(output, dbcursor)

                else:
                    if args.mode == 'inserts':
                        fullLine = '\t'.join(la[1:])
                        fullLine = fullLine.replace('\'', '\'\'')
                        output = '''INSERT INTO {}.{}.[EF_NotProcessed] VALUES ('{}', '{}', '{}' )'''.format(database, schema, la[0], fullLine, today)
                    else:
                        fullout = [tableName] + [s if s is not None else '' for s in la]
                        output = args.delimiter.join(fullout)
                   
                    writeOut(output, dbcursor)

                    #log.write('-- Not Processed Error:\n%s%s' % (la, errSep))
                    break
            
                
    #dbconnection.close()
    f.close()

def processFile(f):
    zfile = zipfile.ZipFile(input_dirname + f)
    
    filesprocessed = []

    for name in zfile.namelist():
        fd = open(input_dirname + name,"w")
        fd.write(zfile.read(name))
        fd.close()

        parseFile(name)

        filesprocessed.append(name)

        os.remove(input_dirname + name)

    if args.mode == 'db': 
        print 'First file processed: ' + min(filesprocessed) + '\n'
        print 'Last file processed: ' + max(filesprocessed) + '\n'
        print 'Number of files processed: ' + str(len(filesprocessed)) + '\n\n'
    

def processDir(dir):
    for zipname in os.listdir(input_dirname):
        if zipname[-3:] == 'zip':
            processFile(zipname)
   
# Order by length so short matches don't take precidence.
orderedFormCodes = OrderedDict(sorted(formCodes.items(), key=lambda t: -len(t[0])))

# Import schema information
conn = sqlite3.connect(":memory:")
c = conn.cursor()
c.execute("CREATE TABLE schemas (TABLE_NAME text,	COLUMN_NAME text,	TYPE_NAME text,	LENGTH integer, ORDINAL_POSITION integer);")
dr = csv.DictReader(open(schema_dirname + 'electronic_filing_schemas_v8_1.csv'), delimiter='\t')
to_db = [(i['TABLE_NAME'], i['COLUMN_NAME'], i['TYPE_NAME'], i['LENGTH'], i['ORDINAL_POSITION']) for i in dr]
c.executemany("INSERT INTO schemas (TABLE_NAME, COLUMN_NAME, TYPE_NAME, LENGTH, ORDINAL_POSITION) values (?, ?, ?, ?, ?);", to_db)
    
schemas = {}
    
for formName in formCodes.values():
    c.execute('SELECT TYPE_NAME, LENGTH FROM schemas where TABLE_NAME = "EF_Sch' + formName + '_Processed" ORDER BY ORDINAL_POSITION ASC')
    schemas[formName] = c.fetchall()
   
parser = argparse.ArgumentParser(description='Parser for FEC Electronic Filing data from OpenSecrets.org')
# Removed for now
# parser.add_argument('--outdir', '-o', type=argparse.FileType('w'), default=sys.stdout, help=' output directory, defaults to standard out')

parser.add_argument("--inputdir", '-i', dest='inputdir', help='Directory of zip files from ftp://ftp.fec.gov/FEC/electronic/', default='input')

parser.add_argument("--mode", '-m', dest='mode', help='Mode of output: db, inserts (insert statements), text', default='text')

parser.add_argument("--delimiter", '-d', dest='delimiter', help='Delimiter for text output.  Use python escapes: --delimiter=\'\\t\' ', default='\t')
    
args = parser.parse_args()
args.delimiter = args.delimiter.decode('string_escape')

if args.mode == 'db':
    import pyodbc
    # Some settings in settings.py
    DBCONNECTION = 'DRIVER={};SERVER={};DATABASE={};UID=datauser;PWD={}'.format(driver, server, database, getpass())

if __name__ == '__main__':
    today = datetime.date.today().strftime("%m/%d/%Y")
    
    # Open error log
    log = open(log_dirname + 'Electronic_Filing_Log_' + str(datetime.date.today()) + '.log', 'a')
    clog = open(log_dirname + 'Electronic_Filing_Log_Correspondence_' + str(datetime.date.today()) + '.log', 'a')

    processDir(args.inputdir)
      
    log.close()
    clog.close()



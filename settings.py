import os


database = 'parsefec'
schema = 'public'
server = 'localhost'
driver = 'PostgreSQL'

input_dirname = 'input'
output_dirname = 'output'
log_dirname = 'logs'
fec_schema = os.path.join('schema', 'electronic_filing_schemas_v8_1.csv')


# Separator between log entries
errSep = '\n-------------------\n\n'


# Form codes to table or output file translation.  Insert "NotProcessed" into 
# any forms that should be skipped.  It is important to keep all possible forms to distinguish
# a not processed form from an unknown form that may appear in the FEC data.

# Notice Some forms with the same schema can go into the same table.  F3LN and F3LA both go
# into a file or table called "EF_SchF3L."
formCodes = {'F99': 'NotProcessed', 
             'F3S': 'NotProcessed', 
             'F3Z' : 'NotProcessed', 
             'TEXT' : 'Text', 
             'HDR' : 'Header', 
             'SC1/' : 'C1',
             'SC2/' : 'C2',
             'F13N' : 'F13',
             'F13A' : 'F13',
             'F132' : 'F132', 
             'F133' : 'F133',
             'F3LN' : 'F3L',
             'F3LA' : 'F3L', 
             'F3LT' : 'F3L', 
             'F3PN' : 'F3P',
             'F3PA' : 'F3P', 
             'F3PT' : 'F3P',
             'F3PS' : 'F3PS', 
             'SC/' : 'C',
             'F3N' : 'F3', 
             'F3A' : 'F3',
             'F3T' : 'F3', 
             'F3L' : 'F3L',
             'F3P' : 'F3P',
             'F3X' : 'F3X',
             'F5N' : 'F5',
             'F5A' : 'F5',
             'F5T' : 'F5',
             'F56' : 'F56',
             'F57' : 'F57',
             'F6N' : 'F6',
             'F6A' : 'F6',
             'F6T' : 'F6',
             'F65' : 'F65',
             'F7A' : 'F7',
             'F7N' : 'F7',
             'F7T' : 'F7',
             'F76' : 'F76',
             'F9N' : 'F9',
             'F9A' : 'F9',
             'F9T' : 'F9',
             'F92' : 'F92',
             'F93' : 'F93',
             'F94' : 'F94',
             'SA' : 'A',
             'SB' : 'B',
             'SD' : 'D',
             'SE' : 'E',
             'SF' : 'F',
             'H1' : 'H1',
             'H2' : 'H2',
             'H3' : 'H3',
             'H4' : 'H4',
             'SI' : 'I',
             'SL' : 'L',
             'F3' : 'F3',
             'F4' : 'F4',
             'F5' : 'F5',
             'F6' : 'F6',
             'F7' : 'F7',
             'F9' : 'F9'}





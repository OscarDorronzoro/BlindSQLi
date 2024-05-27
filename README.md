# Blind SQL Injection
This tool purpose is to automate testing of web servers for blind SQL injection. This tool is intendent to be sqlmap-like but simpler and oriented exclusively to blind injections.

## Install
Clone git repository and execute the python file.

```
git clone https://github.com/OscarDorronzoro/BlindSQLi
python3 blindsqli.py
```

## Usage

```
python3 blindsqli.py [-h] -r REQUEST -p PARAMETERS [PARAMETERS ...] [-xT CSRFTOKEN] [-xU CSRFURL] [-xM CSRFMETHOD] [-s SCHEMA] [-cT CONDTRUE] [-cF CONDFALSE]
                    [-v | --verbose | --no-verbose] [-D DB] [-T TABLE] [-C [COLUMNS ...]] [--dbs | --no-dbs] [--tables | --no-tables]
                    [--row-count | --no-row-count] [--columns | --no-columns] [--rows | --no-rows]

optional arguments:
  -h, --help            show this help message and exit
  -r REQUEST, --request REQUEST
                        file containg http request
  -p PARAMETERS [PARAMETERS ...], --parameters PARAMETERS [PARAMETERS ...]
                        parameters to test for SQLi
  -xT CSRFTOKEN, --csrf-token CSRFTOKEN
                        name of anti-csrf token
  -xU CSRFURL, --csrf-url CSRFURL
                        URL to find anti-csrf token
  -xM CSRFMETHOD, --csrf-method CSRFMETHOD
                        Method used to gather anti-csrf token
  -s SCHEMA, --schema SCHEMA
                        http/https
  -cT CONDTRUE, --condition-true CONDTRUE
                        text pattern to look for in response to determine if injection evaluates to true
  -cF CONDFALSE, --condition-false CONDFALSE
                        text pattern to look for in response to determine if injection evaluates to false
  -v, --verbose, --no-verbose
                        if set show debug info (default: False)

  Query object:
  -D DB                 use database to further enumeration
  -T TABLE              use table to further enumeration
  -C [COLUMNS ...]      columns to select when dumping table

  Enum modes (if no mode is selected, print request info and quit):
  --dbs, --no-dbs       enumerate existing databases (default: False)
  --tables, --no-tables
                        enumerate existing tables within selected database (default: False)
  --row-count, --no-row-count
                        enumerate count(*) on selected table (default: False)
  --columns, --no-columns
                        enumerate columns definition on selected table (default: False)
  --rows, --no-rows     dump rows on selected table (default: False)
```

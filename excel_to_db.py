import csv
import pandas as pd
import pyodbc
import numpy as np
import math
#MUST HAVE: headers in the first row, only 1 file extension, aggregation param set to True if wanting to create new tables only for different datasets, distinguish datatypes set to False if columns do not have to be specified as other than string
from numpy import ndarray
import itertools
from typing import Any

user_input = True
parameters = {'aggregate_similar_data': bool(), 'historical_load': bool(), 'client_name': [], 'is_position': list(),
              'distinguish_between_datatypes': bool(), 'drop_tables': bool(), 'debug': bool(0)}

if not user_input:
    parameters['debug'] = True
    PATHS = ['???', '???']  # if there some paths most of the files come from, can create complete path_i as a f"{paths[x]}\\filename" list element
    FILES_TO_UPLOAD = ['???']
    
    parameters['aggregate_similar_data'] = False # default False, change if needed
    parameters['historical_load'] = False
    if parameters['historical_load']:
        parameters['client_name'] = []
        parameters['is_position'] = [1,1,0,1]
    parameters['distinguish_between_datatypes'] = True  # default True, change if needed
    parameters['drop_tables'] = False

else:
    print("IMPORTANT! The method will only process the first spreadsheet from each file.\n"
          "If your selected spreadsheet is not the first from the left within the Excel application, copy it to a separate file or delete the remaining spreadsheets.\n"
          "Please remove filtering and joined cells.")
    user_messages = [["Should the algorithm aggregate contents of files having the same column set into one table? 1=yes; 0=no -> ",
                      "The parameter can only accept inputs of {1,0}, try again."],
                     ["Do you want the algorithm to append file data to existing tables? 1=YES; 0=NO,I want new tables -> ", None],
                     ["To the table of which client do you want to append the data? \n"
                      "If you want to select one client for each file (in the order of them having been specified in the PATHS parameter), you can do so by separating them with ';' characters and leaving no space between -> ",
                      "The parameter can only accept elements separated by semicolons. Try again.",
                      "The parameter can only accept a list with the same number of elements as the list of the input files. Try again."], # in case of receiving only a single number/bool val, as ßsplit() would not work on that
                     ["Please specify whether the files contain portfolio- or position-level data; 1=position file; 0=portfolio file; please separate these respective values by semicolons (;)", None],
                     ["Do you want the algorithm to distinguish the data types of spreadsheet columns? 1=YES; 0=NO,all column types can be defaulted to text -> ", None],
                     ["Do you want the algorithm to replace SQL Server tables having the same name as any of your files? 1=yes; 0=no, I want new tables with name extensions (e.g. filename_2, filename_3) -> ", None],
                     ["I want to see more detailed messages about what happens during execution (exact rows inserted, datatypes of columns etc.). 1=yes; 0=no ->", None]]
    i_temp = 0
    while i_temp == 0:
        try:
            FILES_TO_UPLOAD = list((input(
                "Please give the full path of the files to be uploaded (example: 'C:\\Users\\username\\Documents\\filename'), separated by semicolons (;) and including the file extension! ->"
            )).split(';'))
            i_temp = 1
            print('\t', f"Value of parameter 'FILES_TO_UPLOAD' has been set to '{FILES_TO_UPLOAD}'")
        except ValueError:
            print(user_messages[2][1])

    for i in list(parameters.keys()):
        if i in ['is_position', 'client_name'] and not parameters['historical_load']:
            continue
        i_temp = 0
        while i_temp == 0:
            try:
                if isinstance(parameters[i], list):
                    parameters[i] = list((input(user_messages[list(parameters.keys()).index(i)][0])).split(';'))
                    assert(len(parameters[i]) == len(FILES_TO_UPLOAD))
                else:
                    input_temp = input(user_messages[list(parameters.keys()).index(i)][0])
                    if input_temp == '0':
                        parameters[i] = False
                    elif input_temp == '1':
                        parameters[i] = True
                    else:
                        raise ValueError
                i_temp = 1
            except ValueError:
                if isinstance(parameters[i], bool):
                    print(user_messages[0][1])
                elif isinstance(parameters[i], list):
                    print(user_messages[2][1])
            except AssertionError:
                print(user_messages[2][2])
            if i_temp == 1:
                print('\t', f"Value of parameter '{i}' has been set to '{parameters[i]}'")
    # insert data into correct table based on client name (search for a convention && {client name} in db, select correct result & set as insert destination)
    # client name can be given irrespective of capital letters & separators
    
driver = '???'
server = '???'
db_name = '???'
conn_str = f"DRIVER={driver}; SERVER={server}; DATABASE={db_name}; Trusted_Connection=yes;"
conn = pyodbc.connect(conn_str)
handle = conn.cursor()

def try_float(cell): #takes any, returns any
    try:
        if math.isnan(cell) or cell == None:
            return 'undefined'
        else:
            return float(cell)
    except:
        return 'nvarchar'

def try_int(cell_float): #takes any, returns any
    if cell_float not in ['nvarchar', 'float', 'undefined']:
        if '.' not in str(cell_float):
            return int(cell_float)
        else:
            return 'float'
    elif cell_float == 'undefined':
        return 'undefined'
    else:
        return cell_float

def try_bit(cell_int): #takes any, returns string
    if cell_int in ['nvarchar', 'float']:
        return cell_int
    elif cell_int == 'undefined':
        return 'bit'
    else:
        if cell_int in [0, 1]:
            return 'bit'
        else:
            return 'integer'

def determine_type(col_data): #takes list, returns string
    cell_types = [try_bit(try_int(try_float(x))) for x in col_data]
    if all(x == 'bit' for x in cell_types):
        return 'bit'
    else:
        if all(x2 in ['integer', 'bit'] for x2 in cell_types):
            return 'integer'
        else:
            if all(x3 != 'nvarchar' for x3 in cell_types):
                return 'float'
            else:
                return 'nvarchar'

extracts: list[pd.DataFrame] = []
assert(all('.xlsx' in x or '.csv' in x for x in FILES_TO_UPLOAD)), "the process can only accept .xlsx and .csv formats"
for loc_i in FILES_TO_UPLOAD:
    try:
        extracts.append(pd.DataFrame((lambda y: pd.read_excel(y) if '.xlsx' in y else pd.read_csv(y, low_memory=False))(loc_i)))
    except Exception as e:
        print(e, f"ERROR in file {loc_i}, will move on to next file")

# if the values in a column can be confidently identified to be of type int, bit, double -> create table as such => there will be a list of same size and same reference of indices
# compares both names of headers and col datatypes to identify data that can be put into the same db
headers = [x.columns.values for x in extracts]
new_tables = np.asarray([None for x in range(len(FILES_TO_UPLOAD))]) # for each file index, displays the name of the db that file's data will go into; is filled with index values & is used to skip datasets already created table for
col_types_nested = [[] for x in range(len(extracts))]


if parameters['aggregate_similar_data']: # create tables where there is a new type of dataset | if not, create one table for each dataset
    for dataset_i in range(0, len(FILES_TO_UPLOAD)):
        col_types_ls = []
        if new_tables[dataset_i] is None:
            similar_dataset_indices = [dataset_i] # contain the new dataset table by default, append more if similar exist
            for unassigned_i in list(filter(lambda y: new_tables[y] is None and y != dataset_i, range(0, len(new_tables)))): # for each OTHER unassigned dataset
                temp_header_unified_other = [str(x).lower() for x in headers[unassigned_i]]
                temp_header_unified_this = [str(x).lower() for x in headers[dataset_i]]
                if all(x in temp_header_unified_other for x in temp_header_unified_this) and all(x2 in temp_header_unified_this for x2 in temp_header_unified_other): # only attribute them as similar if all columns match but the order does not matter
                    similar_dataset_indices.append(unassigned_i) # gathers the index of those datasets that also do not yet have a table assigned to

            new_tables[[similar_dataset_indices]] = FILES_TO_UPLOAD[dataset_i][FILES_TO_UPLOAD[dataset_i].rindex('\\') + 1:FILES_TO_UPLOAD[dataset_i].rindex('.'):].upper()
            column_specs = []
            for column_i in range(len(headers[dataset_i])): # determines datatypes for table creation config input
                cell_length_i = max(list(itertools.chain(*[[len(str(file.iat[row, column_i])) for row in range(len(file))] for file in list(np.asarray(extracts)[[similar_dataset_indices]])])))
                if parameters['distinguish_between_datatypes']:
                    typeof_column_i = determine_type([extracts[dataset_i].iat[row, column_i] for row in range(len(extracts[dataset_i]))])
                else:
                    typeof_column_i = 'nvarchar'
                
                col_types_ls.append(typeof_column_i)
                concat_type_length = (lambda y: f"{y}({cell_length_i})" if y == 'nvarchar' else f"{y}")(typeof_column_i)
                column_specs.append(f"[{headers[dataset_i][column_i]}] {concat_type_length}") #always truncates cell container length -> DB cell max length will be of the longest length data within the selection

            column_specs = ','.join(column_specs)
            handle.execute(f"SELECT * FROM {db_name}.sys.tables WHERE name = '{new_tables[dataset_i]}'")
            for i in range(1):
                if len(handle.fetchall()) != 0:
                    if parameters['drop_tables']:
                        handle.execute(f"DROP TABLE {db_name}.dbo.[{new_tables[dataset_i]}]")
                        handle.commit()
                    else:
                        handle.execute(
                            f"SELECT * FROM {db_name}.sys.tables WHERE name LIKE '{new_tables[dataset_i]}_%'"
                        )
                        name_temp = f"{new_tables[dataset_i]}_{len(handle.fetchall())}"
                        # specifies list of columns with their types
                        handle.execute(
                            f"CREATE TABLE [{name_temp}] ({column_specs}, source_file nvarchar(" + str(len(
                                FILES_TO_UPLOAD[dataset_i][FILES_TO_UPLOAD[dataset_i].rindex('\\') + 1::]
                            )) + "))"
                        )
                        handle.commit()
                        print(f"table {name_temp} created")
                        new_tables[[similar_dataset_indices]] = name_temp
                        break
                # specifies list of columns with their types
                handle.execute(f"CREATE TABLE [{new_tables[dataset_i]}] ({column_specs}, source_file nvarchar(" + str(
                    len(FILES_TO_UPLOAD[dataset_i][FILES_TO_UPLOAD[dataset_i].rindex('\\') + 1::])
                ) + "))")
                handle.commit()
                print(f"table {new_tables[dataset_i]} created")
            if parameters['debug']:
                print(f"SQL command: CREATE TABLE [{new_tables[dataset_i]}] ({column_specs}, source_file nvarchar(" + str(len(
                    FILES_TO_UPLOAD[dataset_i][FILES_TO_UPLOAD[dataset_i].rindex('\\') + 1::]
                )) + "))")

            col_types = col_types_ls
            for i in similar_dataset_indices:
                col_types_nested[i] = col_types_ls
            if parameters['debug']:
                print(col_types_ls, '\n', col_types_nested)
        else:
            col_types = col_types_nested[dataset_i]

        vertical_length = len(extracts[dataset_i])
        for batch_start in range(0, vertical_length, 1000): # always inserts the NEXT 1000 at a crt index (simple INSERT can only take 1000 rows and BULK INSERT is too error-prone)
            newl = '\n'
            sql_str = f"INSERT INTO [{new_tables[dataset_i].upper()}] VALUES ("
            if parameters['debug']:
                print(batch_start, vertical_length)
                print(range(batch_start, (lambda y: batch_start + 1000 if y >= 1000 else batch_start + y)(vertical_length - batch_start)))
            for row_i in range(batch_start, (lambda y: batch_start + 1000 if y >= 1000 else batch_start + y)(vertical_length - batch_start)):
                
                for col_i in range(len(headers[dataset_i])):
                    if col_types[col_i] == 'nvarchar':
                        cell_value = str(extracts[dataset_i].iat[row_i, col_i]).rstrip().lstrip()
                        if "'" in cell_value:
                            try:
                                rbound = cell_value.rindex("'")
                                while True:
                                    cell_value = cell_value[:cell_value.rindex("'", 0, rbound + 1):] + "'" + cell_value[rbound::]
                                    rbound = cell_value.rindex("'", 0, rbound)
                            except ValueError:
                                ...
                        sql_str += "'" + cell_value + "', "
                    else:
                        sql_str += f"{(lambda x: 'null' if math.isnan(x) or x == 'nan' else x)(extracts[dataset_i].iat[row_i, col_i])}, "
                sql_str += "'" + str(FILES_TO_UPLOAD[dataset_i][FILES_TO_UPLOAD[dataset_i].rindex('\\') + 1::]) + "')," + newl + "("
            sql_str = sql_str.rstrip('(').rstrip('\n').rstrip(',')
            if parameters['debug']:
                print(sql_str)
            handle.execute(sql_str) # INSERT INTO in 1000-piece batches, insert filename at last row to be able to distinguish btw separate batches w/i one aggr table
            handle.commit()
        print(f"{vertical_length} rows inserted")

else:
    for dataset_i in range(0, len(FILES_TO_UPLOAD)):
        new_tables[dataset_i] = FILES_TO_UPLOAD[dataset_i][FILES_TO_UPLOAD[dataset_i].rindex('\\') + 1:FILES_TO_UPLOAD[dataset_i].rindex('.'):].upper()
        column_specs = []
        for column_i in range(len(headers[dataset_i])):  # determine datatypes for table creation config input
            cell_length_i = max(
                [len(str(extracts[dataset_i].iat[row, column_i])) for row in range(len(extracts[dataset_i]))])
            if parameters['distinguish_between_datatypes']:
                typeof_column_i = determine_type([extracts[dataset_i].iat[row, column_i] for row in range(len(extracts[dataset_i]))])
            else:
                typeof_column_i = 'nvarchar'
            
            concat_type_length = (lambda y: f"{y}({cell_length_i})" if y == 'nvarchar' else f"{y}")(typeof_column_i)
            col_types_nested[dataset_i].append(typeof_column_i)
            column_specs.append(f"[{headers[dataset_i][column_i]}] {concat_type_length}")

        column_specs = ','.join(column_specs)
        handle.execute(f"SELECT * FROM {db_name}.sys.tables WHERE name = '{new_tables[dataset_i]}'")
        for i in range(1):
            if len(handle.fetchall()) != 0:
                if parameters['drop_tables']:
                    handle.execute(f"DROP TABLE {db_name}.dbo.[{new_tables[dataset_i]}]")
                    handle.commit()
                else:
                    handle.execute(f"SELECT * FROM {db_name}.sys.tables WHERE name LIKE '{new_tables[dataset_i]}_%'")
                    name_temp = f"{new_tables[dataset_i]}_{len(handle.fetchall())}"
                    handle.execute(
                        f"CREATE TABLE [{name_temp}] ({column_specs}, source_file nvarchar(" + str(len(
                            FILES_TO_UPLOAD[dataset_i][FILES_TO_UPLOAD[dataset_i].rindex('\\') + 1::]
                        )) + "))"
                    ) # specifies list of columns with their types
                    handle.commit()
                    print(f"table {name_temp} created")
                    new_tables[dataset_i] = name_temp
                    break
            handle.execute(
                f"CREATE TABLE [{new_tables[dataset_i]}] ({column_specs}, source_file nvarchar(" + str(len(
                    FILES_TO_UPLOAD[dataset_i][FILES_TO_UPLOAD[dataset_i].rindex('\\') + 1::]
                )) + "))"
            ) #specifies list of columns with their types
            handle.commit()
            print(f"table {new_tables[dataset_i]} created")
        if parameters['debug']:
            print(f"SQL command: CREATE TABLE [{new_tables[dataset_i]}] ({column_specs}, source_file nvarchar(" + str(len(
                FILES_TO_UPLOAD[dataset_i][FILES_TO_UPLOAD[dataset_i].rindex('\\') + 1::]
            )) + "))")
        vertical_length = len(extracts[dataset_i])
        col_types = col_types_nested[dataset_i]

        for batch_start in range(0, vertical_length, 1000): # always inserts the NEXT 1000 at a crt index
            newl = '\n'
            if parameters['debug']:
                print(batch_start, vertical_length)
                print(range(batch_start, (lambda y: batch_start + 1000 if y >= 1000 else batch_start + y)(vertical_length - batch_start)))
            sql_str = f"INSERT INTO [{new_tables[dataset_i]}] VALUES ("
            for row_i in range(batch_start, (lambda y: batch_start + 1000 if y >= 1000 else batch_start + y)(vertical_length - batch_start)):
                
                for col_i in range(len(headers[dataset_i])):
                    if col_types[col_i] == 'nvarchar':
                        cell_value = str(extracts[dataset_i].iat[row_i, col_i]).rstrip().lstrip()
                        if "'" in cell_value: # there may be strings containing single quotation marks, these have to be duplicated in order for MS SQL not to interpret them as end of string
                            try:
                                rbound = cell_value.rindex("'")
                                while True:
                                    cell_value = cell_value[:cell_value.rindex("'", 0, rbound + 1):] + "'" + cell_value[rbound::]
                                    rbound = cell_value.rindex("'", 0, rbound)
                            except ValueError: # we exit when we do not find single quotes in the right direction within the string any more
                                ...
                        sql_str += "'" + cell_value + "', "
                    
                    else:
                        sql_str += f"""{
                            (lambda x: 'null' if math.isnan(x) or x == 'nan' else x)(
                                (lambda y: "'" + str(y) + "'" if isinstance(y, bool) else y)(
                                    extracts[dataset_i].iat[row_i, col_i]
                                )
                            )
                        }, """
                sql_str += "'" + str(FILES_TO_UPLOAD[dataset_i][FILES_TO_UPLOAD[dataset_i].rindex('\\') + 1::]) + "')," + newl + "("
            sql_str = sql_str.rstrip('(').rstrip('\n').rstrip(',')
            if parameters['debug']:
                print(sql_str)
            handle.execute(sql_str) # INSERT INTO in 1000 batches, insert filename at last row to be able to distinguish btw separate batches within one aggr table
            handle.commit()
        print(f"{vertical_length} rows inserted")
# insert data in the same table if the headers and the datatypes are the same -> create as many insert queries as there are distinct tables if aggregate_similar_data = TRUE
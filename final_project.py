#################################
##### Name: Cameron Milne
##### Uniqname: ccmilne
#################################

from requests_oauthlib import OAuth1
from bs4 import BeautifulSoup
import requests, json, csv, time, operator
import sqlite3, os
# import logging, sys
import plotly.graph_objects as go
from sqlite3 import Error

### Other files
import database_functions #All Database connectivity and table creations
import interactive_elements #Longer print statements for the interactive terminal
import viz_functions #All plotly functions for the interactive terminal

### Caching
CACHE_FILENAME = 'cache_census.json'
CACHE_DICT = {}
UNIQUE_CACHE_KEY = 'usual'
CENSUS_API_KEY = '3d095bab381ec8a891e05c0fe05da954f2710317'
CENSUS_BASEURL = 'https://api.census.gov/data/timeseries/pseo/earnings'


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()



### Zillow Data
def build_zillow_dictionary(csv_file):
    '''Reads in CSV file from Zillow

    This function reads in the CSV data file from Zillow and returns a list of states
    and the median home prices from the most recent month. The data comes from Zillow's 
    Home Value Index (ZHVI): https://www.zillow.com/research/data/.

    Parameters
    ----------
    csv_file: specifically the 'zillow_by_state.csv' file

    returns:
    -------
    Dictionary of a key: value pairing of state: median home price
    '''
    # file_directory = os.path.dirname('CSV_Files')
    # relative_path = csv_file
    # absolute_file_path = os.path.join(file_directory, relative_path)
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        zillow_states = {}
        for row in reader: #every row in reader contains a state and the median home price values by month
            state_name = row[2].lower()
            recent_month = row[-1]

            #add data to dictionary
            if state_name not in zillow_states:
                zillow_states[state_name] = recent_month

        # del zillow_states['RegionName'] #uppercase
        del zillow_states['regionname'] #lowercase

    #print(zillow_states)
    return zillow_states

def convert_zillow_to_CSV(zillow_dict):
    '''
    '''
    fields = ['State', 'Median Home Value']
    rows = []

    for key, val in zillow_dict.items():
        row = []
        row.append(key)
        row.append(val)
        rows.append(row)

    filename = 'zillow.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile) # creating a csv writer object
        csvwriter.writerow(fields) # writing the fields
        csvwriter.writerows(rows)  # writing the data rows

def build_zillow_complete_dict(csv_file):
    ''' '''
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        zillow_states = {}
        for row in reader: #every row in reader contains a state and the median home price values by month
            # size_rank = row[1]
            state_name = row[2].lower()
            # region_type = row[3]
            # state_abbrev = row[4]
            all_months = list(row[5:])

            #add data to dictionary
            if state_name not in zillow_states:
                zillow_states[state_name] = all_months

        # del zillow_states['RegionName'] #uppercase
        del zillow_states['regionname'] #lowercase

    return zillow_states

# def convert_zillow_complete_to_csv(zillow_complete_dict):
#     '''
#     '''
#     fields = ['State',
#         '1_31_1996', '2_29_1996', '3_31_1996', '4_30_1996', '5_31_1996', '6_30_1996', '7_31_1996', '8_31_1996', '9_30_1996', '10_31_1996', '11_30_1996', '12_31_1996',
#         '1_31_1997', '2_28_1997', '3_31_1997', '4_30_1997', '5_31_1997', '6_30_1997', '7_31_1997', '8_31_1997', '9_30_1997', '10_31_1997', '11_30_1997', '12_31_1997',
#         '1_31_1998', '2_28_1998', '3_31_1998', '4_30_1998', '5_31_1998', '6_30_1998', '7_31_1998', '8_31_1998', '9_30_1998', '10_31_1998', '11_30_1998', '12_31_1998',
#         '1_31_1999', '2_28_1999', '3_31_1999', '4_30_1999', '5_31_1999', '6_30_1999', '7_31_1999', '8_31_1999', '9_30_1999', '10_31_1999', '11_30_1999', '12_31_1999',
#         '1_31_2000', '2_29_2000', '3_31_2000', '4_30_2000', '5_31_2000', '6_30_2000', '7_31_2000', '8_31_2000', '9_30_2000', '10_31_2000', '11_30_2000', '12_31_2000',
#         '1_31_2001', '2_28_2001', '3_31_2001', '4_30_2001', '5_31_2001', '6_30_2001', '7_31_2001', '8_31_2001', '9_30_2001', '10_31_2001', '11_30_2001', '12_31_2001', 
#         '1_31_2002', '2_28_2002', '3_31_2002', '4_30_2002', '5_31_2002', '6_30_2002', '7_31_2002', '8_31_2002', '9_30_2002', '10_31_2002', '11_30_2002', '12_31_2002', 
#         '1_31_2003', '2_28_2003', '3_31_2003', '4_30_2003', '5_31_2003', '6_30_2003', '7_31_2003', '8_31_2003', '9_30_2003', '10_31_2003', '11_30_2003', '12_31_2003', 
#         '1_31_2004', '2_29_2004', '3_31_2004', '4_30_2004', '5_31_2004', '6_30_2004', '7_31_2004', '8_31_2004', '9_30_2004', '10_31_2004', '11_30_2004', '12_31_2004', 
#         '1_31_2005', '2_28_2005', '3_31_2005', '4_30_2005', '5_31_2005', '6_30_2005', '7_31_2005', '8_31_2005', '9_30_2005', '10_31_2005', '11_30_2005', '12_31_2005', 
#         '1_31_2006', '2_28_2006', '3_31_2006', '4_30_2006', '5_31_2006', '6_30_2006', '7_31_2006', '8_31_2006', '9_30_2006', '10_31_2006', '11_30_2006', '12_31_2006', 
#         '1_31_2007', '2_28_2007', '3_31_2007', '4_30_2007', '5_31_2007', '6_30_2007', '7_31_2007', '8_31_2007', '9_30_2007', '10_31_2007', '11_30_2007', '12_31_2007', 
#         '1_31_2008', '2_29_2008', '3_31_2008', '4_30_2008', '5_31_2008', '6_30_2008', '7_31_2008', '8_31_2008', '9_30_2008', '10_31_2008', '11_30_2008', '12_31_2008', 
#         '1_31_2009', '2_28_2009', '3_31_2009', '4_30_2009', '5_31_2009', '6_30_2009', '7_31_2009', '8_31_2009', '9_30_2009', '10_31_2009', '11_30_2009', '12_31_2009', 
#         '1_31_2010', '2_28_2010', '3_31_2010', '4_30_2010', '5_31_2010', '6_30_2010', '7_31_2010', '8_31_2010', '9_30_2010', '10_31_2010', '11_30_2010', '12_31_2010', 
#         '1_31_2011', '2_28_2011', '3_31_2011', '4_30_2011', '5_31_2011', '6_30_2011', '7_31_2011', '8_31_2011', '9_30_2011', '10_31_2011', '11_30_2011', '12_31_2011', 
#         '1_31_2012', '2_29_2012', '3_31_2012', '4_30_2012', '5_31_2012', '6_30_2012', '7_31_2012', '8_31_2012', '9_30_2012', '10_31_2012', '11_30_2012', '12_31_2012', 
#         '1_31_2013', '2_28_2013', '3_31_2013', '4_30_2013', '5_31_2013', '6_30_2013', '7_31_2013', '8_31_2013', '9_30_2013', '10_31_2013', '11_30_2013', '12_31_2013', 
#         '1_31_2014', '2_28_2014', '3_31_2014', '4_30_2014', '5_31_2014', '6_30_2014', '7_31_2014', '8_31_2014', '9_30_2014', '10_31_2014', '11_30_2014', '12_31_2014', 
#         '1_31_2015', '2_28_2015', '3_31_2015', '4_30_2015', '5_31_2015', '6_30_2015', '7_31_2015', '8_31_2015', '9_30_2015', '10_31_2015', '11_30_2015', '12_31_2015', 
#         '1_31_2016', '2_29_2016', '3_31_2016', '4_30_2016', '5_31_2016', '6_30_2016', '7_31_2016', '8_31_2016', '9_30_2016', '10_31_2016', '11_30_2016', '12_31_2016', 
#         '1_31_2017', '2_28_2017', '3_31_2017', '4_30_2017', '5_31_2017', '6_30_2017', '7_31_2017', '8_31_2017', '9_30_2017', '10_31_2017', '11_30_2017', '12_31_2017', 
#         '1_31_2018', '2_28_2018', '3_31_2018', '4_30_2018', '5_31_2018', '6_30_2018', '7_31_2018', '8_31_2018', '9_30_2018', '10_31_2018', '11_30_2018', '12_31_2018', 
#         '1_31_2019', '2_28_2019', '3_31_2019', '4_30_2019', '5_31_2019', '6_30_2019', '7_31_2019', '8_31_2019', '9_30_2019', '10_31_2019', '11_30_2019', '12_31_2019', 
#         '1_31_2020', '2_29_2020', '3_31_2020', '4_30_2020', '5_31_2020', '6_30_2020', '7_31_2020', '8_31_2020', '9_30_2020', '10_31_2020', '11_30_2020', '12_31_2020', 
#         '1_31_2021', '2_28_2021']

#     rows = []

#     for key, value_list in zillow_complete_dict.items():
#         row = []
#         row.append(key)

#         for val in value_list:
#             row.append(val)

#         rows.append(row)

#     filename = 'zillow_complete.csv'
#     with open(filename, 'w', newline='') as csvfile:
#         csvwriter = csv.writer(csvfile) # creating a csv writer object
#         csvwriter.writerow(fields) # writing the fields
#         csvwriter.writerows(rows)  # writing the data rows


### Census Data
def get_census_data(url):
    '''fetches Census API

    Given a link, this function will retrieve the Census
    API data from the Census Bureau for statistics on educational
    attainment data.

    Parameters
    ----------
    url: the specific base url and chained variables for the desired outcome

    returns:
    -------
    Dictionary of key as State and value as # of residents with a bachelor's degree
    '''

    if os.path.isfile('cache_census.json') and os.access('cache_census.json', os.R_OK):
        print('Using Cache')
        with open('cache_census.json', 'r', newline='') as cache_file:
            cache = json.load(cache_file)
            return cache[UNIQUE_CACHE_KEY]

    else:
        print("Fetching from API")
        CACHE_DICT[UNIQUE_CACHE_KEY] = requests.get(url).json()
        save_cache(CACHE_DICT)
        return CACHE_DICT[UNIQUE_CACHE_KEY]

def parse_census_data(census_data):
    '''
    '''
    state_bach_dict = {}

    for individual_list in census_data:
        state_lower = individual_list[0].lower()
        state_bach_dict[state_lower] = individual_list[1]

    # del state_bach_dict['NAME']
    # del state_bach_dict['Puerto Rico']
    del state_bach_dict['name']
    del state_bach_dict['puerto rico']

    return state_bach_dict

def convert_census_to_csv(census_dict):
    '''
    '''
    fields = ['State', 'Bachelor Degrees']
    rows = []

    for key, val in census_dict.items():
        row = []
        row.append(key)
        row.append(val)
        rows.append(row)

    filename = 'census.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile) # creating a csv writer object
        csvwriter.writerow(fields) # writing the fields
        csvwriter.writerows(rows)  # writing the data rows

### Wikipedia Data
def build_wikipedia_dictionary():
    '''Scrapes Wikipedia info into a dictionary

    This function takes in a specific Wikipedia
    page (https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_income)
    and, using the "States and territories ranked by per capita income" table, scrapes
    the state name and per capita income for everyone in that state.

    Parameters
    ----------
    None

    Returns:
    -------
    Dictionary of with key as a state name and value of per capita income
    '''

    WIKIPEDIA_URL = 'https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_income'
    page = requests.get(WIKIPEDIA_URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    # #print(soup.title.string)

    #Trying regex
    tables = soup.find_all('table')
    # print(len(soup.find_all('table'))) #There are 6 tables

    for table in tables:
        if 'Per capita' and 'Number of' in table.text:
            # print(table.text)
            headers = [header.text.strip() for header in table.find_all('th')]
            #print(headers)
            rows = []
            table_rows = table.find_all('tr')
            #print(table_rows)
            for row in table_rows:
                #print(row)
                td = row.find_all('td')
                #print(td)
                row = [row.text.strip() for row in td]
                #print(row)
                rows.append(row)
            rows.insert(0, headers)
            rows.pop(1)
            #print(rows)

    # Convert to dictionary
    wiki_dictionary = {}

    # headings = rows[0]
    #print(headings)
    for item in rows[1:]:
        state_name = item[1].lower()
        wiki_dictionary[state_name] = [item[2], item[3], item[4], item[5], item[6], item[7]]

    # # Drop U.S. and territories uppercase
    # del wiki_dictionary['United States']
    # del wiki_dictionary['American Samoa']
    # del wiki_dictionary['Northern Mariana Islands']
    # del wiki_dictionary['Puerto Rico']
    # del wiki_dictionary['Guam']
    # del wiki_dictionary['U.S. Virgin Islands']

    # Drop U.S. and territories lowercase
    del wiki_dictionary['united states']
    del wiki_dictionary['american samoa']
    del wiki_dictionary['northern mariana islands']
    del wiki_dictionary['puerto rico']
    del wiki_dictionary['guam']
    del wiki_dictionary['u.s. virgin islands']

    #print(wiki_dictionary)
    return wiki_dictionary

def clean_wikipedia_dictionary(wiki_dict):
    '''
    '''
    new_dict = {}

    for key, value_list in wiki_dict.items():
        new_list = []
        for val in value_list:
            new = val.replace('$', '').replace(',', '')
            new_list.append(new)
        new_dict[key] = new_list

    return new_dict

def convert_wikipedia_to_csv(wiki_dict):
    '''
    '''
    fields = [
        'State',
        'Per Capita Income',
        'Median Household Income',
        'Median Family Income',
        'Population',
        'Number of Households',
        'Number of Families',
    ]

    rows = []

    for key, value_list in wiki_dict.items():
        row = []
        row.append(key)

        for val in value_list:
            row.append(val)

        rows.append(row)

    filename = 'wikipedia.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile) # creating a csv writer object
        csvwriter.writerow(fields) # writing the fields
        csvwriter.writerows(rows)  # writing the data rows

### DB/SQLite3
'''
Functions are stored in database_functions.py
'''

# ### Plotly
'''
Functions are stored in viz_functions.py
'''

### Interactive Elements
def list_all_states_above_budget(budget_input):
    zillow_data = build_zillow_dictionary('zillow_by_state.csv')
    zillow_list = [zillow_data]
    new_zillow_dict = [dict([a, int(x)] for a, x in b.items()) for b in zillow_list][0]

    #Confirm budget is above lowest value
    minimum_value = min(new_zillow_dict, key=lambda k: new_zillow_dict[k])

    if budget_input >= new_zillow_dict[minimum_value]:
        affordable_dict = {}
        for key, val in new_zillow_dict.items():
            if budget_input >= val:
                affordable_dict[key] = val

        sorted_values = sorted(affordable_dict.values())
        sorted_dict = {}
        for i in sorted_values:
            for key in affordable_dict.keys():
                if affordable_dict[key] == i:
                    sorted_dict[key] = affordable_dict[key]
                    break

        print('=' * 30)
        print(f"You entered: {budget_input}")
        amount = len(sorted_dict.keys())
        print(f"You can afford to live in {amount} states. ")
        print(f"\nThe states and their median home values are as follows (sorted by affordability):")
        print('-' * 30)
        for key, val in sorted_dict.items():
            capped_key = key.capitalize()
            print(f"{capped_key}: {val}")

    else:
        print('=' * 30)
        print(f"You entered: {budget_input}, but there are no states under that budget. ")
        budget_state, budget = min(new_zillow_dict.items(), key=lambda x: abs(budget_input - x[1]))
        print(f"The closest state is {budget_state.capitalize()} with a median home value of {budget}. ")

def incomeComparer(income_input):
    '''
    '''
    print('=' * 30)
    print(f"You entered: {income_input}")
    wikipedia_data = build_wikipedia_dictionary()
    wikipedia_data_cleaned = clean_wikipedia_dictionary(wikipedia_data)
    # wikipedia_list = [wikipedia_data_cleaned]
    # print(wikipedia_list)

    new_wikipedia_dict = {}
    for key, value_list in wikipedia_data_cleaned.items():
        new_value_list = []
        for value in value_list:
            new_value = int(value)
            new_value_list.append(new_value)
        new_wikipedia_dict[key] = new_value_list[0] #Only income per capita

    state, income = min(new_wikipedia_dict.items(), key=lambda x: abs(income_input - x[1]))
    print(state.capitalize(), income)



if __name__ == "__main__":

    #Calling Zillow functions
    zillow_data = build_zillow_dictionary('zillow_by_state.csv')
    convert_zillow_to_CSV(zillow_data)
    # zillow_complete = build_zillow_complete_dict('zillow_by_state.csv')
    # convert_zillow_complete_to_csv(zillow_complete)

    #Calling Census functions
    census_data = get_census_data('https://api.census.gov/data/2019/acs/acs5?get=NAME,B15003_022E&for=state:*&key=3d095bab381ec8a891e05c0fe05da954f2710317')
    census_data_parsed = parse_census_data(census_data=census_data)
    #print(census_data_parsed)
    convert_census_to_csv(census_data_parsed)

    #Calling Wikipedia functions
    wikipedia_data = build_wikipedia_dictionary()
    wikipedia_data_cleaned = clean_wikipedia_dictionary(wikipedia_data)
    #print(wikipedia_data_cleaned['north dakota'])
    convert_wikipedia_to_csv(wikipedia_data_cleaned)

    #Calling SQLite functions
    database_functions.create_connection('project.db')
    database_functions.create_zillow_table()
    # database_functions.create_z2_table()
    database_functions.create_census_table()
    database_functions.create_wikipedia_table()

    #Testing the Search by State functions
    #list_zillow_details(state='Michigan', zillow_data=zillow_data)
    #list_wikipedia_details(state='Michigan', wikipedia_data=wikipedia_data_cleaned)
    #list_census_details(state='Michigan', census_data=census_data_parsed)
    #list_all_details(state='Michigan', zillow_data=zillow_data, wikipedia_data=wikipedia_data_cleaned, census_data=census_data_parsed)
    #find_state_with_closest_budget(100000)
    #list_all_states_above_budget(100000)
    #incomeComparer(35000)
    # string_list = list(zillow_data.values())
    # int_list = list(map(int, string_list))
    # takeClosest(100000, int_list)

    #Interactive Console
    # interactive_elements.opening_statement()

    while True:

        #Provide initial options
        interactive_elements.provide_initial_options()
        entry = input(f"\nType a number (e.g. '1', '2') or 'exit': ")
        user_input = entry.lower().strip()

        #Option: Exit
        if user_input == 'exit':
            print(f'\nBye!')
            quit()

        #Option #1: Compare personal finances across states
        elif user_input == '1':
            while True:
                print(f"\nWould you like to:")
                print('-' * 30)
                print(f"(a) Enter a budget for a home")
                print(f"(b) Compare your income across state averages")
                print('-' * 30)
                selection = input(f"Enter a letter (e.g. 'a' or 'b') or type 'exit' or 'back': ")
                string_accomodation = selection.lower().strip()

                if string_accomodation == 'exit':
                    print(f'\nBye!')
                    quit()

                elif string_accomodation == 'back':
                    break

                elif string_accomodation == 'a':
                    while True: #Complete
                        budget_entry = input(f"\nEnter a budget (without commas or a dollar sign) or type 'exit' or 'back': ")

                        if budget_entry == 'exit':
                            print(f'\nBye!')
                            quit()

                        elif budget_entry == 'back':
                            break

                        elif budget_entry.isnumeric():
                            list_all_states_above_budget(int(budget_entry))

                        else:
                            print(f"\n ")
                            print('=' * 62)
                            print(f"[Error] Enter a budget (without commas or a dollar sign) or type 'exit' or 'back': ")
                            print('=' * 62)

                elif string_accomodation == 'b':
                    while True: #Complete
                        income_entry = input(f"\nEnter an income (without commas or a dollar sign) or type 'exit' or 'back': ")

                        if income_entry == 'exit':
                            print(f'\nBye!')
                            quit()

                        elif income_entry == 'back':
                            break

                        elif income_entry.isnumeric():
                            incomeComparer(int(income_entry))

                        else:
                            print(f"\n ")
                            print('=' * 62)
                            print(f"[Error] Enter an income (without commas or a dollar sign) or type 'exit' or 'back': ")
                            print('=' * 62)

                else:
                    print(f"\n ")
                    print('=' * 62)
                    print(f"Error: Enter a letter (e.g. 'a' or 'b') or type 'exit' or 'back': ")
                    print('=' * 62)

        #Option #2: Scatterplots
        elif user_input == '2':
            while True:
                print(f"This stage displays scatterplot visualizations between two variables of your choice by state. ")
                variables = ['Median Home Values', 'Bachelor Degrees', 'Per Capita Income', 'Median Household Income', 'Median Family Income', 'Population', 'Number of Households', 'Number of Families']
                wikipedia_variables = variables[2:]
                for i, var in enumerate(variables, start=1):
                    print(f'[{i}] {var}')

                first_entry = input(f"\nSelect a number for a x-axis variable (e.g. 1, 2) or type 'back' or 'exit': ")
                second_entry = input(f'Select a number for a y-axis variable: ')

                if first_entry.strip().lower() == 'exit' or second_entry.strip().lower() == 'exit':
                    print(f'\nBye!')
                    quit()

                elif first_entry.strip().lower() == 'back' or second_entry.strip().lower() == 'back':
                    break

                elif first_entry.isdigit() and second_entry.isdigit():
                    first_var = variables[int(first_entry)-1]
                    second_var = variables[int(second_entry)-1]

                    states = viz_functions.scrapeStateNames(zillow_data)
                    x_values = viz_functions.identifyVariable(int(first_entry))
                    y_values = viz_functions.identifyVariable(int(second_entry))

                    scatter_data = go.Scatter(
                        x=x_values,
                        y=y_values,
                        text=states,
                        marker={'symbol':'circle', 'size':20, 'color': 'green'},
                        mode='markers+text',
                        textposition="top center",
                    )

                    basic_layout = go.Layout(title=f"{first_var} versus {second_var}")
                    fig = go.Figure(data=scatter_data, layout=basic_layout)
                    fig.write_html("scatter.html", auto_open=True)

                else:
                    print(f"\n ")
                    print('=' * 62)
                    print(f"[Error] Please type the number of the path you want to pursue. ")
                    print('=' * 62)


        #Option #3: Search a State
        elif user_input == '3':
            while True: #Complete
                state_search = input(f'\nEnter a state name (e.g. Michigan, michigan) or "exit" or "back": ')
                string_accomodation = state_search.lower().strip()

                if string_accomodation == 'exit':
                    print(f'\nBye!')
                    quit()

                elif string_accomodation == 'back':
                    break

                elif string_accomodation in zillow_data.keys(): #any dictionary will do
                    interactive_elements.list_all_details(state=state_search)

                else:
                    print(f'\n[Error] Type a state for a detailed search or "exit" or "back": ')

        else:
            print(f"\n ")
            print('=' * 62)
            print(f"[Error] Please type the number of the path you want to pursue. ")
            print('=' * 62)






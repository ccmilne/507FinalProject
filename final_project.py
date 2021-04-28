#################################
##### Name: Cameron Milne
##### Uniqname: ccmilne
#################################

from requests_oauthlib import OAuth1
from bs4 import BeautifulSoup
import requests, json, csv, time, operator
import sqlite3, os
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


### Caching
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
    '''Converts the Zillow Dictionary back into a CSV file

    The CSV file used in the build_zillow_dictionary function converted the raw
    data into a dictionary in order for data cleaning. Now, it's being converted
    back to a CSV file in order for the data to be uploaded to the database.
    The function iterates through the dictionary keys and appends each key, value
    to a row in the csv file.

    Parameters
    ----------
    zillow_dict: a specific zillow dictionary produced from build_zillow_dictionary()

    returns:
    --------
    CSV file: 'zillow.csv'
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
    '''Parses Census dictionary and cleans data

    Iterates through the dictionary produced by the get_census_data()
    and removes capitalization, U.S. territories, and headers.

    Parameters
    ----------
    census_data: a dictionary produced by get_census_data()

    returns
    -------
    state_bach_dict: cleaned dictionary
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
    '''Converts the Census Dictionary into a CSV file

    The Census API was loaded into the file into a json and converted into a
    dictionary for data cleaning. Now, it's being converted back to a CSV file 
    in order for the data to be uploaded to the database. The function iterates 
    through the dictionary and appends each key, value to a row in the csv file.

    Parameters
    ----------
    census_dict: a specific census dictionary produced from parse_census_data()

    returns:
    --------
    CSV file: 'census.csv'
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
    '''Parses Wikipedia dictionary and cleans data

    Iterates through the dictionary produced by the build_wikipedia_dictionary()
    and removes capitalization, dollar signs, and commas.

    Parameters
    ----------
    wiki_dict: a dictionary produced by build_wikipedia_dictionary()

    returns
    -------
    new_dict: cleaned dictionary
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
    '''Converts the Wikipedia Dictionary into a CSV file

    The CSV file used in build_wikipedia_dictionary() converted the raw
    data into a dictionary in order for data cleaning. Now, it's being converted
    back to a CSV file in order for the data to be uploaded to the database.
    The function iterates through the dictionary keys and appends each key, list of values
    to a row in the csv file.

    Parameters
    ----------
    wiki_dict: a specific wikipedia dictionary produced from clean_wikipedia_dictionary()

    returns:
    --------
    CSV file: 'wikipedia.csv'
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
'''
Functions are stored in interactive_elements.py
'''



if __name__ == "__main__":

    #Calling Zillow functions
    zillow_data = build_zillow_dictionary('zillow_by_state.csv')
    convert_zillow_to_CSV(zillow_data)

    #Calling Census functions
    census_data = get_census_data('https://api.census.gov/data/2019/acs/acs5?get=NAME,B15003_022E&for=state:*&key=3d095bab381ec8a891e05c0fe05da954f2710317')
    census_data_parsed = parse_census_data(census_data=census_data)
    convert_census_to_csv(census_data_parsed)

    #Calling Wikipedia functions
    wikipedia_data = build_wikipedia_dictionary()
    wikipedia_data_cleaned = clean_wikipedia_dictionary(wikipedia_data)
    convert_wikipedia_to_csv(wikipedia_data_cleaned)

    #Calling SQLite functions
    database_functions.create_connection('project.db')
    database_functions.create_zillow_table()
    database_functions.create_census_table()
    database_functions.create_wikipedia_table()

    #Interactive Console
    interactive_elements.opening_statement()

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
                            interactive_elements.list_all_states_under_budget(int(budget_entry))

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
                            interactive_elements.incomeComparer(int(income_entry))

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






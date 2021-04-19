#################################
##### Name: Cameron Milne
##### Uniqname: ccmilne
#################################

from requests_oauthlib import OAuth1
from bs4 import BeautifulSoup
import requests, json, csv, time, operator
import sqlite3, logging, sys
from sqlite3 import Error

### Caching
CACHE_FILENAME = 'cache_census.json'
CACHE_DICT = {}
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

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        zillow_states = {}
        for row in reader: #every row in reader contains a state and the median home price values by month
            state_name = row[2]
            recent_month = row[-1]

            #add data to dictionary
            if state_name not in zillow_states:
                zillow_states[state_name] = recent_month

        del zillow_states['RegionName']

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


### Census Data
def get_census_data(url):
    '''fetches Census API

    Given a search term, this function will retrieve the iTunes
    media types that correspond with the search term for a specified
    number of returns (specified in limit).

    Parameters
    ----------
    term: any term (Robert Downey Jr., The Beatles, etc.)
    limit: the number of searches returned across categories

    returns:
    -------
    Dictionary of key as State and value as # of residents with a bachelor's degree
    '''
    unique_key = url[-1:39]
    #print(unique_key)

    if unique_key in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[unique_key]

    else:
        print("Fetching")
        CACHE_DICT[unique_key] = requests.get(url).json()
        save_cache(CACHE_DICT)
        return CACHE_DICT[unique_key]

def parse_census_data(census_data):
    '''
    '''
    state_bach_dict = {}

    for individual_list in census_data:
        state_bach_dict[individual_list[0]] = individual_list[1]

    del state_bach_dict['NAME']
    del state_bach_dict['Puerto Rico']

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
        # wiki_dictionary[item[1]] = item[2]
        wiki_dictionary[item[1]] = [item[2], item[3], item[4], item[5], item[6], item[7]]

    # Drop U.S. and territories
    del wiki_dictionary['United States']
    del wiki_dictionary['American Samoa']
    del wiki_dictionary['Northern Mariana Islands']
    del wiki_dictionary['Puerto Rico']
    del wiki_dictionary['Guam']
    del wiki_dictionary['U.S. Virgin Islands']

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

### SQLite3 / Database
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def create_zillow_table():
    conn = sqlite3.connect("project.db")
    curs = conn.cursor()
    curs.execute("DROP TABLE IF EXISTS Zillow;")
    curs.execute("CREATE TABLE IF NOT EXISTS Zillow (State TEXT PRIMARY KEY, Median_Home_Value INT);")

    reader = csv.reader(open('zillow.csv', 'r'), delimiter=',')
    insert_str = '''
        INSERT INTO Zillow
        VALUES (?, ?)
    '''

    for row in reader:
        curs.execute(insert_str, (
            row[0], #State
            row[1], #Median Home Value
        ))

    conn.commit()

def create_census_table():
    conn = sqlite3.connect("project.db")
    curs = conn.cursor()
    curs.execute("DROP TABLE IF EXISTS Census;")
    curs.execute("CREATE TABLE IF NOT EXISTS Census (State TEXT PRIMARY KEY, Bachelor_Degrees INT);")

    reader = csv.reader(open('census.csv', 'r'), delimiter=',')
    insert_str = '''
        INSERT INTO Census
        VALUES (?, ?)
    '''
    for row in reader:
        curs.execute(insert_str, (
            row[0], #State
            row[1], #Bachelor Degrees
        ))

    conn.commit()

def create_wikipedia_table():
    conn = sqlite3.connect("project.db")
    curs = conn.cursor()
    curs.execute("DROP TABLE IF EXISTS Wikipedia;")

    create_str = '''
        CREATE TABLE IF NOT EXISTS Wikipedia (
            State TEXT PRIMARY KEY,
            Per_Capita_Income INT,
            Median_Household_Income INT,
            Median_Family_Income INT,
            Population INT,
            Number_of_Households INT,
            Number_of_Families INT
            )
    '''
    curs.execute(create_str)
    reader = csv.reader(open('wikipedia.csv', 'r'), delimiter=',')
    insert_str = '''
        INSERT INTO Wikipedia
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''

    for row in reader:
        curs.execute(insert_str, (
            row[0], #State
            row[1], #Per_Capita_Income
            row[2], #Median_Household_Income
            row[3], #Median_Family_Income
            row[4], #Population
            row[5], #Number_of_Households
            row[6], #Number_of_Families
        ))

    conn.commit()







if __name__ == "__main__":



    #Calling Zillow Data
    zillow_data = build_zillow_dictionary('zillow_by_state.csv')
    #print(zillow_data)
    zillow_csv = convert_zillow_to_CSV(zillow_data)

    #Calling Census API
    census_data = get_census_data('https://api.census.gov/data/2019/acs/acs5?get=NAME,B15003_022E&for=state:*&key=3d095bab381ec8a891e05c0fe05da954f2710317')
    #print(census_data)
    census_data_parsed = parse_census_data(census_data=census_data)
    #print(census_data_parsed)
    census_csv = convert_census_to_csv(census_data_parsed)
    #print(census_csv)

    wikipedia_data = build_wikipedia_dictionary()
    #print(wikipedia_data)
    wikipedia_data_cleaned = clean_wikipedia_dictionary(wikipedia_data)
    #print(wikipedia_data_cleaned)
    wikipedia_csv = convert_wikipedia_to_csv(wikipedia_data_cleaned)

    #SQLite
    #create_connection('project.db')
    zill = create_zillow_table()
    cens = create_census_table()
    wiki = create_wikipedia_table()








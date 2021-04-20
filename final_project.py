#################################
##### Name: Cameron Milne
##### Uniqname: ccmilne
#################################

from requests_oauthlib import OAuth1
from bs4 import BeautifulSoup
import requests, json, csv, time, operator
import sqlite3, logging, sys, os
from sqlite3 import Error

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

def build_zillow_complete_dict(csv_file):
    ''' '''
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        zillow_states = {}
        for row in reader: #every row in reader contains a state and the median home price values by month
            # size_rank = row[1]
            state_name = row[2]
            # region_type = row[3]
            # state_abbrev = row[4]
            all_months = list(row[5:])

            #add data to dictionary
            if state_name not in zillow_states:
                zillow_states[state_name] = all_months

        del zillow_states['RegionName']

    return zillow_states

def convert_zillow_complete_to_csv(zillow_complete_dict):
    '''
    '''
    fields = ['State',
        '1_31_1996', '2_29_1996', '3_31_1996', '4_30_1996', '5_31_1996', '6_30_1996', '7_31_1996', '8_31_1996', '9_30_1996', '10_31_1996', '11_30_1996', '12_31_1996',
        '1_31_1997', '2_28_1997', '3_31_1997', '4_30_1997', '5_31_1997', '6_30_1997', '7_31_1997', '8_31_1997', '9_30_1997', '10_31_1997', '11_30_1997', '12_31_1997',
        '1_31_1998', '2_28_1998', '3_31_1998', '4_30_1998', '5_31_1998', '6_30_1998', '7_31_1998', '8_31_1998', '9_30_1998', '10_31_1998', '11_30_1998', '12_31_1998',
        '1_31_1999', '2_28_1999', '3_31_1999', '4_30_1999', '5_31_1999', '6_30_1999', '7_31_1999', '8_31_1999', '9_30_1999', '10_31_1999', '11_30_1999', '12_31_1999',
        '1_31_2000', '2_29_2000', '3_31_2000', '4_30_2000', '5_31_2000', '6_30_2000', '7_31_2000', '8_31_2000', '9_30_2000', '10_31_2000', '11_30_2000', '12_31_2000',
        '1_31_2001', '2_28_2001', '3_31_2001', '4_30_2001', '5_31_2001', '6_30_2001', '7_31_2001', '8_31_2001', '9_30_2001', '10_31_2001', '11_30_2001', '12_31_2001', 
        '1_31_2002', '2_28_2002', '3_31_2002', '4_30_2002', '5_31_2002', '6_30_2002', '7_31_2002', '8_31_2002', '9_30_2002', '10_31_2002', '11_30_2002', '12_31_2002', 
        '1_31_2003', '2_28_2003', '3_31_2003', '4_30_2003', '5_31_2003', '6_30_2003', '7_31_2003', '8_31_2003', '9_30_2003', '10_31_2003', '11_30_2003', '12_31_2003', 
        '1_31_2004', '2_29_2004', '3_31_2004', '4_30_2004', '5_31_2004', '6_30_2004', '7_31_2004', '8_31_2004', '9_30_2004', '10_31_2004', '11_30_2004', '12_31_2004', 
        '1_31_2005', '2_28_2005', '3_31_2005', '4_30_2005', '5_31_2005', '6_30_2005', '7_31_2005', '8_31_2005', '9_30_2005', '10_31_2005', '11_30_2005', '12_31_2005', 
        '1_31_2006', '2_28_2006', '3_31_2006', '4_30_2006', '5_31_2006', '6_30_2006', '7_31_2006', '8_31_2006', '9_30_2006', '10_31_2006', '11_30_2006', '12_31_2006', 
        '1_31_2007', '2_28_2007', '3_31_2007', '4_30_2007', '5_31_2007', '6_30_2007', '7_31_2007', '8_31_2007', '9_30_2007', '10_31_2007', '11_30_2007', '12_31_2007', 
        '1_31_2008', '2_29_2008', '3_31_2008', '4_30_2008', '5_31_2008', '6_30_2008', '7_31_2008', '8_31_2008', '9_30_2008', '10_31_2008', '11_30_2008', '12_31_2008', 
        '1_31_2009', '2_28_2009', '3_31_2009', '4_30_2009', '5_31_2009', '6_30_2009', '7_31_2009', '8_31_2009', '9_30_2009', '10_31_2009', '11_30_2009', '12_31_2009', 
        '1_31_2010', '2_28_2010', '3_31_2010', '4_30_2010', '5_31_2010', '6_30_2010', '7_31_2010', '8_31_2010', '9_30_2010', '10_31_2010', '11_30_2010', '12_31_2010', 
        '1_31_2011', '2_28_2011', '3_31_2011', '4_30_2011', '5_31_2011', '6_30_2011', '7_31_2011', '8_31_2011', '9_30_2011', '10_31_2011', '11_30_2011', '12_31_2011', 
        '1_31_2012', '2_29_2012', '3_31_2012', '4_30_2012', '5_31_2012', '6_30_2012', '7_31_2012', '8_31_2012', '9_30_2012', '10_31_2012', '11_30_2012', '12_31_2012', 
        '1_31_2013', '2_28_2013', '3_31_2013', '4_30_2013', '5_31_2013', '6_30_2013', '7_31_2013', '8_31_2013', '9_30_2013', '10_31_2013', '11_30_2013', '12_31_2013', 
        '1_31_2014', '2_28_2014', '3_31_2014', '4_30_2014', '5_31_2014', '6_30_2014', '7_31_2014', '8_31_2014', '9_30_2014', '10_31_2014', '11_30_2014', '12_31_2014', 
        '1_31_2015', '2_28_2015', '3_31_2015', '4_30_2015', '5_31_2015', '6_30_2015', '7_31_2015', '8_31_2015', '9_30_2015', '10_31_2015', '11_30_2015', '12_31_2015', 
        '1_31_2016', '2_29_2016', '3_31_2016', '4_30_2016', '5_31_2016', '6_30_2016', '7_31_2016', '8_31_2016', '9_30_2016', '10_31_2016', '11_30_2016', '12_31_2016', 
        '1_31_2017', '2_28_2017', '3_31_2017', '4_30_2017', '5_31_2017', '6_30_2017', '7_31_2017', '8_31_2017', '9_30_2017', '10_31_2017', '11_30_2017', '12_31_2017', 
        '1_31_2018', '2_28_2018', '3_31_2018', '4_30_2018', '5_31_2018', '6_30_2018', '7_31_2018', '8_31_2018', '9_30_2018', '10_31_2018', '11_30_2018', '12_31_2018', 
        '1_31_2019', '2_28_2019', '3_31_2019', '4_30_2019', '5_31_2019', '6_30_2019', '7_31_2019', '8_31_2019', '9_30_2019', '10_31_2019', '11_30_2019', '12_31_2019', 
        '1_31_2020', '2_29_2020', '3_31_2020', '4_30_2020', '5_31_2020', '6_30_2020', '7_31_2020', '8_31_2020', '9_30_2020', '10_31_2020', '11_30_2020', '12_31_2020', 
        '1_31_2021', '2_28_2021']

    rows = []

    for key, value_list in zillow_complete_dict.items():
        row = []
        row.append(key)

        for val in value_list:
            row.append(val)

        rows.append(row)

    filename = 'zillow_complete.csv'
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

    with open("zillow.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        insert_str = '''
            INSERT INTO Zillow
            VALUES (?, ?)
        '''

        for row in csvreader:
            curs.execute(insert_str, (
                row[0], #State
                row[1], #Median Home Value
            ))

    conn.commit()

# def create_z2_table():
#     conn = sqlite3.connect("project.db")
#     curs = conn.cursor()
#     curs.execute("DROP TABLE IF EXISTS Zillow_Complete;")

#     create_str = '''
#         CREATE TABLE IF NOT EXISTS Zillow_Complete (
#             State TEXT PRIMARY KEY,
#             1_31_1996 INT,2_29_1996 INT,3_31_1996 INT,4_30_1996 INT,5_31_1996 INT,6_30_1996 INT,7_31_1996 INT,8_31_1996 INT,9_30_1996 INT,10_31_1996 INT,11_30_1996 INT,12_31_1996 INT,1_31_1997 INT,2_28_1997 INT,3_31_1997 INT,4_30_1997 INT,
#             5_31_1997 INT,6_30_1997 INT,7_31_1997 INT,8_31_1997 INT,9_30_1997 INT,10_31_1997 INT,11_30_1997 INT,12_31_1997 INT,1_31_1998 INT,2_28_1998 INT,3_31_1998 INT,4_30_1998 INT,5_31_1998 INT,6_30_1998 INT,7_31_1998 INT,8_31_1998 INT,9_30_1998 INT,10_31_1998 INT,11_30_1998 INT,12_31_1998 INT,1_31_1999 INT,2_28_1999 INT,3_31_1999 INT,4_30_1999 INT,5_31_1999 INT,6_30_1999 INT,7_31_1999 INT,8_31_1999 INT,9_30_1999 INT,10_31_1999 INT,11_30_1999 INT,12_31_1999 INT,1_31_2000 INT,2_29_2000 INT,3_31_2000 INT,4_30_2000 INT,5_31_2000 INT,6_30_2000 INT,7_31_2000 INT,8_31_2000 INT,9_30_2000 INT,10_31_2000 INT,11_30_2000 INT,12_31_2000 INT,1_31_2001 INT,2_28_2001 INT,3_31_2001 INT,4_30_2001 INT,5_31_2001 INT,6_30_2001 INT,7_31_2001 INT,8_31_2001 INT,9_30_2001 INT,10_31_2001 INT,11_30_2001 INT,12_31_2001 INT,1_31_2002 INT,2_28_2002 INT,3_31_2002 INT,4_30_2002 INT,5_31_2002 INT,6_30_2002 INT,7_31_2002 INT,8_31_2002 INT,9_30_2002 INT,10_31_2002 INT,11_30_2002 INT,12_31_2002 INT,1_31_2003 INT,2_28_2003 INT,3_31_2003 INT,4_30_2003 INT,5_31_2003 INT,6_30_2003 INT,7_31_2003 INT,8_31_2003 INT,9_30_2003 INT,10_31_2003 INT,11_30_2003 INT,12_31_2003 INT,1_31_2004 INT,2_29_2004 INT,3_31_2004 INT,4_30_2004 INT,5_31_2004 INT,6_30_2004 INT,7_31_2004 INT,8_31_2004 INT,9_30_2004 INT,10_31_2004 INT,11_30_2004 INT,12_31_2004 INT,1_31_2005 INT,2_28_2005 INT,3_31_2005 INT,4_30_2005 INT,5_31_2005 INT,6_30_2005 INT,7_31_2005 INT,8_31_2005 INT,9_30_2005 INT,10_31_2005 INT,11_30_2005 INT,12_31_2005 INT,1_31_2006 INT,2_28_2006 INT,3_31_2006 INT,4_30_2006 INT,5_31_2006 INT,6_30_2006 INT,7_31_2006 INT,8_31_2006 INT,9_30_2006 INT,10_31_2006 INT,11_30_2006 INT,12_31_2006 INT,1_31_2007 INT,2_28_2007 INT,3_31_2007 INT,4_30_2007 INT,5_31_2007 INT,6_30_2007 INT,7_31_2007 INT,8_31_2007 INT,9_30_2007 INT,10_31_2007 INT,11_30_2007 INT,12_31_2007 INT,1_31_2008 INT,2_29_2008 INT,3_31_2008 INT,4_30_2008 INT,5_31_2008 INT,6_30_2008 INT,7_31_2008 INT,8_31_2008 INT,9_30_2008 INT,10_31_2008 INT,11_30_2008 INT,12_31_2008 INT,1_31_2009 INT,2_28_2009 INT,3_31_2009 INT,4_30_2009 INT,5_31_2009 INT,6_30_2009 INT,7_31_2009 INT,8_31_2009 INT,9_30_2009 INT,10_31_2009 INT,11_30_2009 INT,12_31_2009 INT,1_31_2010 INT,2_28_2010 INT,3_31_2010 INT,4_30_2010 INT,5_31_2010 INT,6_30_2010 INT,7_31_2010 INT,8_31_2010 INT,9_30_2010 INT,10_31_2010 INT,11_30_2010 INT,12_31_2010 INT,1_31_2011 INT,2_28_2011 INT,3_31_2011 INT,4_30_2011 INT,5_31_2011 INT,6_30_2011 INT,7_31_2011 INT,8_31_2011 INT,9_30_2011 INT,10_31_2011 INT,11_30_2011 INT,12_31_2011 INT,1_31_2012 INT,2_29_2012 INT,3_31_2012 INT,4_30_2012 INT,5_31_2012 INT,6_30_2012 INT,7_31_2012 INT,8_31_2012 INT,        9_30_2012 INT,10_31_2012 INT,11_30_2012 INT,12_31_2012 INT,1_31_2013 INT,2_28_2013 INT,3_31_2013 INT,4_30_2013 INT,5_31_2013 INT,6_30_2013 INT,7_31_2013 INT,8_31_2013 INT,9_30_2013 INT,10_31_2013 INT,11_30_2013 INT,12_31_2013 INT,1_31_2014 INT,2_28_2014 INT,3_31_2014 INT,4_30_2014 INT,5_31_2014 INT,6_30_2014 INT,7_31_2014 INT,8_31_2014 INT,9_30_2014 INT,10_31_2014 INT,11_30_2014 INT,12_31_2014 INT,1_31_2015 INT,2_28_2015 INT,3_31_2015 INT,4_30_2015 INT,5_31_2015 INT,6_30_2015 INT,7_31_2015 INT,8_31_2015 INT,9_30_2015 INT,10_31_2015 INT,11_30_2015 INT,12_31_2015 INT,1_31_2016 INT,2_29_2016 INT,3_31_2016 INT,4_30_2016 INT,5_31_2016 INT,6_30_2016 INT,7_31_2016 INT,8_31_2016 INT,9_30_2016 INT,10_31_2016 INT,11_30_2016 INT,12_31_2016 INT,1_31_2017 INT,2_28_2017 INT,3_31_2017 INT,4_30_2017 INT,5_31_2017 INT,6_30_2017 INT,7_31_2017 INT,8_31_2017 INT,9_30_2017 INT,10_31_2017 INT,11_30_2017 INT,12_31_2017 INT,1_31_2018 INT,2_28_2018 INT,3_31_2018 INT,4_30_2018 INT,5_31_2018 INT,6_30_2018 INT,7_31_2018 INT,8_31_2018 INT,9_30_2018 INT,10_31_2018 INT,11_30_2018 INT,12_31_2018 INT,1_31_2019 INT,2_28_2019 INT,3_31_2019 INT,4_30_2019 INT,5_31_2019 INT,6_30_2019 INT,7_31_2019 INT,8_31_2019 INT,9_30_2019 INT,10_31_2019 INT,11_30_2019 INT,12_31_2019 INT,1_31_2020 INT,2_29_2020 INT,3_31_2020 INT,4_30_2020 INT,5_31_2020 INT,6_30_2020 INT,7_31_2020 INT,8_31_2020 INT,9_30_2020 INT,10_31_2020 INT,11_30_2020 INT,12_31_2020 INT,1_31_2021 INT,2_28_2021 INT
#         )
#     '''

#     curs.execute(create_str)

#     with open("zillow_by_state.csv", "r") as csvfile:
#         csvreader = csv.reader(csvfile)
#         next(csvreader)
#         insert_str = '''
#             INSERT INTO Zillow_Complete
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
#                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
#                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
#                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
#                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
#                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
#                 )
#             '''

#         for row in csvreader:
#             curs.execute(insert_str, (
#                 # row[0], #State
#                 # row[1], #Median Home Value
#                 row[0:]
#             ))

#     conn.commit()


def create_census_table():
    conn = sqlite3.connect("project.db")
    curs = conn.cursor()
    curs.execute("DROP TABLE IF EXISTS Census;")
    curs.execute("CREATE TABLE IF NOT EXISTS Census (State TEXT PRIMARY KEY, Bachelor_Degrees INT);")

    with open("census.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        insert_str = '''
            INSERT INTO Census
            VALUES (?, ?)
        '''
        for row in csvreader:
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
    with open("wikipedia.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        insert_str = '''
            INSERT INTO Wikipedia
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''

        for row in csvreader:
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

    #Calling Zillow functions
    zillow_data = build_zillow_dictionary('zillow_by_state.csv')
    convert_zillow_to_CSV(zillow_data)
    zillow_complete = build_zillow_complete_dict('zillow_by_state.csv')
    convert_zillow_complete_to_csv(zillow_complete)

    #Calling Census functions
    census_data = get_census_data('https://api.census.gov/data/2019/acs/acs5?get=NAME,B15003_022E&for=state:*&key=3d095bab381ec8a891e05c0fe05da954f2710317')
    census_data_parsed = parse_census_data(census_data=census_data)
    convert_census_to_csv(census_data_parsed)

    #Calling Wikipedia functions
    wikipedia_data = build_wikipedia_dictionary()
    wikipedia_data_cleaned = clean_wikipedia_dictionary(wikipedia_data)
    convert_wikipedia_to_csv(wikipedia_data_cleaned)

    #Calling SQLite functions
    create_connection('project.db')
    create_zillow_table()
    #create_z2_table()
    create_census_table()
    create_wikipedia_table()








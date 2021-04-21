# Interactive Elements
import final_project
from bs4 import BeautifulSoup
import requests, json, csv, time, operator

### Initial Chunks
def opening_statement():
    '''
    '''
    import final_project
    print(f"\nThis program explores data related to home values, bachelor degree statistics, and family finance. Here are some of the variables you can explore by state: ")
    print('-' * 26)
    print(f"1. Median Home Values")
    print(f"2. Per Capita Income")
    print(f"3. Median Household Income")
    print(f"4. Median Family Income")
    print(f"5. Population")
    print(f"6. Number of Households")
    print(f"7. Number of Families")
    print(f"8. Bachelor Degrees")
    print('-' * 26)
    print(f"In order to get started, type the number of the path below to explore different relationships")

def provide_initial_options():
    '''
    '''
    import final_project
    print(f'\nOptions:')
    print(f"1. Compare your personal finances with state averages")
    print(f"2. Compare States")
    print(f"3. Search by State")

### State Search Functions
def list_zillow_details(state, zillow_data):
    '''
    '''
    import final_project
    state_entry = state.strip().lower()

    matched_columns = {}

    if state_entry in zillow_data.keys():
        matched_columns['State'] = state
        matched_columns['Median Home Value'] = zillow_data[state_entry]

    for key, val in matched_columns.items():
        print(f"{key}: {val}")

def list_wikipedia_details(state, wikipedia_data):
    '''
    '''
    import final_project
    state_entry = state.strip().lower()

    matched_columns = {}

    if state_entry in wikipedia_data.keys():
        variable_list = wikipedia_data[state_entry]
        matched_columns['State'] = state
        matched_columns['Per Capita Income'] = variable_list[0]
        matched_columns['Median Household Income'] = variable_list[1]
        matched_columns['Median Family Income'] = variable_list[2]
        matched_columns['Population'] = variable_list[3]
        matched_columns['Number of Households'] = variable_list[4]
        matched_columns['Number of Families'] = variable_list[5]

    for key, val in matched_columns.items():
        print(f"{key}: {val}")

def list_census_details(state, census_data):
    '''
    '''
    import final_project
    state_entry = state.strip().lower()

    matched_columns = {}

    if state_entry in census_data.keys():
        matched_columns['State'] = state
        matched_columns['Bachelor Degrees'] = census_data[state_entry]

    for key, val in matched_columns.items():
        print(f"{key}: {val}")

def list_all_details(state):
    '''
    '''
    import final_project

    print('=' * 30)
    print(f"Details on {state}")
    print('=' * 30)

    print(f"\nZillow")
    print('-' * 30)
    zillow_data = final_project.build_zillow_dictionary('zillow_by_state.csv')
    list_zillow_details(state=state, zillow_data=zillow_data)

    print(f"\nWikipedia")
    print('-' * 30)
    wikipedia_data = final_project.build_wikipedia_dictionary()
    wikipedia_data_cleaned = final_project.clean_wikipedia_dictionary(wikipedia_data)
    list_wikipedia_details(state=state, wikipedia_data=wikipedia_data_cleaned)

    print(f"\nCensus API")
    print('-' * 30)
    census_data = final_project.get_census_data('https://api.census.gov/data/2019/acs/acs5?get=NAME,B15003_022E&for=state:*&key=3d095bab381ec8a891e05c0fe05da954f2710317')
    census_data_parsed = final_project.parse_census_data(census_data=census_data)
    list_census_details(state=state, census_data=census_data_parsed)


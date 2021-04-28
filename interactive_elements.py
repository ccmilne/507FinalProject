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

### Compare Personal Finance Functions
def list_all_states_above_budget(budget_input):
    '''
    '''
    import final_project
    zillow_data = final_project.build_zillow_dictionary('zillow_by_state.csv')
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
    import final_project
    print('=' * 30)
    print(f"You entered: {income_input}")
    wikipedia_data = final_project.build_wikipedia_dictionary()
    wikipedia_data_cleaned = final_project.clean_wikipedia_dictionary(wikipedia_data)
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


import requests, json, csv
import plotly.graph_objects as go
import final_project

### Plotly
def scrapeStateNames(dictionary):
    '''
    Used for Census and Zillow:
    '''
    import final_project
    sorted_dict = sorted(dictionary)
    return sorted_dict

def scrapeVariable(dictionary):
    '''
    '''
    import final_project
    newlist = []
    sorted_dict = dict(sorted(dictionary.items()))
    for key, val in sorted_dict.items():
        newlist.append(int(val))
    return newlist

def scrapeWikipediaVariables(dictionary, variable_position):
    '''
    '''
    import final_project
    newlist = []
    sorted_dict = dict(sorted(dictionary.items()))
    #print(sorted_dict)
    for key, value_list in sorted_dict.items():
        new_value_list = []
        for value in value_list:
            new_value_list.append(int(value))
        newlist.append(new_value_list)
    #print(newlist)
    desired_variables = []
    for item in newlist:
        desired_variables.append(item[variable_position-1])
    #print(desired_variables)
    return desired_variables

def identifyVariable(number_entry):
    '''
    '''
    import final_project
    zillow_data = final_project.build_zillow_dictionary('zillow_by_state.csv')
    census_data = final_project.get_census_data('https://api.census.gov/data/2019/acs/acs5?get=NAME,B15003_022E&for=state:*&key=3d095bab381ec8a891e05c0fe05da954f2710317')
    census_data_parsed = final_project.parse_census_data(census_data=census_data)
    wikipedia_data = final_project.build_wikipedia_dictionary()
    wikipedia_data_cleaned = final_project.clean_wikipedia_dictionary(wikipedia_data)

    variables = ['Median Home Values', 'Bachelor Degrees', 'Per Capita Income', 'Median Household Income', 'Median Family Income', 'Population', 'Number of Households', 'Number of Families']
    var = variables[number_entry-1]

    if var == 'Median Home Values':
        x_value = scrapeVariable(zillow_data)

    elif var == 'Bachelor Degrees':
        x_value = scrapeVariable(census_data_parsed)

    else:
        adjustment = number_entry - 2
        x_value = scrapeWikipediaVariables(wikipedia_data_cleaned, variable_position=adjustment)

    return x_value

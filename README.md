# 507FinalProject

This project explores relationships between educational attainment and family finance metrics, offering a snapshot of the costliness of living in certain states. 
The data sources used:
- Zillow's [HMVI Research Data](https://www.zillow.com/research/data/)
- U.S. [Census API](https://api.census.gov/data/2019/acs/acs5?get=NAME,B15003_022E&for=state:*&key=3d095bab381ec8a891e05c0fe05da954f2710317)
- Wikipedia's [List of States and Territories by Income](https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_income )

The project offers users several ways of interacting with the data. 
The first is an interactive console that provides three paths and the second is a Flask web browser display. 

***Interactive Console***
1. Compare your personal finances with state averages

The first path allows the user to select from two options:
(a) Enter a budget for a home, (b) Compare your income across states.
These options enable a user to input their budget or income and compare with other states to determine the most affordable options based on median values.

2. Compare States

The second path uses a library called Plotly to produce scatterplots of any two variables of choice.
When using this option, a user can choose two variables from this list: 'Median Home Values', 'Bachelor Degrees', 'Per Capita Income', 'Median Household Income', 'Median Family Income', 'Population', 'Number of Households', 'Number of Families.'
The resulting scatterplot will include all fifty states and the District of Columbia. 

3. Search by State

The final search element allows a user to explore the above variables at a state level where all of the data is printed for them. 

***Flask***

Using Flask's web browser framework, this project also displays the data sourced and used in HTML formats. 

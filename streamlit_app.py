import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
from vega_datasets import data
alt.data_transformers.enable("vegafusion")

st.caption('A data visualization project by Jinge Mao, Zhirou Li.')

st.write("\n")

# Define the navigation menu
menu = ["Trends", "Death", "Income"]
choice = st.sidebar.selectbox("App Navigation", menu)

# Show different content based on navigation choice
if choice == "Trends":
    st.header("Policy, Opinions and Trends")

    st.subheader('_What\'s the Childhood Vaccination policies of each country?_')
    st.subheader('Global Childhood Vaccination Policies Map')

    source = alt.topo_feature(data.world_110m.url, 'countries')

    vaccination_data = pd.read_csv('https://raw.githubusercontent.com/MartinMao2000/bmi706-project/main/data/vaccination_data_code.csv')

    policy_color_map = {
        'Mandatory': '#66c2a5',
        'Recommended': '#8da0cb',
        'No source found': 'grey',
        'Mandatory for School Entry': 'yellow'# Add or adjust categories based on your CSV
        # Add other policies as needed
    }

    # Map the policy to a color for each c4	ountry
    vaccination_data['color'] = vaccination_data['Childhood vaccination policy'].map(policy_color_map)

    # Load the world map
    source = alt.topo_feature(data.world_110m.url, 'countries')

    # Merge your vaccination_data with the world map data here
    # This step is conceptual; actual implementation requires matching country codes between your CSV data and the topojson
    # For this example, let's assume 'vaccination_data' now includes a 'id' column matching the topojson country identifiers

    # Create the map visualization
    world_map = alt.Chart(source).mark_geoshape().encode(
        color=alt.Color('color:N', scale=None),
        tooltip=['Country:N', 'Childhood vaccination policy:N']  # Adjust as necessary
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(vaccination_data, 'country-code', ['Country','color', 'name', 'Childhood vaccination policy'])  
    ).project(
        type='equirectangular'
    ).properties(
        width=600,
        height=300
    )


    width = 600
    height  = 300
    project = 'equirectangular'

    # a gray map using as the visualization background
    background = alt.Chart(source
    ).mark_geoshape(
        fill='#aaa',
        stroke='white'
    ).properties(
        width=width,
        height=height
    ).project(project)

    # Combine the background map with the colored countries
    final_map = background + world_map


    # Create a DataFrame for the legend
    legend_data = pd.DataFrame({
        'Childhood vaccination policy': ['Mandatory', 'Recommended', 'No source found', 'Mandatory for School Entry'],
        'color': ['#66c2a5', '#8da0cb', 'grey', 'yellow']
    })

    # Create a legend chart
    legend = alt.Chart(legend_data).mark_square(size=100).encode(
        y=alt.Y('Childhood vaccination policy:N', axis=alt.Axis(title="Vaccination Policy")),
        color=alt.Color('color:N', scale=None, legend=None)
    ).properties(
        title="Legend"
    )

    # Combine the map with the legend
    # Adjust spacing as needed
    final_viz = alt.hconcat(final_map, legend, spacing=30)

    # Display the combined visualization
    final_viz

    # Define a list of continents
    continents = ['Africa', 'Asia', 'Europe', 'North America', 'South America', 'Australia', 'Antarctica']

    # Create a dropdown menu for the user to select a continent
    selected_continent = st.selectbox('Select a continent:', continents)

    # Define the center points and zoom levels for each continent
    continent_focus = {
        'Africa': {'center': [20, 0], 'scale': 200},
        'Asia': {'center': [100, 40], 'scale': 200},
        'Europe': {'center': [15, 50], 'scale': 200},
        'North America': {'center': [-90, 40], 'scale': 200},
        'South America': {'center': [-60, -15], 'scale': 200},
        'Australia': {'center': [134, -25], 'scale': 200},
        'Antarctica': {'center': [0, -90], 'scale': 200}
    }

    # Get the center and zoom level for the continent selected by the user
    focus = continent_focus[selected_continent]

    # Adjust the projection of the map
    world_map = world_map.project(
        type='mercator',
        scale=focus['scale'],
        center=focus['center']
    )

    # Display the map
    st.altair_chart(world_map, use_container_width=True)

    st.subheader('Preview of Source Data')

    # Data preview (show a subset or the entire DataFrame as needed)
    st.dataframe(vaccination_data)  # Adjust the number of rows as needed

    # Enable download of the vaccination_data as CSV
    csv = vaccination_data.to_csv(index=False)
    st.download_button(
        label="Download vaccination data as CSV",
        data=csv,
        file_name='vaccination_data.csv',
        mime='text/csv',
    )

    st.write("\n")  
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    st.subheader('_What\'s the relationship between people\'s belief towards vaccinations and the prevalence of disease?_')
    st.subheader('2019 Measles Prevalence vs Vaccine Effectiveness Disagreement')

    st.caption('The number of children with measles per 100,000 children under five years old is plotted against the percentage of respondents who disagree that vaccines are effective.')

    # Reload the dataset after execution state reset
    data_path = 'https://raw.githubusercontent.com/MartinMao2000/bmi706-project/main/data/measles-prevalence-vaccine-attitudes.csv'
    vaccine_attitudes = pd.read_csv(data_path)

   # Extract continent information for the year 2015
    continents = vaccine_attitudes[vaccine_attitudes['Year'] == 2015][['Entity', 'Continent']].drop_duplicates()
    continent_dict = continents.set_index('Entity')['Continent'].to_dict()

    # Add continent information to the data for the year 2019
    vaccine_attitudes['Continent'] = vaccine_attitudes['Entity'].map(continent_dict)

    # Filter the data for the year 2019
    data_2019 = vaccine_attitudes[vaccine_attitudes['Year'] == 2019].dropna(subset=[
        'measles_cases',
        'attitude'
    ])

    # Assign colors to each country based on their continent for 2019
    continent_colors = {
        'Africa': 'blue', 'Europe': 'green', 'North America': 'red',
        'Oceania': 'purple', 'South America': 'orange', 'Asia': 'yellow'
    }
    data_2019['color'] = data_2019['Continent'].map(continent_colors)


    # Remove rows where 'Continent' column is null
    data_2019 = vaccine_attitudes[(vaccine_attitudes['Year'] == 2019) & (vaccine_attitudes['Continent'].notnull())]

    # Streamlit country selection box with default selection of a few countries
    default_selections = ['China', 'India', 'United States']  # As an example
    selected_countries = st.multiselect(
        'Select countries',
        options=data_2019['Entity'].unique(),
        default=default_selections
    )

    # Create base chart including color legend
    base = alt.Chart(data_2019).mark_circle(opacity=0.5, color='lightgrey').encode(
        x=alt.X('attitude:Q', axis=alt.Axis(title='Share of people who disagree the effectiveness of vaccines(%)')),
        y=alt.Y('measles_cases:Q', axis=alt.Axis(title='Measles Prevalence in Children ')),
        color=alt.Color('Continent:N', legend=alt.Legend(title="Continent"))  # Use continent names as color legend
    )

    # If countries are selected, create highlighted chart
    if selected_countries:
        highlighted = alt.Chart(data_2019[data_2019['Entity'].isin(selected_countries)]).mark_circle().encode(
            x='attitude:Q',
            y='measles_cases:Q',
            color=alt.Color('Continent:N', legend=alt.Legend(title="Continent")),  # Use continent names as color legend
            tooltip=['Entity', 'attitude', 'measles_cases', 'Continent']
        ) + alt.Chart(data_2019[data_2019['Entity'].isin(selected_countries)]).mark_text(dy=-10).encode(
            x='attitude:Q',
            y='measles_cases:Q',
            text='Entity:N'
        )
        final_chart = alt.layer(base, highlighted).properties(
            width=600,
            height=400
        )
    else:
        final_chart = base.properties(
            title='2019 Measles Prevalence vs Vaccine Effectiveness Disagreement',
            width=600,
            height=400
        )

    # Display the chart
    st.altair_chart(final_chart)

    st.subheader('Preview of Source Data')
    # Data preview
    st.dataframe(data_2019)  # Adjust the number of rows as needed

    # Enable download of the filtered_data as CSV
    csv = data_2019.to_csv(index=False)
    st.download_button(
        label="Download measles prevalence vs vaccine attitudes data as CSV",
        data=csv,
        file_name='measles-prevalence-vaccine-attitudes.csv',
        mime='text/csv',
    )

    st.write("\n")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    st.subheader('_What\'s the vaccinations coverage (and diffences between countries) trend over time?_')
    st.subheader('Vaccination Coverage Over Time by Country and Vaccine')


  # Load the dataset
    vaccination_data_path = 'https://raw.githubusercontent.com/MartinMao2000/bmi706-project/main/data/global-vaccination-coverage.csv'
    vaccination_coverage = pd.read_csv(vaccination_data_path)

    # Data preprocessing
    vaccine_names = {
        'BCG': 'Tuberculosis (BCG)',
        'DTP3': 'Diphtheria/tetanus/pertussis (DTP3)',
        'HepB3': 'Hepatitis B (HepB3)',
        'Hib3': 'H. influenza type b (Hib3)',
        'IPV1': 'Inactivated polio vaccine (IPV)',
        'MCV1': 'Measles, first dose (MCV1)',
        'PCV3': 'Pneumococcal vaccine (PCV3)',
        'Pol3': 'Polio (Pol3)',
        'RCV1': 'Rubella (RCV1)',
        'RotaC': 'Rotavirus (RotaC)',
        'YFV': 'Yellow fever (YFV)'
    }
    vaccination_data_long = vaccination_coverage.melt(id_vars=['Entity', 'Code', 'Year'], var_name='Vaccine', value_name='Coverage')
    vaccination_data_long['Vaccine'] = vaccination_data_long['Vaccine'].str.replace(r' \(% of one-year-olds immunized\)', '', regex=True)
    vaccination_data_long['Vaccine'] = vaccination_data_long['Vaccine'].map(vaccine_names).fillna(vaccination_data_long['Vaccine'])

    # Streamlit controls
    # Country selection
    countries = sorted(vaccination_coverage['Entity'].unique().tolist())
    default_countries = ['United States', 'India', 'China']  # Example, default selection
    selected_countries = st.multiselect('Select countries', countries, default=default_countries)

    # Vaccine selection
    vaccines = list(vaccine_names.values())
    default_vaccines = ['Measles, first dose (MCV1)', 'Polio (Pol3)', 'Diphtheria/tetanus/pertussis (DTP3)']  # Example, default selection
    selected_vaccines = st.multiselect('Select vaccines', vaccines, default=default_vaccines)

    # Year selection
    years = vaccination_coverage['Year'].unique()
    years = np.sort(years)
    min_year, max_year = st.slider("Select Year Range", int(years.min()), int(years.max()), (int(years.min()), int(years.max())))

    # Data filtering
    filtered_data = vaccination_data_long[
        (vaccination_data_long['Entity'].isin(selected_countries)) & 
        (vaccination_data_long['Vaccine'].isin(selected_vaccines)) &
        (vaccination_data_long['Year'] >= min_year) &
        (vaccination_data_long['Year'] <= max_year)
    ]

    # Create the chart
    chart = alt.Chart(filtered_data).mark_point(filled=True).encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y('Coverage:Q', title='Vaccine Coverage(%)'),
        color=alt.Color('Entity:N', legend=alt.Legend(title='Country')),
        shape=alt.Shape('Vaccine:N', legend=alt.Legend(title='Vaccine Names')),
        tooltip=['Entity', 'Year', 'Vaccine', 'Coverage']
    ).properties(
        width=800,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)


    st.subheader('Preview of Source Data')
    # Data preview
    st.dataframe(filtered_data)  # Adjust the number of rows as needed

    # Enable download of the filtered_data as CSV
    csv = filtered_data.to_csv(index=False)
    st.download_button(
        label="Download filtered vaccination coverage data as CSV",
        data=csv,
        file_name='filtered_vaccination_coverage_data.csv',
        mime='text/csv',
    )

    
elif choice == "Death":
    st.subheader('_How have Deaths caused by vaccine-preventable diseases changed over time?_')
    st.subheader("Deaths caused by vaccine-preventable diseases")

    data_path = 'https://raw.githubusercontent.com/MartinMao2000/bmi706-project/main/data/deaths-caused-by-vaccine-preventable-diseases-over-time.csv'
    data = pd.read_csv(data_path)

    # Convert data
    disease_columns = data.columns[3:]  # Select all columns starting from the fourth one
    melted_data = data.melt(id_vars=['Entity', 'Code', 'Year'], 
                            value_vars=disease_columns, 
                            var_name='Disease', 
                            value_name='Deaths')

    # Streamlit user interaction widgets
    countries = melted_data['Entity'].unique()
    selected_countries = st.multiselect('Select countries:', countries, default=['Spain', 'Egypt', 'Haiti'])

    years = melted_data['Year'].unique()
    year_range = st.slider('Select a year range:', min_value=min(years), max_value=max(years), value=(min(years), max(years)))

    # Filter data based on user selection
    filtered_data = melted_data[(melted_data['Entity'].isin(selected_countries)) & 
                                (melted_data['Year'] >= year_range[0]) & 
                                (melted_data['Year'] <= year_range[1])]

    # Create a 3x3 grid of charts
    charts = []
    for disease in disease_columns:
        # Filter data for each disease
        disease_data = filtered_data[filtered_data['Disease'] == disease]
        
        # Create a chart if data exists
        if not disease_data.empty:
            chart = alt.Chart(disease_data).mark_line().encode(
                x='Year:O',
                y=alt.Y('Deaths:Q', scale=alt.Scale(zero=False)),
                color='Entity:N',
                tooltip=['Entity', 'Year', 'Deaths']
            ).properties(
                title=disease.replace('Deaths - ', '').replace(' - Sex: Both - Age: All Ages (Number)', ''),
                width=200,  # Set a fixed width to fit the 3x3 grid
                height=200  # Set a fixed height
            )
            charts.append(chart)

    # Combine charts into a 3x3 grid
    grid_chart = alt.vconcat(*[
        alt.hconcat(*charts[i:i+3]) for i in range(0, len(charts), 3)
    ], spacing=10).resolve_scale(
        x='shared',  # Make all charts share the same x-axis
        y='independent'
    ).properties(
        title=f"Vaccine-preventable diseases deaths over time (Comparing Countries)"
    )

    # Display the chart in Streamlit
    st.altair_chart(grid_chart, use_container_width=True)

elif choice == "Income":
    # Add a title
    st.subheader('_How does Vaccination Coverage vary with GDP over time?_')
    st.subheader('Vaccination Coverage by GDP')


    # Load the data
    vaccination_income_data_path = 'https://raw.githubusercontent.com/MartinMao2000/bmi706-project/main/data/vaccination-coverage-by-income-in.csv'
    vaccination_income_data = pd.read_csv(vaccination_income_data_path)

    # Create a mapping from country to continent based on the data from 2015
    continent_mapping = vaccination_income_data[vaccination_income_data['Year'] == 2015][['Entity', 'Continent']].set_index('Entity').to_dict()['Continent']
    vaccination_income_data['Continent'] = vaccination_income_data['Entity'].map(continent_mapping)

    # Clean the data, removing NaN values
    vaccination_income_data_cleaned = vaccination_income_data.dropna(subset=['DTP3 (% of one-year-olds immunized)', 'GDP per capita (output, multiple price benchmarks)'])

    # Slider for selecting the year
    years = sorted(vaccination_income_data_cleaned['Year'].unique())
    selected_year = st.select_slider('Select Year', options=years, value=2015)

    # Filter data based on the selected year
    vaccination_income_data_filtered = vaccination_income_data_cleaned[vaccination_income_data_cleaned['Year'] == selected_year]

    # Multiselect for selecting countries
    selected_countries = st.multiselect(
        'Select countries',
        options=vaccination_income_data_filtered['Entity'].unique(),
        default=['United States', 'India', 'China', 'Brazil', 'Nigeria', 'Slovenia', 'South Africa', 'Peru', 'Norway', 'Palestine', 'North Macedonia', 'Laos', 'Kuwait', 'Honduras']  # Default options, specify as needed
    )

    # Filter data further based on selected countries
    filtered_data = vaccination_income_data_filtered[vaccination_income_data_filtered['Entity'].isin(selected_countries)]

    # Define the scatter plot
    points = alt.Chart(filtered_data).mark_circle(size=60).encode(
        x=alt.X('GDP per capita (output, multiple price benchmarks):Q', axis=alt.Axis(title='GDP per capita')),
        y=alt.Y('DTP3 (% of one-year-olds immunized):Q', axis=alt.Axis(title='DTP3 Immunized')),
        color='Continent:N',
        tooltip=['Entity', 'Year', 'DTP3 (% of one-year-olds immunized)', 'GDP per capita (output, multiple price benchmarks)', 'Continent']
    ).properties(
        width=1500,  # Set width to 700
        height=400  # Set height to 400
    )

    # Define the text layer
    text = points.mark_text(
        align='left',
        baseline='middle',
        dx=7  # Move the text to the right of the points
    ).encode(
        text='Entity:N'
    ).properties(
        width=1500,  # Set width to 700
        height=400  # Set height to 400
    )

    # Combine the scatter plot and text layer
    chart = alt.layer(points, text)

    # Display the chart in the Streamlit app
    st.altair_chart(chart, use_container_width=True)

    # Title and data frame for data preview
    st.subheader('Preview of Source Data')
    st.dataframe(vaccination_income_data_cleaned)  # Display a portion of the data for performance improvement

    # Option to download the cleaned data
    csv = vaccination_income_data_cleaned.to_csv(index=False)
    st.download_button(
        label="Download vaccination coverage by income data as CSV",
        data=csv,
        file_name='vaccination_coverage_by_income_data.csv',
        mime='text/csv',
    )

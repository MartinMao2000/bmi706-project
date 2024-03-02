import altair as alt
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    ### P1.2 ###
    cancer_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/cancer_ICD10.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Cancer", "Sex"],
        var_name="Age",
        value_name="Deaths",
    )

    pop_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/population.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Sex"],
        var_name="Age",
        value_name="Pop",
    )

    df = pd.merge(left=cancer_df, right=pop_df, how="left")
    df["Pop"] = df.groupby(["Country", "Sex", "Age"])["Pop"].fillna(method="bfill")
    df.dropna(inplace=True)

    df = df.groupby(["Country", "Year", "Cancer", "Age", "Sex"]).sum().reset_index()
    df["Rate"] = df["Deaths"] / df["Pop"] * 100_000

    return df

# Uncomment the next line when finished
df = load_data()
### P1.2 ###


st.write("## Age-specific cancer mortality rates")

### P2.1 ###
# replace with st.slider
# https://docs.streamlit.io/library/api-reference/widgets/st.slider
year = st.slider(
    label="Year", 
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=2012,
    step=1
)
subset = df[df["Year"] == year]
### P2.1 ###


### P2.2 ###
# replace with st.radio
# https://docs.streamlit.io/library/api-reference/widgets/st.radio
sex = st.radio(
    label="Sex",
    options=subset["Sex"].unique().tolist()
)
subset = subset[subset["Sex"] == sex]
### P2.2 ###


### P2.3 ###
# replace with st.multiselect
# (hint: can use current hard-coded values below as as `default` for selector)
# https://docs.streamlit.io/library/api-reference/widgets/st.multiselect
default_countries = [
    "Austria",
    "Germany",
    "Iceland",
    "Spain",
    "Sweden",
    "Thailand",
    "Turkey",
]
countries = st.multiselect(
    label="Countries",
    options=subset["Country"].unique().tolist(),
    default=default_countries
)
subset = subset[subset["Country"].isin(countries)]
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
# https://docs.streamlit.io/library/api-reference/widgets/st.selectbox
default_cancer = "Malignant neoplasm of stomach"
options = subset["Cancer"].unique().tolist()
cancer = st.selectbox(
    label='Cancer',
    options=options,
    index=options.index(default_cancer)
)
subset = subset[subset["Cancer"] == cancer]
### P2.4 ###


### P2.5 ###
ages = [
    "Age <5",
    "Age 5-14",
    "Age 15-24",
    "Age 25-34",
    "Age 35-44",
    "Age 45-54",
    "Age 55-64",
    "Age >64",
]

age_selection = alt.selection_interval(encodings=["x"])
country_selection = alt.selection_single(encodings=["y"])

heatmap = alt.Chart(subset[subset["Rate"] != 0]).mark_rect().encode(
    x=alt.X("Age", sort=ages),
    y=alt.Y("Country"),
    color=alt.Color("Rate", title="Mortality rate per 100k", scale=alt.Scale(type='log', domain=[0.01, 1000])),
    opacity=alt.condition(country_selection, alt.value(1), alt.value(0.1)),
    tooltip=["Rate"],
).properties(
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
    width=500
).add_selection(
    age_selection
)

bar = alt.Chart(subset).mark_bar().encode(
    x=alt.X("sum(Pop):Q", title='Sum of population size'),
    y=alt.Y("Country", sort="-x"),
    color=alt.value("#0068C9"),
    tooltip=[
        alt.Tooltip("sum(Pop):Q", title="Sum of population size"),
        "Country"
    ],
).properties(
    width=500
).transform_filter(
    age_selection
).add_selection(
    country_selection
)

### P2.5 ###

st.altair_chart(
    alt.vconcat(heatmap, bar),
    use_container_width=True
)

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")

import streamlit as st
import pandas as pd
import numpy as np
st.title('CoDe Graduation Project')
DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache #Streamlits cache command
def load_data(nrows): #Downloads data and put it into a Pandas dataframe, converst the date columns from text to datetime
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text('Loading data..')
data = load_data(10000)
data_load_state.text("Done! (using st.cache)")

current_data = st.text("Currently using dummy Uber Data from New York drawing from an AWS server")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Number of pickups by hour')
hist_value = np.histogram( #NumPy Histogram, numpy will be the main way to construct graphs in streamlit
    data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]

st.bar_chart(hist_value)

st.subheader("Map of all pickups")

hour_to_filter = st.slider('hour', 0, 23, 17)  #Streamlits inbuilt slider definition, format is :Name of Slider, minimum, maximum, default
filtered_data = data[data[DATE_COLUMN].dt.hour ==hour_to_filter] #Format is: Grab Pandas table through Definition, Grab only the Date Column from the Pandas table, grab only the hours from each pandas entry then filter it according to filter value
st.subheader(f'Map of all pickups at {hour_to_filter}:00')
st.map(filtered_data)
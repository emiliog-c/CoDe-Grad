import streamlit as st
#specklepy libraries
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
#import pandas
import pandas as pd
#import plotly express
import plotly.express as pxc

st.set_page_config(
    page_title="CoDe Graduation Project",
    page_icon="📊")

header = st.container()
input = st.container()
viewer = st.container()
report = st.container()
graphs = st.container()


with header:
    st.title ("CoDe Graduation Project: Speckle Visualisation Dashboard")

with input:
    st.subheader("Speckle Repository")
    serverCol, tokenCol = st.columns([1,3]) #ratio of the columns, token is 3 times larger than server column.
    speckleServer = serverCol.text_input("Server URL", "speckle.xyz", help="Speckle server to connect.")
    speckleToken = tokenCol.text_input("Speckle token", "087fea753d12f91a6f692c8ea087c1bf4112e93ed7", help="If you don't know how to get your token, take a look at this [link](<https://speckle.guide/dev/tokens.html>)👈")
    client = SpeckleClient(host=speckleServer) #SpecklePy Command, gets host according to the text input in speckleServer
    account = get_account_from_token(speckleToken, speckleServer) #applies the account with the data from the token and server input
    client.authenticate_with_account(account) #method command
    streams = client.stream.list() #Speckle Stream List
    streamNames = [s.name for s in streams]
    sName = st.selectbox(label="Select your stream", options=streamNames, help="Select your stream from the dropdown")
    st.text(dir(streamNames))
    stream = client.stream.search(sName)[0]
    branches = client.branch.list(stream.id)
    commits = client.commit.list(stream.id, limit=100)
    

with viewer:
    st.subheader("Latest Commit")
    commitID = str(commits[0].id)#Looks for the newest commit
    embed_src = "https://speckle.xyz/embed?stream="+stream.id+"&commit="+commitID
    st.components.v1.iframe(src=embed_src, width=600, height=400)

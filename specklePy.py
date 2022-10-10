import streamlit as st
#specklepy libraries
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
#import pandas
import pandas as pd
#import plotly express
import plotly.express as px

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
    speckleToken = tokenCol.text_input("Speckle token", "d2b80238f7f7ed8b655f0311571163f3a609849c85", help="In order to access the streams, the token must be able to read profile")
    client = SpeckleClient(host=speckleServer) #SpecklePy Command, gets host according to the text input in speckleServer
    account = get_account_from_token(speckleToken, speckleServer) #applies the account with the data from the token and server input
    client.authenticate_with_account(account) #method command
    streams = client.stream.list() #Speckle Stream List
    streamNames = [s.name for s in streams]
    sName = st.selectbox(label="Select your stream", options=streamNames, help="Select your stream from the dropdown")
    stream = client.stream.search(sName)[0]
    branches = client.branch.list(stream.id)
    commits = client.commit.list(stream.id, limit=100)
    

with viewer:
    st.subheader("Latest Commit")
    #commitID = str(commits[0].id)#Looks for the newest commit
    commitMessage = [d.message for d in commits]
    commitNum = [c.id for c in commits]
    df_commits = pd.DataFrame(list(zip(commitMessage, commitNum)),
                        columns =["Commit Message", "Commit ID"]) #Creates Pandas Dataframe with the commit message in the first column and the ID of it in the second
    cName = st.selectbox(label="Select your commit", options=commitMessage, help="Select your commit from the dropdown") #Shows the message in the Dropdown
    j = df_commits[df_commits['Commit Message'].str.contains(cName)]#Searches the Pandas Dataframe for the string that was chosen in the dropdown to find the ID in the dataframe. Problem with this is that duplicate commital messages will screw with the search system, so theres probably a much more efficient system of searching the pandas dataframe according to the index number instead of searching it according to the string, but thats for a later date.
    k = j.iloc[0]["Commit ID"]
    embed_src = "https://speckle.xyz/embed?stream="+stream.id+"&commit="+k
    st.text(embed_src)
    st.components.v1.iframe(src=embed_src, width=1200, height=800)

with graphs:
    st.subheader("Graphs")
    branch_graph_col, connector_graph_col, collaborator_graph_col = st.columns([2,1,1]) #columns for charts, will be the main way to order graphs
    commits= pd.DataFrame.from_dict([c.dict() for c in commits])
    apps = commits["sourceApplication"]
    apps = apps.value_counts().reset_index()
    apps.columns=["app","count"]
    fig = px.pie(apps, names=apps["app"],values=apps["count"], hole=0.5)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=1, r=1, t=1, b=1),
        height=200,
        )
    connector_graph_col.plotly_chart(fig, use_container_width=True)

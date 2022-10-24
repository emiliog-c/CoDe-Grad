import streamlit as st
#specklepy libraries
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
#import pandas
import pandas as pd
#import plotly express
import plotly.express as px
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from specklepy.serialization.base_object_serializer import BaseObjectSerializer

st.set_page_config(
    page_title="CoDe Graduation Project",
    page_icon="📊")

header = st.container()
input = st.container()
viewer = st.container()
graphs = st.container()
newblock = st.container()
minmax = st.container()

from specklepy.objects import Base
from specklepy.objects.geometry import Point

class time_period(Base):
    monthS: int
    monthE: int
    dayS: int
    dayE: int
    hourS: int
    hourE: int
    origin: Point = None

    def __init__(self, monthS=1, monthE=1, dayS=1, dayE=1, hourS=1, hourE=1, origin=Point(), **kwargs) -> None:
        super().__init__(**kwargs)
        # mark the origin as a detachable attribute
        self.add_detachable_attrs({"origin"})

        self.monthS = monthS
        self.monthE = monthE
        self.dayS = dayS
        self.dayE = dayE
        self.hourS = hourS
        self.hourE = hourE
        self.origin = origin

class minvalmaxval(Base):
    min: int
    max: int
    message: str
    origin: Point = None

    def __init__(self, min=1, max=1, message="test", origin=Point(), **kwargs) -> None:
        super().__init__(**kwargs)
        # mark the origin as a detachable attribute
        self.add_detachable_attrs({"origin"})

        self.message = message
        self.min = min
        self.max = max
        self.origin = origin

@st.cache(suppress_st_warning=True)


def view_model(s, k):
    embed_src = "https://speckle.xyz/embed?stream="+s.id+"&commit="+k
    st.text(embed_src)
    st.components.v1.iframe(src=embed_src, width=1200, height=800)

def send_commit_1(val1, val2, val3, val4, val5, val6, blocksName, comMessage):
    commit_button = st.button("Send Commit",key = 1)
    
    if commit_button:
            # this serialises the block and sends it to the transport
        periodBlock = time_period(monthS = int(val1), monthE = int(val2), dayS = int(val3), dayE = int(val4), hourS = int(val5), hourE = int(val6))
        transport = ServerTransport(client=client, stream_id=blocksName)
        hash = operations.send(base=periodBlock, transports=[transport])

        # you can now create a commit on your stream with this object
        commit_id = client.commit.create(
            stream_id=blocksName, 
            object_id=hash, 
            message=comMessage,
            )

def send_commit_2(val1, val2, blocksName, comMessage):
    commit_button2 = st.button("Send Commit", key=3)
    
    if commit_button2:
            # this serialises the block and sends it to the transport
        periodBlock = minvalmaxval(min = int(val1), max = int(val2), message=str(comMessage))
        transport = ServerTransport(client=client, stream_id=blocksName)
        hash = operations.send(base=periodBlock, transports=[transport])

        # you can now create a commit on your stream with this object
        commit_id = client.commit.create(
            stream_id=blocksName, 
            object_id=hash, 
            message=comMessage,
            )
            

def search(values, searchFor):
    for k in values:
        for v in values[k]:
            if searchFor in v:
                return k
    return None




with header:
    st.title ("CoDe Graduation Project: Speckle Visualisation Dashboard")

with input:
    st.subheader("Speckle Repository")
    serverCol, tokenCol = st.columns([1,3]) #ratio of the columns, token is 3 times larger than server column.
    speckleServer = serverCol.text_input("Server URL", "speckle.xyz", help="Speckle server to connect.")
    speckleToken = tokenCol.text_input("Speckle token", "57cd5333ad1bcb27f28318286cc970f398e4122ea8", help="In order to access the streams, the token must be able to read profile")
    client = SpeckleClient(host=speckleServer) #SpecklePy Command, gets host according to the text input in speckleServer
    account = get_account_from_token(speckleToken, speckleServer) #applies the account with the data from the token and server input
    client.authenticate_with_account(account) #method command
    streams = client.stream.list() #Speckle Stream List
    streamNames = [s.name for s in streams]
    sName = st.selectbox(label="Select your stream", options=streamNames, help="Select your stream from the dropdown")
    stream = client.stream.search(sName)[0]
    stream_name = stream.id
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
    iD = j.iloc[0]["Commit ID"]
    view_model(stream, iD)

with graphs:
    st.subheader("Graphs")
    commit = client.commit.get(stream_name, iD)
    transport3 = ServerTransport(client=client, stream_id=stream_name)
    res = operations.receive(commit.referencedObject, transport3)
    levels = res["@Data"]
    free = levels.get_member_names()
    lev2 = levels["@{0;0}"]
    received_base = client.object.get(stream_name, "e565f93c1af52caa0cdb37038fc18571")
    free2 = received_base.get_member_names()
    st.subheader(received_base["@objectType"])

    


with newblock:
    st.subheader("Commit New Block")
    streams2 = client.stream.list() #Speckle Stream List
    streamNames2 = [s.name for s in streams2]
    sName2 = st.selectbox(label="Select your stream", options=streamNames2, help="Select your stream from the dropdown", key=2)
    stream2 = client.stream.search(sName2)[0]
    stream_name2 = stream2.id
    stream__id2 = client.stream.get(id=sName2)
    commitName = st.text_input("Commit Name")
    monthSCol, monthECol = st.columns([1,1]) 
    daySCol, dayECol = st.columns([1,1]) 
    hourSCol, hourECol = st.columns([1,1])
    monthSval = monthSCol.number_input("Starting month for the analysis period")
    monthEval = monthECol.number_input("Ending month for the analysis period")
    daySval = daySCol.number_input("Starting day for the analysis period")
    dayEval = dayECol.number_input("Ending day for the analysis period")
    hourSval = hourSCol.number_input("Starting hour for the analysis period")
    hourEval = hourECol.number_input("Ending hour for the analysis period") 

    send_commit_1(monthSval, monthEval, daySval, dayEval, hourSval, hourEval, stream_name2, commitName)

with minmax:
    st.subheader("Min and Max Block")
    streams3 = client.stream.list() #Speckle Stream List
    streamNames3 = [s.name for s in streams3]
    sName3 = st.selectbox(label="Select your stream", options=streamNames3, help="Select your stream from the dropdown", key=4)
    stream3 = client.stream.search(sName3)[0]
    stream_name3 = stream3.id
    stream__id3 = client.stream.get(id=sName3)
    commitNameMin = st.text_input("Commit Min/Max Message")
    minCol, maxCol = st.columns([1,1])
    minVal = minCol.number_input("Minimum Value")
    maxVal = maxCol.number_input("Max Value")
    

    send_commit_2(minVal, maxVal, stream_name3, commitNameMin)


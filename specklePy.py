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

from collections import Counter



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
    st.components.v1.iframe(src=embed_src, width=800, height=800)

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
            branch_name="datetime", 
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
            branch_name= "minmax",
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

with st.sidebar:
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
    #commitID = str(commits[0].id)#Looks for the newest commit
    commitMessage = [d.message for d in commits]
    commitNum = [c.id for c in commits]
    df_commits = pd.DataFrame(list(zip(commitMessage, commitNum)),
                        columns =["Commit Message", "Commit ID"]) #Creates Pandas Dataframe with the commit message in the first column and the ID of it in the second
    cName = st.selectbox(label="Select your commit", options=commitMessage, help="Select your commit from the dropdown") #Shows the message in the Dropdown
    j = df_commits[df_commits['Commit Message'].str.contains(cName)]#Searches the Pandas Dataframe for the string that was chosen in the dropdown to find the ID in the dataframe. Problem with this is that duplicate commital messages will screw with the search system, so theres probably a much more efficient system of searching the pandas dataframe according to the index number instead of searching it according to the string, but thats for a later date.
    iD = j.iloc[0]["Commit ID"]
    
    
    with st.expander('Change time period of model'):
        branchs = client.branch.list(stream)
        commitName = st.text_input("New Commit Name")
        monthSCol, monthECol = st.columns([1,1]) 
        daySCol, dayECol = st.columns([1,1]) 
        hourSCol, hourECol = st.columns([1,1])
        monthSval = monthSCol.number_input("Starting month for the analysis period")
        monthEval = monthECol.number_input("Ending month for the analysis period")
        daySval = daySCol.number_input("Starting day for the analysis period")
        dayEval = dayECol.number_input("Ending day for the analysis period")
        hourSval = hourSCol.number_input("Starting hour for the analysis period")
        hourEval = hourECol.number_input("Ending hour for the analysis period") 

        send_commit_1(monthSval, monthEval, daySval, dayEval, hourSval, hourEval, stream_name, commitName)
    
    with st.expander("Change min and max of legend of model"):
        branchs2 = client.branch.list(stream)
        #bName2 = st.selectbox(label="Select your branch", options=branchs2, help="Select your branch from the dropdown", key=3)
        commitNameMin = st.text_input("Commit Min/Max Message")
        minCol, maxCol = st.columns([1,1])
        minVal = minCol.number_input("Minimum Value")
        maxVal = maxCol.number_input("Max Value")
    

        send_commit_2(minVal, maxVal, stream_name, commitNameMin)
        
with viewer:
    st.subheader("Speckle Viewer of chosen model")
    view_model(stream, iD)

with graphs:
    st.subheader("Graphs")
    branch_graph_col, connector_graph_col = st.columns([1,1])
    commit = client.commit.get(stream_name, iD)
    transport3 = ServerTransport(client=client, stream_id=stream_name)
    res = operations.receive(commit.referencedObject, transport3)
    check = res["@Data"]
    free2 = check.get_member_names() #gets all the attributes in the commit
    chars = '@' #check for detachable attributes
    selected_types = []
    agh = [idx for idx in free2 if idx[0].lower() == chars.lower()] #checks all the attribute names for the detachable ones, luckily when GH sends it through it puts the tree numbers on the outside for each object
    objects = []
    material = []
    check2 = agh[0]
    check3 = res["@Data"][check2][0]
    serializer = BaseObjectSerializer()
    uh = serializer.write_json(check3)
    if "@objectType" in str(uh): #does a simple check if the object is there, will be used when the drop downs for the various graphs will be added
        check4 = True
    else:
        check4 = False
    if check4 == True:
        for j in agh:
            yes = res["@Data"][j][0]["@objectType"]#loops through and grabs the object type accordingly
            objects.append(yes)
        for m in agh:
            noo = res["@Data"][m][0]["@material"]
            material.append(noo)
        
        cnt = Counter()
        cnt2 = Counter()
        for word in objects:
            cnt[word] += 1 #counts each time a word is repeated
        
        for word in material:
            cnt2[word] += 1

        cnt3 = dict(cnt)
        cnt4 = dict(cnt2)
        df1 = pd.DataFrame(list(cnt3.items()), columns = ['type', 'number']) #pandas dataframes for the plotly graphs
        df2 = pd.DataFrame(list(cnt4.items()), columns = ['material', 'number'])
        #ill change these for definitions when i have the time
        objectFig = px.pie(df1, names=df1['type'], values=df1['number'])
        objectFig.update_layout(
            showlegend=False,
            margin=dict(l=1,r=1,t=1,b=1),
            height=500,
            yaxis_scaleanchor="x",)
        materialFig = px.pie(df2, names=df2['material'], values=df2['number'])
        materialFig.update_layout(
            showlegend=False,
            margin=dict(l=1,r=1,t=1,b=1),
            height=500,
            yaxis_scaleanchor="x",)
        connector_graph_col.plotly_chart(objectFig, use_container_width=True)
        branch_graph_col.plotly_chart(materialFig, use_container_width=True)
    
    else:
        st.subheader("No Graphs to show")
        
    #definitely needs a clean up

    







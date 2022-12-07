import streamlit as st
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import collections
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from specklepy.serialization.base_object_serializer import BaseObjectSerializer
from specklepy.objects import Base
from specklepy.objects.geometry import Point

from collections import Counter
st.set_page_config(
    page_title="CoDe Graduation Project",
    page_icon="📊",
    layout="wide")

#Streamlit containers
header = st.container()
input = st.container()
viewer = st.container()
graphs = st.container()
newblock = st.container()
minmax = st.container()
metadata = st.expander("Metadata")


#For the time period filter
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

#For the Legend Min/Max filter
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
    #st.text(embed_src)
    st.components.v1.iframe(src=embed_src, width=800, height=800)

def send_commit_1(val1, val2, val3, val4, val5, val6, blocksName, comMessage, keyNum): #Time Period Filter function
    commit_button = st.button("Send Commit", key=keyNum)
    
    if commit_button:
            # this serialises the block and sends it to the transport
        periodBlock = time_period(monthS = int(val1), monthE = int(val2), dayS = int(val3), dayE = int(val4), hourS = int(val5), hourE = int(val6))
        transport = ServerTransport(client=client, stream_id=blocksName)
        hash = operations.send(base=periodBlock, transports=[transport])

        commit_id = client.commit.create(
            stream_id=blocksName,
            branch_name="datetime", 
            object_id=hash, 
            message=comMessage,
            )

def send_commit_2(val1, val2, blocksName, comMessage, keyNum): #Min/Max Legend changer function
    commit_button2 = st.button("Send Commit", key=keyNum)
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

class createBlock:
    def __init__(self, client, blockNum, key1, key2, key3, commitN1, monthSkey, monthEkey, daySkey, dayEkey, hourSkey, hourEkey, commit1, commMinkey, minValKey, maxValKey, commit2, minDenKey, maxDenKey, sBox1, sBox2, blockNum1, blockNum2, graphColN1, graphColN2,metaNum, key4, key5):
        self.client = client #Unlocked Client
        self.blockNum = blockNum #Block Number
        self.key1 = key1 #Block Text Input key
        self.key2 = key2 #Stream Select Input Key
        self.key3 = key3 #Commit Select Input Key
        self.commitN1 = commitN1 #Commit Name Key
        self.monthSkey = monthSkey
        self.monthEkey = monthEkey
        self.daySkey = daySkey
        self.dayEkey = dayEkey
        self.hourSkey = hourSkey
        self.hourEkey = hourEkey
        self.commit1 = commit1
        self.commMinkey = commMinkey
        self.minValKey = minValKey
        self.maxValKey = maxValKey
        self.commit2 = commit2
        self.minDenKey = minDenKey
        self.maxDenKey = maxDenKey
        self.sBox1 = sBox1 #Selection Box Key 1
        self.sBox2 = sBox2 #Selection Box Key 2
        self.streamNames = streamNames 
        self.blockNum1 = blockNum1
        self.blockNum2 = blockNum2
        self.graphColN1 = graphColN1
        self.graphColN2 = graphColN2
        self.metaNum = metaNum
        self.key4 = key4 #Stream selector for Time Period
        self.key5 = key5 #Stream selector for Min/Max

    def sideblock(self):
        bName1 = st.text_input("Block Name", key=self.key1, value = self.blockNum)
        sName = st.selectbox(label="Select your stream", options=self.streamNames, key=self.key2, help="Select your stream from the dropdown")
        stream = self.client.stream.search(sName)[0]
        stream_name = stream.id
        commits = self.client.commit.list(stream.id, limit=100)
        commitMessage = [d.message for d in commits]
        commitNum = [c.id for c in commits]
        commitDict = dict(zip(commitMessage, commitNum))
        cName = st.selectbox(label="Select your commit", options=commitDict, key=self.key3, help="Select your commit from the dropdown") #Shows the message in the Dropdown
        iD = commitDict[cName]
        with st.expander('Change time period of model'):
            streamC1 = st.selectbox(label="Select your Stream", options=self.streamNames, key=self.key4, help="Select your Stream from the dropdown")
            commitName = st.text_input("New Commit Name", key=self.commitN1)
            monthSCol, monthECol = st.columns([1,1]) 
            daySCol, dayECol = st.columns([1,1]) 
            hourSCol, hourECol = st.columns([1,1])
            monthSval = monthSCol.number_input("Starting month for the analysis period", key = self.monthSkey)
            monthEval = monthECol.number_input("Ending month for the analysis period", key = self.monthEkey)
            daySval = daySCol.number_input("Starting day for the analysis period", key = self.daySkey)
            dayEval = dayECol.number_input("Ending day for the analysis period", key = self.dayEkey)
            hourSval = hourSCol.number_input("Starting hour for the analysis period", key = self.hourSkey)
            hourEval = hourECol.number_input("Ending hour for the analysis period", key = self.hourEkey) 
            send_commit_1(monthSval, monthEval, daySval, dayEval, hourSval, hourEval, streamC1, commitName, self.commit1)
        
        with st.expander("Change min and max of legend of model"):
            streamC2 = st.selectbox(label="Select your Stream", options=self.streamNames, key=self.key5, help="Select your Stream from the dropdown")
            #bName2 = st.selectbox(label="Select your branch", options=branchs2, help="Select your branch from the dropdown", key=3)
            commitNameMin = st.text_input("Commit Min/Max Message", key=self.commMinkey)
            minCol, maxCol = st.columns([1,1])
            minVal = minCol.number_input("Minimum Value", key = self.minValKey)
            maxVal = maxCol.number_input("Max Value", key = self.maxValKey)
            send_commit_2(minVal, maxVal, streamC2, commitNameMin, self.commit2)
        
        with st.expander("Change min level of Density Check"):
            minColDen, maxColDen = st.columns([1,1])
            minValDen = minColDen.number_input("Minimum Value", key = self.minDenKey, value=0)
            maxValDen = maxColDen.number_input("Max Value", key = self.maxDenKey, value=999999999)

        
        selectBox1, selectBox2 = st.columns([1,1])
        graphs = {"Object Type": '@objectType', 'Material Type': '@material', "Viewer": "viewer", "Metadata": "metadata", "Density Chart": 'densityChart', "Mass Chart": "massChart"}
        gT1 = selectBox1.selectbox(label="Select your Graph Type", options=graphs, key=self.sBox1)
        gT2 = selectBox2.selectbox(label="Select your Graph Type", options=graphs, key=self.sBox2)
        commit = self.client.commit.get(sName, iD)
        moveAttributes = [cName, stream_name, iD, gT1, gT2, minValDen, maxValDen, bName1]
        return moveAttributes

    def graphInit(self, newVars):
        cName = newVars[0]
        stream_name = newVars[1]
        iD = newVars[2]
        gT1 = newVars[3]
        gT2 = newVars[4]
        minValDen = newVars[5]
        maxValDen = newVars[6]
        bName1 = newVars[7]
        with st.container():
            st.subheader(bName1)
            self.blockNum1, self.blockNum2 = st.columns([1,1])
            self.graphColN1, self.graphColN2 = st.columns([1,1])
            commit = self.client.commit.get(stream_name, iD)
            transport3 = ServerTransport(client=self.client, stream_id=stream_name)
            res = operations.receive(commit.referencedObject, transport3)
            graphs = {"Object Type": '@objectType', 'Material Type': '@material', "Viewer": "viewer", "Metadata": "metadata", "Density Chart": 'densityChart', "Mass Chart": "massChart"}
            gFull1 = (graphs[gT1])
            gFull2 = (graphs[gT2])
            def checkCheck(data1, graphChoice, colChoice, graphName):
                check0 = data1["@Data"]
                check1 = check0.get_member_names() #gets all the attributes in the commit
                chars = '@' #check for detachable attributes
                agh = [idx for idx in check1 if idx[0].lower() == chars.lower()] #checks all the attribute names for the detachable ones, luckily when GH sends it through it puts the tree numbers on the outside for each object
                check2 = agh[0]
                check3 = data1["@Data"][check2]
                numcheck = len(check3)
                check4 = data1["@Data"][check2][0]["geoProps"] #THIS IS THE CORRECT PATH
                serializer = BaseObjectSerializer()
                uh = serializer.write_json(check4)
                if graphChoice == "viewer":
                    embed_src = "https://speckle.xyz/embed?stream="+stream_name+"&commit="+iD
                    with colChoice:
                        st.text(graphName + " of commit " + cName)
                        st.components.v1.iframe(src=embed_src, width=1000, height=600)
                if graphChoice == "metadata":
                    check0 = res["@Data"]
                    check1 = check0.get_member_names() #gets all the attributes in the commit
                    chars = '@' #check for detachable attributes
                    agh = [idx for idx in check1 if idx[0].lower() == chars.lower()]
                    values = []
                    for x in range(numcheck):
                        yes1 = res["@Data"][agh[0]][x]["geoProps"]#loops through and grabs the object type accordingly
                        yes2 = yes1.get_member_names()
                        yes3 = res["@Data"][agh[0]][x]#loops through and grabs the object type accordingly
                        yes4 = yes3.get_member_names()
                        values.append(yes2)
                    emptDict = {}
                    colChoice.text("Metadata of " + cName)
                    with colChoice:
                        form = st.form(key=self.metaNum)
                        selected_paramsObj = form.multiselect("Select Object parameters", yes4)
                        selected_paramsGeo = form.multiselect("Select geoProps parameters", yes2)
                        form.form_submit_button("RUN")
                    for x in range(numcheck):
                        values = []
                        fire = res["@Data"][agh[0]][x]['geoProps']["@objectName"]#loops through and grabs the object type accordingly
                        for params in selected_paramsGeo:
                            checkcheck = res["@Data"][agh[0]][x]['geoProps'].get_member_names()
                            if params in checkcheck:
                                yes = res["@Data"][agh[0]][x]["geoProps"][params] #loops through and grabs the object type accordingly
                                values.append(yes)
                            else: 
                                nodata = str("No data")
                                values.append(nodata)
                            emptDict[fire] = values
                        for params in selected_paramsObj:
                            checkcheck = res["@Data"][agh[0]][x].get_member_names()
                            if params in checkcheck:
                                yes = res["@Data"][agh[0]][x][params] #loops through and grabs the object type accordingly
                                values.append(yes)
                            else: 
                                nodata = str("No data")
                                values.append(nodata)
                            emptDict[fire] = values
                    true_geoDF = pd.DataFrame(emptDict)
                    # result_GeoDict = pd.DataFrame.from_dict([GeoDict])
                    true_geoDF = true_geoDF.transpose()
                    parameters = selected_paramsGeo+ selected_paramsObj
                    true_geoDF.columns = parameters
                    #st.text(emptDict)
                    colChoice.table(true_geoDF)
                if graphChoice == "densityChart":
                    check0 = res["@Data"]
                    check1 = check0.get_member_names() #gets all the attributes in the commit
                    chars = '@' #check for detachable attributes
                    agh = [idx for idx in check1 if idx[0].lower() == chars.lower()]
                    values = []
                    emptDict = collections.defaultdict(list)
                    emptDict2 = {}
                    for x in range(numcheck):
                        values = []
                        values2 = []
                        mat = res["@Data"][agh[0]][x]['geoProps']["@material"]
                        den = res["@Data"][agh[0]][x]["geoProps"]['@density']#loops through and grabs the object type accordingly
                        checkz = res["@Data"][agh[0]][x]["geoProps"]['@ee']
                        eeDens = den*float(checkz)
                        if eeDens > minValDen:
                            if eeDens < maxValDen:
                                emptDict[mat].append(eeDens)
                            else:
                                emptDict[mat].append(0)
                        else:
                            emptDict[mat].append(0)
                        values2.append(float(checkz))
                    finDict = dict(emptDict)
                    for keys in finDict:
                        final = sum(finDict[keys])
                        finDict[keys] = final
                    emptDict2 = collections.defaultdict(list)
                    for keys in finDict:
                        emptDict2["Material Type"].append(keys)
                        emptDict2["kgCO2E/m2"].append(finDict[keys])
                    emptDict2 = dict(emptDict2)
                    fig = px.bar(emptDict2, x='Material Type', y='kgCO2E/m2')
                    colChoice.text(graphName + " of commit " + cName)
                    colChoice.plotly_chart(fig, use_container_width=True)
                if graphChoice == "massChart":
                    check0 = res["@Data"]
                    check1 = check0.get_member_names() #gets all the attributes in the commit
                    chars = '@' #check for detachable attributes
                    agh = [idx for idx in check1 if idx[0].lower() == chars.lower()]
                    values = []
                    emptDict = collections.defaultdict(list)
                    emptDict2 = {}
                    for x in range(numcheck):
                        values = []
                        values2 = []
                        mat = res["@Data"][agh[0]][x]['geoProps']["@material"]
                        den = res["@Data"][agh[0]][x]["geoProps"]['@density']#loops through and grabs the object type accordingly
                        emptDict[mat].append(float(den))
                    finDict = dict(emptDict)
                    for keys in finDict:
                        final = sum(finDict[keys])
                        finDict[keys] = final
                    emptDict2 = collections.defaultdict(list)
                    for keys in finDict:
                        emptDict2["Material Type"].append(keys)
                        emptDict2["Mass (m3)"].append(finDict[keys])
                    emptDict2 = dict(emptDict2)
                    fig = px.bar(emptDict2, x='Material Type', y='Mass (m3)')
                    colChoice.text(graphName + " of commit " + cName)
                    colChoice.plotly_chart(fig, use_container_width=True)
                else:
                    if graphChoice in str(uh): #does a simple check if the object is there, will be used when the drop downs for the various graphs will be added
                        check5 = True
                    elif "Objects.Geometry" in str(uh):
                        check5 = True
                    else:
                        check5 = False
                    if check5 == True:
                        if "Type" in graphName:
                            objects = []
                            for x in range(numcheck):
                                yes = data1["@Data"][agh[0]][x]["geoProps"][graphChoice]#loops through and grabs the object type accordingly
                                objects.append(yes)
                            cnt = Counter()
                            for word in objects:
                                cnt[word] += 1 #counts each time a word is repeated
                            cnt3 = dict(cnt)
                            df1 = pd.DataFrame(list(cnt3.items()), columns = ['type', 'number']) #pandas dataframes for the plotly graphs
                                #ill change these for definitions when i have the time
                            objectFig = px.pie(df1, names=df1['type'], values=df1['number'])
                            objectFig.update_layout(
                                showlegend=True,
                                margin=dict(l=1,r=1,t=1,b=1),
                                height=500,
                                yaxis_scaleanchor="x",)
                            colChoice.text(graphName + " of commit " + cName)
                            colChoice.plotly_chart(objectFig, use_container_width=True)
                        else:
                            colChoice.text("No Graph/Table to show")
            checkCheck(res, gFull1, self.graphColN1, gT1)
            checkCheck(res, gFull2, self.graphColN2, gT2)

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
    titleIn = st.text_input("Dashboard Name", key="dash1", value = "CoDe Graduation Project: Speckle Visualisation Dashboard")
    addButt, remButt = st.columns([1,1])
    if 'count' not in st.session_state:
        st.session_state.count = 1
    if addButt.button("Add box"):
        st.session_state.count += 1
    if st.session_state.count > 1:
        if remButt.button("Remove box"):
            st.session_state.count -= 1
    count = int(st.session_state.count)
    blockDict = {}
    for x in range (1, count):
        tempList=[]
        tempList.append(client)
        tempList.append(x)
        for z in range(1, 27):
            tempList.append(str(x)+"key"+str(z))
        blockDict["block{0}".format(x)] = tempList
    newDict = {}
    fluck = {}
    for y in range (1, count):
        newBlist = blockDict["block{0}".format(y)]
        newDict["cre{0}".format(y)] = createBlock(newBlist[0], newBlist[1], newBlist[2], newBlist[3], newBlist[4], newBlist[5], newBlist[6], newBlist[7], newBlist[8], newBlist[9], newBlist[10], newBlist[11], newBlist[12], newBlist[13], newBlist[14], newBlist[15], newBlist[16], newBlist[17], newBlist[18], newBlist[19], newBlist[20], newBlist[21], newBlist[22], newBlist[23], newBlist[24], newBlist[25], newBlist[26], newBlist[27])
        fluck["bre{0}".format(y)] = newDict["cre{0}".format(y)].sideblock()
with header:
    st.title(titleIn)
    for j in range (1, count):
        newDict["cre{0}".format(j)].graphInit(fluck["bre{0}".format(j)])

# get parameter value from parameter name
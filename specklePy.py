import streamlit as st
#specklepy libraries
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
#import pandas
import pandas as pd
#import plotly express
import plotly.express as px
import plotly.graph_objects as go
import collections

from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from specklepy.serialization.base_object_serializer import BaseObjectSerializer

st.set_page_config(
    page_title="CoDe Graduation Project",
    page_icon="📊",
    layout="wide")



header = st.container()
input = st.container()
viewer = st.container()
graphs = st.container()
newblock = st.container()
minmax = st.container()
metadata = st.expander("Metadata")

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
    #st.text(embed_src)
    st.components.v1.iframe(src=embed_src, width=800, height=800)

def send_commit_1(val1, val2, val3, val4, val5, val6, blocksName, comMessage, keyNum):
    commit_button = st.button("Send Commit", key=keyNum)
    
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

def send_commit_2(val1, val2, blocksName, comMessage, keyNum):
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


class graphBlock:
    def __init__(self, blockNum1, blockNum2, graphColN1, graphColN2, clientName, sName1, iD1, sName2, sBox1, sBox2, commitName, gT1, gT2, metaNum, denMin, denMax):
        self.blockNum1 = blockNum1
        self.blockNum2 = blockNum2
        self.graphColN1 = graphColN1
        self.graphColN2 = graphColN2
        self.clientName = clientName
        self.sName1 = sName1
        self.iD1 = iD1
        self.sName2 = sName2
        self.sBox1 = sBox1
        self.sBox2 = sBox2
        self.commitName = commitName
        self.gT1 = gT1
        self.gT2 = gT2
        self.metaNum = metaNum
        self.denMin = denMin
        self.denMax = denMax

    def graphInit(self):
        with st.container():
            self.blockNum1, self.blockNum2 = st.columns([1,1])
            self.graphColN1, self.graphColN2 = st.columns([1,1])
            commit = self.clientName.commit.get(self.sName1, self.iD1)
            transport3 = ServerTransport(client=self.clientName, stream_id=self.sName1)
            res = operations.receive(commit.referencedObject, transport3)
            graphs = {"Object Type": '@objectType', 'Material Type': '@material', "Viewer": "viewer", "Metadata": "metadata", "Density Chart": 'densityChart', "Mass Chart": "massChart"}
            #gT1 = self.blockNum1.selectbox(label="Select your Graph Type", options=graphs, key=self.sBox1)
            #gT2 = self.blockNum2.selectbox(label="Select your Graph Type", options=graphs, key=self.sBox2)
            gFull1 = (graphs[self.gT1])
            gFull2 = (graphs[self.gT2])
            def checkCheck(data1, graphChoice, colChoice, graphName):
                check = data1["@Data"]
                free2 = check.get_member_names() #gets all the attributes in the commit
                chars = '@' #check for detachable attributes
                selected_types = []
                agh = [idx for idx in free2 if idx[0].lower() == chars.lower()] #checks all the attribute names for the detachable ones, luckily when GH sends it through it puts the tree numbers on the outside for each object
                check2 = agh[0]
                check3 = data1["@Data"][check2]
                numcheck = len(check3)
                check5 = data1["@Data"][check2][0]
                check10 = data1["@Data"][check2][0]["geoProps"] #THIS IS THE CORRECT PATH
                #check4 = check3.get_member_names()
                serializer = BaseObjectSerializer()
                uh = serializer.write_json(check10)
                
                if graphChoice == "viewer":
                    embed_src = "https://speckle.xyz/embed?stream="+self.sName2.id+"&commit="+self.iD1
                    with colChoice:
                        st.text(graphName + " of commit " + self.commitName)
                        st.components.v1.iframe(src=embed_src, width=1000, height=600)
                if graphChoice == "metadata":
                    check = res["@Data"]
                    free2 = check.get_member_names() #gets all the attributes in the commit
                    chars = '@' #check for detachable attributes
                    selected_types = []
                    agh = [idx for idx in free2 if idx[0].lower() == chars.lower()]
                    types = []
                    values = []
                    for x in range(numcheck):
                        yes1 = res["@Data"][agh[0]][x]["geoProps"]#loops through and grabs the object type accordingly
                        yes2 = yes1.get_member_names()
                        yes3 = res["@Data"][agh[0]][x]#loops through and grabs the object type accordingly
                        yes4 = yes3.get_member_names()
                        values.append(yes2)
                    emptDict = {}
                    #yes4 = [x for x in yes2 if "Value" not in x]
                    #yes4 = [x for x in yes2 if "units" not in x]
                    #yes4 = [x for x in yes2 if "speckle_type" not in x]
                    colChoice.text("Metadata of " + self.commitName)
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
                    check = res["@Data"]
                    free2 = check.get_member_names() #gets all the attributes in the commit
                    chars = '@' #check for detachable attributes
                    selected_types = []
                    agh = [idx for idx in free2 if idx[0].lower() == chars.lower()]
                    types = []
                    values = []
                    emptDict = collections.defaultdict(list)
                    emptDict2 = {}
                    for x in range(numcheck):
                        values = []
                        values2 = []
                        fire = res["@Data"][agh[0]][x]['geoProps']["@material"]
                        objCheck = res["@Data"][agh[0]][x]['geoProps']["@material"]
                        yes1 = res["@Data"][agh[0]][x]["geoProps"]['@density']#loops through and grabs the object type accordingly
                        checkz = res["@Data"][agh[0]][x]["geoProps"]['@ee']
                        eeDens = yes1*float(checkz)
                        if eeDens > self.denMin:
                            if eeDens < self.denMax:
                                emptDict[fire].append(eeDens)
                            else:
                                emptDict[fire].append(0)
                        else:
                            emptDict[fire].append(0)
                        values2.append(float(checkz))
                        #values.append(objCheck)
                        #Cdict = Counter(emptDict) + Counter(emptDict2)
                        #for key in emptDict2:
                        #    if key in emptDict:
                         #       emptDict2[key] = (emptDict2[key]) + (emptDict[key])
                         #   else:
                           #     pass
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
                    colChoice.text(graphName + " of commit " + self.commitName)
                    colChoice.plotly_chart(fig, use_container_width=True)
                    #st.table(finDict)
                if graphChoice == "massChart":
                    check = res["@Data"]
                    free2 = check.get_member_names() #gets all the attributes in the commit
                    chars = '@' #check for detachable attributes
                    selected_types = []
                    agh = [idx for idx in free2 if idx[0].lower() == chars.lower()]
                    types = []
                    values = []
                    emptDict = collections.defaultdict(list)
                    emptDict2 = {}
                    for x in range(numcheck):
                        values = []
                        values2 = []
                        fire = res["@Data"][agh[0]][x]['geoProps']["@material"]
                        objCheck = res["@Data"][agh[0]][x]['geoProps']["@material"]
                        yes1 = res["@Data"][agh[0]][x]["geoProps"]['@density']#loops through and grabs the object type accordingly
                        emptDict[fire].append(float(yes1))
                        #values.append(objCheck)
                        #Cdict = Counter(emptDict) + Counter(emptDict2)
                        #for key in emptDict2:
                        #    if key in emptDict:
                         #       emptDict2[key] = (emptDict2[key]) + (emptDict[key])
                         #   else:
                           #     pass
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
                    colChoice.text(graphName + " of commit " + self.commitName)
                    colChoice.plotly_chart(fig, use_container_width=True)
                    #st.table(finDict)



                else:
                    if graphChoice in str(uh): #does a simple check if the object is there, will be used when the drop downs for the various graphs will be added
                        check4 = True
                    elif "Objects.Geometry" in str(uh):
                        check4 = True
                    else:
                        check4 = False
                    if check4 == True:
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
                            colChoice.text(graphName + " of commit " + self.commitName)
                            colChoice.plotly_chart(objectFig, use_container_width=True)
                        else:
                            colChoice.text("No Graph/Table to show")

                        
            checkCheck(res, gFull1, self.graphColN1, self.gT1)
            checkCheck(res, gFull2, self.graphColN2, self.gT2)
        


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
    st.subheader("Block 1")
    bName1 = st.text_input("Block Name", key="block1", value = "Block 1")
    sName = st.selectbox(label="Select your stream", options=streamNames, key="crazy1", help="Select your stream from the dropdown")
    stream = client.stream.search(sName)[0]
    stream_name = stream.id
    branches = client.branch.list(stream.id)
    commits = client.commit.list(stream.id, limit=100)
    commitMessage = [d.message for d in commits]
    commitNum = [c.id for c in commits]
    commitDict = dict(zip(commitMessage, commitNum))
    cName = st.selectbox(label="Select your commit", options=commitDict, key="crazy2", help="Select your commit from the dropdown") #Shows the message in the Dropdown
    iD = commitDict[cName]
    with st.expander('Change time period of model'):
        branchs = client.branch.list(stream)
        commitName = st.text_input("New Commit Name", key="time1")
        monthSCol, monthECol = st.columns([1,1]) 
        daySCol, dayECol = st.columns([1,1]) 
        hourSCol, hourECol = st.columns([1,1])
        monthSval = monthSCol.number_input("Starting month for the analysis period", key = "monthS1")
        monthEval = monthECol.number_input("Ending month for the analysis period", key = "monthE1")
        daySval = daySCol.number_input("Starting day for the analysis period", key = "dayS1")
        dayEval = dayECol.number_input("Ending day for the analysis period", key = "dayE1")
        hourSval = hourSCol.number_input("Starting hour for the analysis period", key = "hourS1")
        hourEval = hourECol.number_input("Ending hour for the analysis period", key = "hourE1") 
        send_commit_1(monthSval, monthEval, daySval, dayEval, hourSval, hourEval, stream_name, commitName, "comm1")
    
    with st.expander("Change min and max of legend of model"):
        branchs2 = client.branch.list(stream)
        #bName2 = st.selectbox(label="Select your branch", options=branchs2, help="Select your branch from the dropdown", key=3)
        commitNameMin = st.text_input("Commit Min/Max Message", key="minmax1")
        minCol, maxCol = st.columns([1,1])
        minVal = minCol.number_input("Minimum Value", key = "minVal1")
        maxVal = maxCol.number_input("Max Value", key = "maxVal1")
        send_commit_2(minVal, maxVal, stream_name, commitNameMin, "comm2")
    
    with st.expander("Change min level of Density Check"):
        minColDen, maxColDen = st.columns([1,1])
        minValDen = minColDen.number_input("Minimum Value", key = "minVal1Den", value=0)
        maxValDen = maxColDen.number_input("Max Value", key = "maxVal1Den", value=999999999)

    
    selectBox1, selectBox2 = st.columns([1,1])
    graphs = {"Object Type": '@objectType', 'Material Type': '@material', "Viewer": "viewer", "Metadata": "metadata", "Density Chart": 'densityChart', "Mass Chart": "massChart"}
    gT1 = selectBox1.selectbox(label="Select your Graph Type", options=graphs, key="sBox1")
    gT2 = selectBox2.selectbox(label="Select your Graph Type", options=graphs, key="sBox2")
    
    addButt, remButt = st.columns([1,1])
    if 'count' not in st.session_state:
        st.session_state.count = 0
    if addButt.button("Add box"):
        st.session_state.count += 1
    if st.session_state.count > 0:
        if remButt.button("Remove box"):
            st.session_state.count -= 1

    if st.session_state.count >= 1:
        st.subheader("Block 2")
        bName2 = st.text_input("Block Name", key="block2", value = "Block 2")
        sName2 = st.selectbox(label="Select your stream", options=streamNames, key="crazy3", help="Select your stream from the dropdown")
        stream2 = client.stream.search(sName2)[0]
        stream_name2 = stream2.id
        branches2 = client.branch.list(stream2.id)
        commits2 = client.commit.list(stream2.id, limit=100)
        commitMessage2 = [d.message for d in commits2]
        commitNum2 = [c.id for c in commits2]
        commitDict2 = dict(zip(commitMessage2, commitNum2))
        cName2 = st.selectbox(label="Select your commit", options=commitDict2, key="crazy4", help="Select your commit from the dropdown") #Shows the message in the Dropdown
        iD2 = commitDict2[cName2]
        with st.expander('Change time period of model'):
            branchs4 = client.branch.list(stream2)
            commitName2 = st.text_input("New Commit Name", key="time2")
            monthSCol2, monthECol2 = st.columns([1,1]) 
            daySCol2, dayECol2 = st.columns([1,1]) 
            hourSCol2, hourECol2 = st.columns([1,1])
            monthSval2 = monthSCol2.number_input("Starting month for the analysis period", key = "monthS2")
            monthEval2 = monthECol2.number_input("Ending month for the analysis period", key = "monthE2")
            daySval2 = daySCol2.number_input("Starting day for the analysis period", key = "dayS2")
            dayEval2 = dayECol2.number_input("Ending day for the analysis period", key = "dayE2")
            hourSval2 = hourSCol2.number_input("Starting hour for the analysis period", key = "hourS2")
            hourEval2 = hourECol2.number_input("Ending hour for the analysis period", key = "hourE2") 
            send_commit_1(monthSval2, monthEval2, daySval2, dayEval2, hourSval2, hourEval2, stream_name2, commitName2, "comm3")
    
        with st.expander("Change min and max of legend of model"):
            branchs5 = client.branch.list(stream2)
            #bName2 = st.selectbox(label="Select your branch", options=branchs2, help="Select your branch from the dropdown", key=3)
            commitNameMin2 = st.text_input("Commit Min/Max Message", key="minmax2")
            minCol2, maxCol2 = st.columns([1,1])
            minVal2 = minCol2.number_input("Minimum Value", key = "minVal2")
            maxVal2 = maxCol2.number_input("Max Value", key = "maxVal2")
            send_commit_2(minVal2, maxVal2, stream_name2, commitNameMin2, "comm4")
        with st.expander("Change min level of Density Check"):
            minColDen2, maxColDen2 = st.columns([1,1])
            minValDen2 = minColDen2.number_input("Minimum Value", key = "minVal2Den", value=0)
            maxValDen2 = maxColDen2.number_input("Max Value", key = "maxVal2Den", value=999999999)
        selectBox3, selectBox4 = st.columns([1,1])
        gT3 = selectBox3.selectbox(label="Select your Graph Type", options=graphs, key="sBox3")
        gT4 = selectBox4.selectbox(label="Select your Graph Type", options=graphs, key="sBox4")
    if st.session_state.count >= 2:
        st.subheader("Block 3")
        bName3 = st.text_input("Block Name", key="block3", value = "Block 3")
        sName3 = st.selectbox(label="Select your stream", options=streamNames, key="crazy5", help="Select your stream from the dropdown")
        stream3 = client.stream.search(sName2)[0]
        stream_name3 = stream3.id
        branches3 = client.branch.list(stream3.id)
        commits3 = client.commit.list(stream3.id, limit=100)
        commitMessage3 = [d.message for d in commits3]
        commitNum3 = [c.id for c in commits3]
        commitDict3 = dict(zip(commitMessage3, commitNum3))
        cName3 = st.selectbox(label="Select your commit", options=commitDict3, key="crazy6", help="Select your commit from the dropdown") #Shows the message in the Dropdown
        iD3 = commitDict3[cName3]
        with st.expander('Change time period of model'):
            branchs6 = client.branch.list(stream)
            commitName3 = st.text_input("New Commit Name", key="time3")
            monthSCol3, monthECol3 = st.columns([1,1]) 
            daySCol3, dayECol3 = st.columns([1,1]) 
            hourSCol3, hourECol3 = st.columns([1,1])
            monthSval3 = monthSCol3.number_input("Starting month for the analysis period", key = "monthS3")
            monthEval3 = monthECol3.number_input("Ending month for the analysis period", key = "monthE3")
            daySval3 = daySCol3.number_input("Starting day for the analysis period", key = "dayS3")
            dayEval3 = dayECol3.number_input("Ending day for the analysis period", key = "dayE3")
            hourSval3 = hourSCol3.number_input("Starting hour for the analysis period", key = "hourS3")
            hourEval3 = hourECol3.number_input("Ending hour for the analysis period", key = "hourE3") 
            send_commit_1(monthSval3, monthEval3, daySval3, dayEval3, hourSval3, hourEval3, stream_name3, commitName3, "comm5")
    
        with st.expander("Change min and max of legend of model"):
            branchs7 = client.branch.list(stream)
            #bName2 = st.selectbox(label="Select your branch", options=branchs2, help="Select your branch from the dropdown", key=3)
            commitNameMin3 = st.text_input("Commit Min/Max Message", key="minmax3")
            minCol3, maxCol3 = st.columns([1,1])
            minVal3 = minCol3.number_input("Minimum Value", key = "minVal3")
            maxVal3 = maxCol3.number_input("Max Value", key = "maxVal3")
            send_commit_2(minVal3, maxVal3, stream_name3, commitNameMin3, "comm6")
        with st.expander("Change min level of Density Check"):
            minColDen3, maxColDen3 = st.columns([1,1])
            minValDen3 = minColDen3.number_input("Minimum Value", key = "minVal3Den", value=0)
            maxValDen3 = maxColDen3.number_input("Max Value", key = "maxVal3Den", value=999999999)
        selectBox5, selectBox6 = st.columns([1,1])
        gT5 = selectBox5.selectbox(label="Select your Graph Type", options=graphs, key="sBox5")
        gT6 = selectBox6.selectbox(label="Select your Graph Type", options=graphs, key="sBox6")

with header:
    st.title(titleIn)

with viewer:
    st.subheader(bName1)
    cray = graphBlock("try3", "try4", "g3", "g4", client, stream_name, iD, stream, 7, 8, cName, gT1, gT2, "m1", minValDen, maxValDen)
    cray.graphInit()
    attList = []
    if st.session_state.count >= 1:
        st.subheader(bName2)
        initNum = 9
        endNum = 16
        attList = []
        for x in range (initNum, endNum):
            attList.append(x)
        boxNum2 = graphBlock(str(attList[0]), str(attList[1]), str(attList[2]), str(attList[3]), client, stream_name2, iD2, stream2, attList[4], attList[5], cName2, gT3, gT4, "m2", minValDen2, maxValDen2)
        boxNum2.graphInit()
        attList = []
    if st.session_state.count >= 2:
        st.subheader(bName3)
        initNum = 17
        endNum = 23
        attList = []
        for x in range (initNum, endNum):
            attList.append(x)
        boxNum3 = graphBlock(str(attList[0]), str(attList[1]), str(attList[2]), str(attList[3]), client, stream_name3, iD3, stream3, attList[4], attList[5], cName3, gT5, gT6, "m3", minValDen3, maxValDen3)
        boxNum3.graphInit()
        attList = []
# get parameter value from parameter name

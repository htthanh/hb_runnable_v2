from enum import Enum
import shutil

# excludedRoutes = ['route72-1.json', # timetable not available (in routeInfo/route72-1.json)
#                   'route70-5.json', # because this route has only 2 stops, 1 at HCMC boundary, 1 outside HCMC.
#                   'route61-4.json', # this route has only 2 stops, 1 outside of HCMC
#                   'route61-7.json' # this route has only 2 stops, 1 outside of HCMC
#                   ]

# htt-debug
htt_excludedRoutes = ['route72-1.json', # timetable not available (in routeInfo/route72-1.json)
                  'route70-5.json', # because this route has only 2 stops, 1 at HCMC boundary, 1 outside HCMC.
                  'route61-4.json', # this route has only 2 stops, 1 outside of HCMC
                  'route61-7.json' # this route has only 2 stops, 1 outside of HCMC
                  ]

# # htt-debug-begin
# # 'route1.json', 'route2.json', 'route3.json', 'route4.json', 'route5.json', 'route6.json', 'route7.json', 'route8.json', 'route9.json', 'route10.json', 'route11.json', 'route13.json', 'route14.json', 'route15.json', 'route16.json', 'route17.json', 'route18.json', 'route19.json', 'route20.json', 'route22.json', 'route23.json', 'route24.json', 'route25.json', 'route27.json', 'route28.json', 'route29.json', 'route30.json', 'route31.json', 'route32.json', 'route33.json', 'route34.json', 'route36.json', 'route38.json', 'route39.json', 'route41.json', 'route43.json', 'route44.json', 'route45.json', 'route46.json', 'route47.json', 'route48.json', 'route50.json', 'route52.json', 'route53.json', 'route55.json', 'route56.json', 'route57.json', 'route58.json', 'route59.json', 'route60-1.json', 'route60-2.json', 'route60-3.json', 'route60-4.json', 'route61-1.json', 'route61-3.json', 'route61-4.json', 'route61-6.json', 'route61-7.json', 'route61-8.json', 'route61.json', 'route62-1.json', 'route62-2.json', 'route62-3.json', 'route62-5.json', 'route62-6.json', 'route62-7.json', 'route62-8.json', 'route62-9.json', 'route62-10.json', 'route62-11.json', 'route62.json', 'route63.json', 'route64.json', 'route65.json', 'route68.json', 'route69.json', 'route70-1.json', 'route70-2.json', 'route70-3.json', 'route70-5.json', 'route70.json', 'route71.json', 'route72-1.json', 'route72.json', 'route73.json', 'route74.json', 'route75.json', 'route76.json', 'route77.json', 'route78.json', 'route79.json', 'route81.json', 'route84.json', 'route85.json', 'route86.json', 'route87.json', 'route88.json', 'route89.json', 'route90.json', 'route91.json', 'route93.json', 'route94.json', 'route99.json', 'route100.json', 'route101.json', 'route102.json', 'route103.json', 'route104.json', 'route107.json', 'route109.json', 'route110.json', 'route120.json', 'route122.json', 'route123.json', 'route124.json', 'route126.json', 'route127.json', 'route128.json', 'route139.json', 'route140.json', 'route141.json', 'route144.json', 'route145.json', 'route146.json', 'route148.json', 'route150.json', 'route151.json', 'route152.json', 'routeD1.json', 'routeD2.json', 'routeD3.json'
# excludedRoutes = ['route9.json', 'route10.json', 'route11.json', 'route13.json', 'route14.json', 'route15.json', 'route16.json', 'route17.json', 'route18.json', 'route19.json', 'route20.json', 'route22.json', 'route23.json', 'route24.json', 'route25.json', 'route27.json', 'route28.json', 'route29.json', 'route30.json', 'route31.json', 'route32.json', 'route33.json', 'route34.json', 'route36.json', 'route38.json', 'route39.json', 'route41.json', 'route43.json', 'route44.json', 'route45.json', 'route46.json', 'route47.json', 'route48.json', 'route50.json', 'route52.json', 'route53.json', 'route55.json', 'route56.json', 'route57.json', 'route58.json', 'route59.json', 'route60-1.json', 'route60-2.json', 'route60-3.json', 'route60-4.json', 'route61-1.json', 'route61-3.json', 'route61-4.json', 'route61-6.json', 'route61-7.json', 'route61-8.json', 'route61.json', 'route62-1.json', 'route62-2.json', 'route62-3.json', 'route62-5.json', 'route62-6.json', 'route62-7.json', 'route62-8.json', 'route62-9.json', 'route62-10.json', 'route62-11.json', 'route62.json', 'route63.json', 'route64.json', 'route65.json', 'route68.json', 'route69.json', 'route70-1.json', 'route70-2.json', 'route70-3.json', 'route70-5.json', 'route70.json', 'route71.json', 'route72-1.json', 'route72.json', 'route73.json', 'route74.json', 'route75.json', 'route76.json', 'route77.json', 'route78.json', 'route79.json', 'route81.json', 'route84.json', 'route85.json', 'route86.json', 'route87.json', 'route88.json', 'route89.json', 'route90.json', 'route91.json', 'route93.json', 'route94.json', 'route99.json', 'route100.json', 'route101.json', 'route102.json', 'route103.json', 'route104.json', 'route107.json', 'route109.json', 'route110.json', 'route120.json', 'route122.json', 'route123.json', 'route124.json', 'route126.json', 'route127.json', 'route128.json', 'route139.json', 'route140.json', 'route141.json', 'route144.json', 'route145.json', 'route146.json', 'route148.json', 'route150.json', 'route151.json', 'route152.json', 'routeD1.json', 'routeD2.json', 'routeD3.json']

htt_allRoutes = ['route1.json', 'route2.json', 'route3.json', 'route4.json', 'route5.json', 'route6.json', 'route7.json', 'route8.json', 'route9.json', 'route10.json', 'route11.json', 'route13.json', 'route14.json', 'route15.json', 'route16.json', 'route17.json', 'route18.json', 'route19.json', 'route20.json', 'route22.json', 'route23.json', 'route24.json', 'route25.json', 'route27.json', 'route28.json', 'route29.json', 'route30.json', 'route31.json', 'route32.json', 'route33.json', 'route34.json', 'route36.json', 'route38.json', 'route39.json', 'route41.json', 'route43.json', 'route44.json', 'route45.json', 'route46.json', 'route47.json', 'route48.json', 'route50.json', 'route52.json', 'route53.json', 'route55.json', 'route56.json', 'route57.json', 'route58.json', 'route59.json', 'route60-1.json', 'route60-2.json', 'route60-3.json', 'route60-4.json', 'route61-1.json', 'route61-3.json', 'route61-4.json', 'route61-6.json', 'route61-7.json', 'route61-8.json', 'route61.json', 'route62-1.json', 'route62-2.json', 'route62-3.json', 'route62-5.json', 'route62-6.json', 'route62-7.json', 'route62-8.json', 'route62-9.json', 'route62-10.json', 'route62-11.json', 'route62.json', 'route63.json', 'route64.json', 'route65.json', 'route68.json', 'route69.json', 'route70-1.json', 'route70-2.json', 'route70-3.json', 'route70-5.json', 'route70.json', 'route71.json', 'route72-1.json', 'route72.json', 'route73.json', 'route74.json', 'route75.json', 'route76.json', 'route77.json', 'route78.json', 'route79.json', 'route81.json', 'route84.json', 'route85.json', 'route86.json', 'route87.json', 'route88.json', 'route89.json', 'route90.json', 'route91.json', 'route93.json', 'route94.json', 'route99.json', 'route100.json', 'route101.json', 'route102.json', 'route103.json', 'route104.json', 'route107.json', 'route109.json', 'route110.json', 'route120.json', 'route122.json', 'route123.json', 'route124.json', 'route126.json', 'route127.json', 'route128.json', 'route139.json', 'route140.json', 'route141.json', 'route144.json', 'route145.json', 'route146.json', 'route148.json', 'route150.json', 'route151.json', 'route152.json', 'routeD1.json', 'routeD2.json', 'routeD3.json']

# # htt-debug-end

stopsOutsideHCMC = [7509, 7261, 7217, 7218, 7281, 7210, 7209, 7214, 7591, 7257, 7216, 7208, 7215, 7213, 7280, 7211, 7136, 7220, 7263, 7219, 7212, 7595]

maxWalkDist = 300 # metres
walkSpeed = 1.3 # metres/second - average comfortable walk speed for people of all ages
maxWalkTime = maxWalkDist/walkSpeed # in seconds
maxWaitTime = 60*60 # seconds - max wait time at a bus stop for transfering, assumingly 30 minutes.
dfaultDwellTime = 6 # seconds - the default period from when a bus arrives at a bus stop to when it leaves the stop.


# dataFolder = '../data'
# trashSite = './trashSite'
# outputsFolder = './outputs'
# nodeDegDistribFolder = '%s/nodeDegDistrib' % outputsFolder
# pathLenDistribFolder = '%s/pathLenDistrib' % outputsFolder
# nodeCentralsFolder = '%s/nodeCentrals' % outputsFolder
# picklesFolder = '%s/pickles' % outputsFolder
# mapPlots = '%s/mapPlots' % outputsFolder
# ttgAnalysisFolder = '%s/ttgAnalysis' % outputsFolder

# nodeDegPkl = '%s/nodeDeg.pkl' % picklesFolder
# shortestPathPkl = '%s/shortestHops.pkl' % picklesFolder
# shortestTimePkl = '%s/shortestTime.pkl' % picklesFolder
# shortestDistPkl = '%s/shortestDist.pkl' % picklesFolder

# htt-debug-begin
import os
# PROJECT_ROOT = '/home/htthanh/Downloads/server/busnet-master-original' # local-ubuntu
# PROJECT_ROOT = '/media/htthanh/to-server-20250723/busnet-master-original' # slurm-ubuntu
# PROJECT_ROOT = '/home/htthanh/htthanhdata/src/busnet-master-original' # vmware-ubuntu
# htt-isolation (2026-11-27): PROJECT_ROOT = thu muc cha cua myPy/ chua chinh file nay, de moi ban code
# (hb_busnet_runnable, hb_busnet_runnable_v2) chi doc/ghi trong folder cua chinh no. Tren server, ban golden
# dat tai .../busnet-master-original/myPy/ nen gia tri van giong dong hardcode o tren.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataFolder = os.path.join(PROJECT_ROOT, 'data')
stopSeqFolder = os.path.join(PROJECT_ROOT, 'data/stopSeq')
routeInfoFolder = os.path.join(PROJECT_ROOT, 'data/routeInfo')
trashSite = os.path.join(PROJECT_ROOT, 'myPy/trashSite')
outputsFolder = os.path.join(PROJECT_ROOT, 'myPy/outputs')

nodeDegDistribFolder = '%s/nodeDegDistrib' % outputsFolder
pathLenDistribFolder = '%s/pathLenDistrib' % outputsFolder
nodeCentralsFolder = '%s/nodeCentrals' % outputsFolder
picklesFolder = '%s/pickles' % outputsFolder
mapPlots = '%s/mapPlots' % outputsFolder
ttgAnalysisFolder = '%s/ttgAnalysis' % outputsFolder

nodeDegPkl = '%s/nodeDeg.pkl' % picklesFolder
shortestPathPkl = '%s/shortestHops.pkl' % picklesFolder
shortestTimePkl = '%s/shortestTime.pkl' % picklesFolder
shortestDistPkl = '%s/shortestDist.pkl' % picklesFolder

# # force remove trashSite and outputsFolder
# if os.path.exists(trashSite):
#     shutil.rmtree(trashSite)
# if os.path.exists(outputsFolder):
#     shutil.rmtree(outputsFolder)

os.makedirs(picklesFolder, exist_ok=True)
os.makedirs(nodeCentralsFolder, exist_ok=True)
os.makedirs(mapPlots, exist_ok=True)
os.makedirs(nodeDegDistribFolder, exist_ok=True)
os.makedirs(pathLenDistribFolder, exist_ok=True)
os.makedirs(ttgAnalysisFolder, exist_ok=True)
os.makedirs(trashSite, exist_ok=True)

NPROCESSES=25
# htt-P1: bien the shortest path cua buoc 5: 'v3' = P0 (goc, calcShortestPathsSubset_v3),
#         'v3p' = P1 (bo quet pandas toan bang), 'v4' = P2 (P1 + dao vong 2/3 + gop loi goi igraph). Output cua bien the khac 'v3' ghi vao trashSite/gttShortestPaths_<variant>/
SP_VARIANT = 'v3'
# htt-debug-end

class RouteInfoCols(Enum):
    routeId = 0
    routeNo = 1
    routeName = 2
    timeTableIn = 3
    timeTableOut = 4

# ======================================================================================================================
class BusMapRouteCols(Enum):
    # Not all columns in the Busmap json file need to be listed here. List only those we need.
    # However exact column names in the json file should be used.
    StationId = 0
    StationOrder = 1
    StationDirection = 2
    RouteId = 3
    StationName = 6
    pathPoints = 7
    Address = 8
    Lat = 9
    Lng = 10

# ======================================================================================================================
class GNodeAttribs(Enum):
    routes = 0
    StationId = 1
    StationDesc = 2
    Lat = 4
    Lng = 5

    neighbourNodes = 'neighbour nodes'

    nLines = 'Number of lines'
    nServices = 'Number of services'
    inDeg = 8
    outDeg = 9
    totDeg = 'Node degree (total)'

    ccHops = 'Closeness centrality (by number of stops)'
    ccTime = 'Closeness centrality (by mean travel time)'
    ccDist = 'Closeness centrality (by travel distance)'
    cbHops = 'Betweenness centrality (by number of stops)'
    cbTime = 'Betweenness centrality (by mean travel time)'
    cbDist = 'Betweenness centrality (by travel distance)'

    frV_u30 = 'Destination proximity density (under 30 minutes)' # as origin
    frV_u60 = 'Destination proximity density (under 60 minutes)' # as origin
    frV_u90 = 'Destination proximity density (under 90 minutes)' # as origin
    frV_o90 = 'Destination proximity density (over 90 minutes)' # as origin
    frV_3060 = 'Destination proximity density (30-60 minutes)' # as origin
    frV_6090 = 'Destination proximity density (60-90 minutes)' # as origin

    toV_u30 = 'Origin proximity density (under 30 minutes)' # as destination
    toV_u60 = 'Origin proximity density (under 60 minutes)' # as destination
    toV_u90 = 'Origin proximity density (under 90 minutes)' # as destination
    toV_o90 = 'Origin proximity density (over 90 minutes)' # as destination
    toV_3060 = 'Origin proximity density (30-60 minutes)' # as destination
    toV_6090 = 'Origin proximity density (60-90 minutes)' # as destination

    ndfrV_u30 = 'Nodes from this station under 30 minutes'
    ndfrV_u60 = 'Nodes from this station under 60 minutes'
    ndfrV_u90 = 'Nodes from this station under 90 minutes'
    ndfrV_o90 = 'Nodes from this station over 90 minutes'
    ndfrV_3060 = 'Nodes from this station 30-60 minutes'
    ndfrV_6090 = 'Nodes from this station 60-90 minutes'

    ndtoV_u30 = 'Nodes to this station under 30 minutes'
    ndtoV_u60 = 'Nodes to this station under 60 minutes'
    ndtoV_u90 = 'Nodes to this station under 90 minutes'
    ndtoV_o90 = 'Nodes to this station over 90 minutes'
    ndtoV_3060 = 'Nodes to this station 30-60 minutes'
    ndtoV_6090 = 'Nodes to this station 60-90 minutes'

class GNodeRouteCols(Enum):
    RouteId = 0
    StationDirection = 1
    StationOrder = 2

# ======================================================================================================================
class GEdgeAttribs(Enum):
    routes = 0
    nLines = 1
    meanRoadDist = 2
    meanTravTime = 3
    nServices = 4

class GEdgeRouteCols(Enum):
    RouteId = 0
    StationDirection = 1
    edgeOrder = 2
    pathPoints = 3
    roadDist = 4
    tTrav = 5


# ======================================================================================================================
class RoutesCols(Enum):
    RouteId = 0
    StationDirection = 1
    RouteNo = 2
    RouteName = 3
    tripTime = 4
    tripDist = 5
    designedTtb = 6
    actualTtb = 7

class RoutesTtbCols(Enum):
    StationOrder = 0
    StationCode = 1
    timetable = 2


# ======================================================================================================================
class GttEdgeAttribs(Enum):
    type = 'type'
    typeBus = 'bus'
    typeWalk = 'walk'
    typeWait = 'wait'
    dirRouteID = 'directed route ID' #e.g 134_0 for routeID 134, direction 0
    time = 'time'
    transfer = 'transfer'

class GttNodeAttribs(Enum):
    ndDesc = 'ndDesc'

class dfNdDetailsCols(Enum):
    RouteId = 'RouteId'
    StationDirection = 'StationDirection'
    StationId = 'StationId'
    time = 'time'
    dirRoute = 'dirRoute'
    arrOrDep = 'arrOrDep'
    arr = 'arr'
    dep = 'dep'
    gttNdID = 'gttNdID'

class dfAllTransfersCols(Enum):
    stopFr = 'stopFr'
    stopTo = 'stopTo'
    nodeFr = 'nodeFr'
    nodeTo = 'nodeTo'
    timeFr = 'timeFr'
    timeTo = 'timeTo'
    type = 'type'
import pickle
import os
import time
import sys
from datetime import datetime
import multiprocessing

import graph_v2
import constants as const
import topoAnalysis as topo
import topoPostproc
import utilities as utils
import ttGraph_v2
import ttgAnalysisMultip_v2
import ttgPostprocMultip

# import faulthandler
# faulthandler.enable()
# faulthandler.dump_traceback_later(30, repeat=True, file=sys.stderr)

import logging

# ======================================================================================================================
if __name__=='__main__':
    logging.basicConfig(
        filename="my_script.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.info("Program started")
    try:
        # print("Starting main.py")
        # htt_route_part = -1
        # num_routes_per_run = 4
        # if len(sys.argv) > 1:
        #     htt_route_part = int(sys.argv[1])
        # print(f"htt_route_part: {htt_route_part}")
        # if htt_route_part == -1:
        #     const.excludedRoutes = const.htt_excludedRoutes
        # else:
        #     htt_routes = const.htt_allRoutes[htt_route_part*num_routes_per_run:min((htt_route_part+1)*num_routes_per_run, len(const.htt_allRoutes))]
        #     const.excludedRoutes = [item for item in const.htt_allRoutes if item not in htt_routes]
        #     for item in const.htt_excludedRoutes:
        #         if item not in const.excludedRoutes:
        #             const.excludedRoutes.append(item)
        # print(f"const.excludedRoutes: {const.excludedRoutes}")
        # htt_run_routes = set(const.htt_allRoutes) - set(const.excludedRoutes)
        # print(f"routes to process: {htt_run_routes}")
        # if len(htt_run_routes) == 0:
        #     print("No routes to process")
        #     exit()

        # start_time1 = time.time() # htt-debug
        # print(f"start_time1: {utils.printCurrentTime()} cpu_count() {multiprocessing.cpu_count()}")
        # # '''
        # # CONSTRUCTS GRAPH IN L-SPACE AND DFROUTES =========================================================================
        # pFile_G = '%s/G.pkl' % const.picklesFolder
        # pFile_dfRoutes = '%s/dfRoutes.pkl' % const.picklesFolder
        # if os.path.isfile(pFile_G) and os.path.isfile(pFile_dfRoutes):
        #     G = pickle.load(open(pFile_G, 'rb'))
        #     dfRoutes = pickle.load(open(pFile_dfRoutes, 'rb'))
        #     print('unpickling G and dfRoutes completed')
        # else:
        #     G, dfRoutes = graph_v2.construct_G_dfRoutes()
        #     print('constructing G and dfRoutes completed')
        #     with open(pFile_G, 'wb') as f:
        #         pickle.dump(G, f)
        #     with open(pFile_dfRoutes, 'wb') as f:
        #         pickle.dump(dfRoutes, f)
        # #printStuff(G,dfRoutes)
        # # htt-debug => part of run (1)
        # # '''
        # end_time1 = time.time() # htt-debug
        # print(f"Time taken1: {end_time1 - start_time1} seconds; {utils.printCurrentTime()}; cpu_count() {multiprocessing.cpu_count()} => CONSTRUCTS GRAPH IN L-SPACE AND DFROUTES") # htt-debug

        # '''
        # stopPairsSameRoute = ttgAnalysisMultip.getStopPairsSameRoute(dfRoutes)
        # with open('%s/stopPairsSameRoute.pkl' % const.picklesFolder, 'wb') as f:
        #     pickle.dump(stopPairsSameRoute, f)
        # # htt-debug => stopPairsSameRoute.pkl is not used later => no need to run
        # '''

        # start_time2 = time.time() # htt-debug
        # print(f"start_time2: {utils.printCurrentTime()} cpu_count() {multiprocessing.cpu_count()}")
        # # '''
        # # TOPOLOGICAL ANALYSIS =============================================================================================
        # topo.topoMain(G, dfRoutes)
        # # assigns betweenness centralities (by time, by distance, by number of hops) to G
        # G = pickle.load(open('%s/G_proxDens.pkl' % const.picklesFolder, 'rb'))
        # topo.assignBetwCentralityToG(G)
        # with open('%s/G_wNdAttribs.pkl' % const.picklesFolder, 'wb') as f:
        #     pickle.dump(G, f)
        # # '''
        # end_time2 = time.time() # htt-debug
        # print(f"Time taken2: {end_time2 - start_time2} seconds; {utils.printCurrentTime()}; cpu_count() {multiprocessing.cpu_count()} => TOPOLOGICAL ANALYSIS") # htt-debug

        # start_time3 = time.time() # htt-debug
        # print(f"start_time3: {utils.printCurrentTime()} cpu_count() {multiprocessing.cpu_count()}")
        # # '''
        # # TOPO ANLYSIS POSTPROCESSING
        # G_wNdAttribs = pickle.load(open('%s/G_wNdAttribs.pkl' % const.picklesFolder, 'rb'))
        # dfRoutes = pickle.load(open('%s/dfRoutes.pkl' % const.picklesFolder, 'rb'))
        # stopPairDist = pickle.load(open('%s/stopPairsDist.pkl' % const.picklesFolder, 'rb'))
        # topoPostproc.main_topoPostproc(G_wNdAttribs, dfRoutes, stopPairDist)
        # # '''
        # end_time3 = time.time() # htt-debug
        # print(f"Time taken3: {end_time3 - start_time3} seconds; {utils.printCurrentTime()}; cpu_count() {multiprocessing.cpu_count()} => TOPO ANLYSIS POSTPROCESSING") # htt-debug

        # # '''
        # # # TEMPORAL TOPOLOGICAL ANALYSIS ====================================================================================
        # # #dirRouteID = '10_1'
        # # #timeWindow = [5*3600, 22*3600]
        # # #fileName = '%s/%s_allDay.png' % (const.trashSite, dirRouteID)
        # # #ttgVisual_v2.plotTransitLinks_v2(gttTransit, dirRouteID, timeWindow, fileName)

        # # #dfRoutes = pickle.load(open('%s/dfRoutes.pkl' % const.picklesFolder, 'rb'))
        # # #ttgVisual_v2.plotRoutesAllday(dfRoutes)

        # # #ttgPostprocMultip.calcBetwCentral(allStops=None, dfAllShortestPaths=None)
        # # # htt-debug => gttTransit not found => no need to run
        # # '''
        
        # start_time4 = time.time() # htt-debug
        # print(f"start_time4: {utils.printCurrentTime()} cpu_count() {multiprocessing.cpu_count()}")
        # # htt-debug-begin
        # G = pickle.load(open('%s/G_proxDens.pkl' % const.picklesFolder, 'rb'))
        # dfRoutes = pickle.load(open('%s/dfRoutes.pkl' % const.picklesFolder, 'rb'))
        # stopPairsDist = pickle.load(open('%s/stopPairsDist.pkl' % const.picklesFolder, 'rb'))
        # nProcesses=const.NPROCESSES
        # gttTransit, dfNdDetails, ndIDict, ndIDictInv, dfAllTransfers = ttGraph_v2.makeTopoTempGraphMultip(G, dfRoutes, stopPairsDist, nProcesses)
        # # htt-debug-end
        # end_time4 = time.time() # htt-debug
        # print(f"Time taken4: {end_time4 - start_time4} seconds; {utils.printCurrentTime()}; cpu_count() {multiprocessing.cpu_count()} => TEMPORAL TOPOLOGICAL ANALYSIS") # htt-debug

        start_time5 = time.time() # htt-debug
        print(f"start_time5: {utils.printCurrentTime()} cpu_count() {multiprocessing.cpu_count()}")
        # htt-debug-begin
        ttgAnalysisMultip_v2.main_ttgAnalysisMultip_v2()
        # htt-debug-end
        end_time5 = time.time() # htt-debug
        print(f"Time taken5: {end_time5 - start_time5} seconds; {utils.printCurrentTime()}; cpu_count() {multiprocessing.cpu_count()} => TEMPORAL SHORTEST PATH ANALYSIS") # htt-debug

        # start_time6 = time.time() # htt-debug
        # print(f"start_time6: {utils.printCurrentTime()} cpu_count() {multiprocessing.cpu_count()}")
        # ttgPostprocMultip.main_ttgPostprocMultip()
        # #ttgPostprocMultip.main_draft()
        # end_time6 = time.time() # htt-debug
        # print(f"Time taken6: {end_time6 - start_time6} seconds; {utils.printCurrentTime()}; cpu_count() {multiprocessing.cpu_count()} => TEMPORAL SHORTEST PATH POSTPROCESSING") # htt-debug
    except Exception as e:
        logging.exception("Unexpected error: %s => %s", (e, utils.printCurrentTime()))


    
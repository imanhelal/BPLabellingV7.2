'''
This code is copyrighted to Dina Bayomie and Iman Helal @2015 Research work
Information System Department, Faculty of computers and Information System
Cairo University, Egypt
'''

import sys
import math
from tree import Tree
from branch import Branch
from traceLog import TraceLog

from algorithm import Algorithm
import os
import shutil
import csv 
# to calculate the processing time of the algorithm
import time 
#start run time of program
start_time_program = time.time()


from py4j.java_gateway import JavaGateway 

gateway = JavaGateway()
startActivity= gateway.entry_point.getStartActivityName()
print 'startActivity', startActivity

dic=gateway.entry_point.getMatrixRelations()
M=dict()
for k in dic :
    M[k]=dict()
    for n in dic[k]:
        M[k][n]=dic[k][n]

dicArr=gateway.entry_point.getAllParents()
Parents=dict()
for k in dicArr :
    Parents[k]=[]
    for n in dicArr[k]:
        Parents[k].append(n)
      

gateway.shutdown()

S=[]
T=dict()
GivenConfidenceLevel=0#.3

''' removing folders '''
txtDirectory="labeledEventLog_txt/"
csvDirectory="labeledEventLog_csv/"
xesDirectory="labeledEventLog_xes/"
otherDirectory="otherEventLog_all/"
if os.path.exists(txtDirectory):
    shutil.rmtree(txtDirectory)
if os.path.exists(csvDirectory):
    shutil.rmtree(csvDirectory)
if os.path.exists(xesDirectory):
    shutil.rmtree(xesDirectory)
if os.path.exists(otherDirectory):
    shutil.rmtree(otherDirectory)

print "processing input ....."
print "reading unlabeled event log"
'''reading and preparing event log input 1'''
filename=sys.argv[1]
splitarr=filename.split('.')
extension=splitarr[len(splitarr)-1]
print extension
print filename
timestamps=[]
if (extension =='txt'):
    fin = open(sys.argv[1], 'r')
    for line in fin:
        tupleLog= line.strip()
        if len(tupleLog) > 0:
            record=tupleLog.split(';')
            S.append(record)    
            
    fin.close()
    print (S)

elif(extension == 'csv'):
    fin  = open(sys.argv[1], "r")
    reader = csv.DictReader(fin)
    fields= reader.fieldnames 
    print fields   
    for row in reader:
        event=[]
        for i in range(0, len(fields)):
            event.append(row[reader.fieldnames[i]])
        S.append(event) 
        
    fin.close()
    print (S)


# reading and preparing T input 2
print "reading Activity execution times metadata"
T=dict()
fin  = open(sys.argv[2], "r")
reader = csv.DictReader(fin)
rownum = 0
fields= reader.fieldnames
print fields
for row in reader:

        heuristic=[]
        for i in range(1, len(reader.fieldnames)):
            heuristic.append(float(row[reader.fieldnames[i]]))
        T[row[reader.fieldnames[0]]]=heuristic   

fin.close()
print 'T' ,T


start_time_algorithm = time.clock()
print "start apply labeling algorithm"
alg=Algorithm(S,T,M,Parents,startActivity,GivenConfidenceLevel)       
alg.apply_algorithm()
end_time_algorithm=time.clock()
print "event logs"
i =1
for eLog in alg.constructedTraces:
    eLog.write_traceLog_into_file_csv(i)
    eLog.write_traceLog_into_file_txt(i)
    eLog.write_traceLog_into_XML(i)
    eLog.prepare_traceLog(i)
    i+=1
#print other traces that have produces but not completely fit
if (len(alg.otherConstructedTraces)>0):
    print "other event logs "
    for oeLog in alg.otherConstructedTraces:
        oeLog.write_traceLog_into_file_csv(i,otherDirectory)
        oeLog.write_traceLog_into_file_txt(i,otherDirectory)
        oeLog.write_traceLog_into_XML(i,otherDirectory)
        oeLog.prepare_traceLog(i)
        i+=1

print"program execution time : %s seconds " % (time.time() - start_time_program)
print"Algorithm execution time :  %s seconds " % (end_time_algorithm - start_time_algorithm)

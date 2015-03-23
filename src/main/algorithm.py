'''
This code is copyrighted to Dina Bayomie and Iman Helal @2015 Research work
Information System Department, Faculty of computers and Information System
Cairo University, Egypt

@author:  Dina Bayomie, Iman Helal
'''
from tree import Tree
from branch import Branch
from traceLog import TraceLog
from branchTree import BranchTree
import math
#import itertools
# to access the bp object
#from py4j.java_gateway import JavaGateway


class Algorithm:
    '''
    classdocs
    '''
    S = []  # Extracted unlabeled Sequence from File directly [timestamp , activity]
    T = dict()
    M = dict()
    Parents = dict()
    GivenConfidenceLevel = 0
    
    activitiesProb = dict()  # check to small letter
    
    traces = Tree()
    BranchConfidenceLevel = dict()  # key leaf node : value calculated confidence level p(leaf| branch)
    Branches = []
    constructedTraces = []#right traces
    otherConstructedTraces=[]#that may missing some events or cases 
    root = None  # root of traces\cases tree [tree]
    branchRoot = None  # root of traceLogs tree [branchTree]
    
    startActivity = ''
    totalBranchesConfidenceLevel = 0.0  # 1.0
    numOfCases = 0
    CasesBranches = dict()
    traceLogsTree = BranchTree()

    def __init__(self, S, T, M, Parents, startActivity, GivenConfidenceLevel):
        self.M = M
        self.Parents = Parents
        self.T = T
        self.S = S
        self.startActivity = startActivity
        self.traces.add_node(1, 1, 0, 'start', 0, None)
        self.root = self.traces.get_root()
        self.calculate_activity_probability(self.S)
        self.GivenConfidenceLevel = GivenConfidenceLevel
   
    def trunc(self, number, digit=4):
        return (math.floor(number * pow(10, digit) + 0.5)) / pow(10, digit)
    
    '''Calculate probability of each activity withing giving sequence'''
    def calculate_activity_probability(self, sequence):
        sequnceLength = len(sequence)
        appearances = dict()
        for curr in sequence:
            if(not appearances.has_key(curr[1])):
                appearances[curr[1]] = 1.0
            else:
                appearances[curr[1]] = appearances[curr[1]] + 1.0
        for a in appearances:
            value = self.trunc(appearances[a] / sequnceLength, 4)
            self.activitiesProb[a] = value
    
    def distinct_possible_cases(self, possibleNodes):
        distinctNodes = []
        for n in possibleNodes:
            if(n not in distinctNodes):
                distinctNodes.append(n)
        return distinctNodes 
         
    '''Explore all possible cases for each symbol'''    
    
    def check_possible_branches_based_on_Model (self, symbol):
        possibleNodes = dict()
        event = symbol[1]  
        
        if(event == self.startActivity):     
            possibleNodes[self.root]=None
            
        else: 
            for l in self.traces.get_leafs(self.root):
                node = l
                while (node != self.root):
                    activity = node.activity
                    relation = self.M.get(activity).get(event)
                    
                    if(relation.lower() == "seq"):
                        
                        arrParents = self.Parents[event]
                        
                        flag = 0
                        for j in range(0, len(arrParents)):
                            if(len(arrParents) == 1):
                                possibleNodes[node]=None
                                break;
                            
                            if(flag == 1):
                                break;
                            for i in range(1, len(arrParents)):
                                if i == j :
                                    continue
                                rel = self.M.get(arrParents[j]).get(arrParents[i])
                                if(rel == 'and'):
                                    f1 = self.traces.check_existance_in_branch(node, arrParents[j])
                                    f2 = self.traces.check_existance_in_branch(node, arrParents[i])
                                    if(f1 and f2):
                                        possibleNodes[node]=None
                                        flag = 1
                                        break;
                            
                                elif(rel == 'xor'):
                                    possibleNodes[node]=None
                        break
                    elif(relation.lower() == "xor"):                        
                        node = node.parent
                        continue
                    elif(relation.lower() == "and"):
                        isExist = self.traces.check_existance_in_branch(node, event)
                        if(not isExist):
                            modelSeqNode=None
                            arrParents = self.Parents[event]
                            for p in arrParents:
                                modelSeqNode=self.traces.get_existed_activity_in_branch(node, p)
                            
                            possibleNodes[node]=modelSeqNode
                        node = node.parent
                        continue
                    elif(relation.lower() == "none"):
                        node = node.parent
                        continue;
               
        return possibleNodes            

    '''Heuristic calculation method [min, avg , max]'''
    def check_possible_branches_based_on_heuristics(self, symbol, possibleNodes):
        symbolTimestamp = symbol[0]
        avgArr = []
        minArr = []
        maxArr = []
        metadataTime = self.T.get(symbol[1])
        for n in possibleNodes:
            node=n
            if(possibleNodes[n]!=None):
                node=possibleNodes[n]
                
            if(n == self.root):
                avgArr.append(n)
                continue            
            diff = int(symbolTimestamp) - int(node.timestamp)
            if(diff == metadataTime[1]):
                avgArr.append(n)
            elif diff >= metadataTime[0] and diff < metadataTime[1]:
                minArr.append(n)
            elif diff > metadataTime[1] and diff <= metadataTime[2]:
                maxArr.append(n)     
        calcPool = {'avg':avgArr, 'min':minArr, 'max':maxArr}
        return calcPool
    
    '''need to change how it handel if all  in average '''
    
    '''calculate given probability of  node per branch'''
    def calculate_precentage(self, calcPool, highestPriority='avg'):
        calcPrecentage = dict()
        noOfCases = len(sum(calcPool.values(), []))
        otherHeuristic = list(set(sum(calcPool.values(), [])) - set(calcPool[highestPriority]))
        noOfHighestPriority = len(calcPool[highestPriority])
        noOfOtherHeuristic = len(otherHeuristic)
        total = 0
        totalNumber = noOfCases * noOfCases
        if(noOfCases == 1):
            totalNumber = 2.0
        totalNumber *= 1.0
        if(noOfOtherHeuristic >0):
            for a in calcPool[highestPriority]:
                calcPrecentage[a] = ((noOfCases + 1.0) / totalNumber)
                total += calcPrecentage[a]
            for m in otherHeuristic:
                calcPrecentage[m] = ((noOfCases - (noOfHighestPriority * 1.0 / noOfOtherHeuristic * 1.0)) / totalNumber) * 1.0
                total += calcPrecentage[m]
        else:
            for a in calcPool[highestPriority]:
                calcPrecentage[a] = ((noOfCases) / totalNumber)
                total += calcPrecentage[a]                    
            
        return calcPrecentage   
    
    '''Return all possible nodes based on model and heuristic calculation'''
    def filter_possible_cases(self, symbol):
        
        possibleCasesFromM = self.check_possible_branches_based_on_Model(symbol)
        calcPool = self.check_possible_branches_based_on_heuristics(symbol, possibleCasesFromM)
        possibleNodes = self.calculate_precentage(calcPool, 'avg')
        
        return possibleNodes   

     
    '''building tree for given unlabeled event log and distribute the event to cases tree '''
    def build_branches_tree(self):
               
        labelCaseId = 1;
        for symbol in self.S:
            dictionary = self.filter_possible_cases(symbol)
            numPossibleBranches = len(dictionary)
            for n in dictionary :
                caseId = n.caseId
                if(caseId == 0):
                    caseId = labelCaseId
                    labelCaseId = labelCaseId + 1;        
                percentage = dictionary[n]  
                self.traces.add_node(percentage, 1.0 / numPossibleBranches, symbol[0], symbol[1], caseId, n)


    
    '''Calculate confidence level for each branch in cases traces tree and also build the branches trace log tree'''
    def calculate_confidence_level_branch(self):
        self.CasesBranches = dict()
        
        self.traceLogsTree.add_branch(0, 0, [], 1.0)
        self.branchRoot = self.traceLogsTree.get_root(0)
        branchId=1
        for leaf in self.traces.get_leafs(self.root):
            nodes = []
            prob = leaf.percentage
            result = 1
            if(leaf.parent != self.root):
                result = self.traces.get_branch_confidenceLevel(leaf.parent)
                nodes = self.traces.get_branch_nodes(leaf, nodes)
            else:
                nodes.append(leaf)
            confLevel = prob * result
            nodes.reverse()
            
            branch = Branch(branchId, leaf.caseId, nodes, confLevel) 
            isToAddToRoot = True  
            possibleBranches=[]
            caseBranches=self.traceLogsTree.get_branches_of_case(self.branchRoot,branch.caseId-1)
            #if(len(caseBranches) == 0):
                #print "case has no branches",branch.caseId-1
                
                #print "unable to create the event logs insufficent activities"
                
                #return
            print "no of branches in case :",branch.caseId-1," ",len(caseBranches) 
            for branchLeaf in caseBranches:
                currentBranch = branchLeaf
                branches = []
                branches = self.traceLogsTree.get_trace_branches(currentBranch, branches)
                isConflict = self.conflictBranch(branch, branches)
                if(not isConflict):
                        isToAddToRoot = False
                        possibleBranches.append(currentBranch)
            possibleBranches = self.distinct_possible_cases(possibleBranches)
            for b in possibleBranches:
                self.traceLogsTree.add_branch_object(branch, b)
            
            if(isToAddToRoot and branch.caseId == 1):
                self.traceLogsTree.add_branch_object(branch, self.branchRoot)
            branchId += 1
            
   
    '''@return True if branch is from the same case of any of the branches or has common timestamp event , False otherwise '''        
    def conflictBranch(self, branch, branches):  
        isConflict = self.CheckBranchesPerCase(branch, branches)
        if(not isConflict):
            isConflict = self.CheckViolatingBranches(branch, branches)
        return isConflict    
           
          
            
    def CheckBranchesPerCase(self, selectedBranch, remainingBranches):
        isSameCaseId = False
        for x in remainingBranches:
            if(x.caseId == selectedBranch.caseId): 
                return True   
        return isSameCaseId 
    
    def CheckViolatingBranches(self, selectedBranch, remainingBranches):
        isSameTimestamp = False
        for x in remainingBranches:
            intersect = list(set(x.timestampList).intersection(set(selectedBranch.timestampList)))
            if len(intersect) != 0:
                return True
        return isSameTimestamp          

    def build_traceLog(self):
        traceLogId=1
        for branchLeaf in self.traceLogsTree.get_leafs(self.branchRoot):
            branches = []
            branches = self.traceLogsTree.get_trace_branches(branchLeaf, branches)
            traceLogObject=TraceLog(traceLogId,branches,self.activitiesProb,self.root)
            if(len(branches)==self.numOfCases and len(traceLogObject.events)==len(self.S) and traceLogObject.confidenceLevel >= self.GivenConfidenceLevel):
                print "the same no of cases" 
                '''if():
                    print "same no of events"
                    if():
                        print "accepted cl"
                        '''
                self.constructedTraces.append(traceLogObject)
            else:
                self.otherConstructedTraces.append(traceLogObject)
            traceLogId+=1

    def apply_algorithm(self):
        print "build cases tree"
        self.build_branches_tree()
        self.numOfCases = len(self.root.children)
        print "number of cases in given event log : ",self.numOfCases
        self.traces.display(self.root)
        print "prepare labeled event logs "
        print "construct branches tree from cases tree"
        self.calculate_confidence_level_branch()
        #self.traceLogsTree.display(self.branchRoot)
        print "compose event logs from branches tree"
        self.build_traceLog()
        self.constructedTraces=sorted(self.constructedTraces, key=lambda TraceLog: TraceLog.confidenceLevel, reverse=True) 
        print "number of labeled event logs :" , self.constructedTraces

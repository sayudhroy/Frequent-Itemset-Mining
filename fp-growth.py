"""
FP-Growth Algorithm
"""

# Importing the Libraries
import pandas as pd
import operator
import numpy as np
from itertools import combinations
import time

# Defining the Tree Class
class Tree:
    def __init__(self, value, weight):
        self.value = value
        self.weight = weight
        self.children = []
        
    def __repr__(self, level=0):
        ret = "\t"*level+repr(self.value)+repr(self.weight)+"\n"
        for child in self.children:
            ret += child.__repr__(level+1)
        return ret
    
    def isContainedIn(self, obj):
        for item in obj.children:
            if self.value == item.value:
                return item
        return False
finalList = []

# Loading the Data
def loadData():
    
    fileName = 'adult.data'
    colNames = ['age', 'workclass', 'fnlwgt', 'education', 'education-num',
                'marital-status', 'occupation', 'relationship', 'race', 'sex',
                'capital-gain', 'capital-loss', 'hours-per-week',
                'native-country', 'income']
    
    df = pd.read_csv(fileName, names = colNames)
    df = preprocessData(df)
        
    return df
    
# Preprocess the Data    
def preprocessData(df):
    
    # Changing all Missing Data ?s to NaN
    df = df.applymap(lambda d: np.nan if d== ' ?' else d)
    df = df.dropna(axis = 0) # Drop Rows With NaNs
    
    # Deleting Attributes Which Are Not Needed
    df.drop('fnlwgt', axis = 1, inplace = True)
    df.drop('education-num', axis = 1, inplace = True)
    
    # Converting Continuous Variables to Categorical
    df['age'] = pd.cut(df['age'], [0, 30, 60, 100], 
                labels = ['Young', 'Middle-aged', 'Senior'], 
                right = True, include_lowest = True)
    df['hours-per-week'] = pd.cut(df['hours-per-week'], [0, 20, 40, 100], 
                           labels = ['Part-time', 'Full-time', 'Over-time'], 
                           right = True, include_lowest = True)
    df['capital-gain'] = pd.cut(df['capital-gain'], [0, 1, 100000], 
                       labels = ['No-Gain', 'Positive-Gain'], 
                       right = True, include_lowest = True)
    df['capital-loss'] = pd.cut(df['capital-loss'], [0, 1, 100000],
                   labels = ['No-Loss', 'Positive-Loss'], 
                   right = True, include_lowest = True)
    
    # Removing Spaces from the Data Entries
    df = df.applymap(lambda x: x.strip() if type(x) is str else x)
    
    return df

# (b) Problem 6.8 (2): FP-Growth Algorithm
def fpg(df, min_sup):
    size = len(df.index)
    min_sup = (min_sup / 100.0) * size
    print 'Minimum Support Count: ', int(min_sup)
    
    # Generate Initial Set of Candidates
    print '\nPlease Wait. Scanning Database First Time.'
    candidates = getC1(df)
    
    # Generate Initial Set of Frequent Itemsets
    frequent = {k:v for k, v in candidates.items() if v >= min_sup}
    print 'Database Scan Complete.'
    
    # Generate List of Frequent Itemsets in Descending Order
    flist = sorted(frequent.items(), key=operator.itemgetter(1), reverse=True)
    itemsets1 = flist
    flist = [i[0] for i in flist]
    print '\nF-List Generated: ', flist
    print '\nPlease Wait. Scanning Database Second Time.'
    df = df.reset_index()
        
    # Scan Database Again to Find Ordered Frequent Itemlist
    ordFreqList = [[] for _ in range(len(df))]
    for i, j in df.iterrows():
        if i>0 and i % 10000 == 0:
            print 'Read', i, 'Records.'
        row = j.tolist()
        for item in flist:
            if item in row:
                ordFreqList[i].append(item)
    print 'Database Scan Complete.'
    display(itemsets1, 1)
    freqItemSets = frequentItems(flist, ordFreqList, min_sup)
    total = len(itemsets1) + len(freqItemSets)
    dictlist = []
    maxi = 0
    for key, value in freqItemSets.iteritems():
        if len(key) > maxi:
            maxi = len(key)
        temp = [key,value]
        dictlist.append(temp)
    for i in range(2, maxi+1):
        display(dictlist, i)
    
    print '\nFrequent Itemsets Have Been Generated. End of FP-Growth Algorithm.'
    print 'No. of Frequent Itemsets Generated: ', total

def getC1(df):
    candidates = {}
    for index, row in df.iterrows():
        data = list(row)
        if index>0 and index % 10000 == 0:
            print 'Read', index, 'Records.'
        for item in data:
            if item in candidates.keys():
                candidates[item] += 1
            else:
                candidates[item] = 1
    return candidates
        
def display(sets, k):
    print '\n---- Frequent [', k, '] Itemsets ----'
    if k == 1:
        for i in sets:
            key = list(i[0].split())
            val = i[1]
            print key, ' - ', val
    else:
        for i in sets:
            if len(i[0]) == k:
                key = list(i[0])
                val = i[1]
                print key, ' - ', val            

# Generate the FP Tree
def makeTree(flist):
    init = Tree([], 0)
    for item in flist:
        node = init
        for elem in item:
            newnode = Tree(elem, 1)
            index = newnode.isContainedIn(node)
            if index:
                index.weight += 1
                node = index
            else:
                node = node.children
                node.append(newnode)
                node = newnode
    return init

# Generate the Frequent Pattern Base
def getPaths(tree, item, lst = []):
    node = tree
    if node.value == item:
        lst.append(node.weight)
        temp = []
        temp.extend(lst)
        temp.pop(0)
        finalList.append(temp)
        lst.pop()
    else:
        lst.append(node.value)
        for child in node.children:
            getPaths(child, item)
        lst.pop()

# Generate Frequent Itemsets        
def frequentItems(items, flist, min_sup):
    frequent_patterns = {}
    global finalList
    tree = makeTree(flist)
    for item in items:
        getPaths(tree, item)
        condPattBase = finalList
        localDict = freqPatterns(item, condPattBase, min_sup)
        frequent_patterns.update(localDict)
        finalList = []
    return frequent_patterns
        
def freqPatterns(item, patterns, min_sup):
    globalDict = {}
    for pattern in patterns:
        localDict = {}
        if len(pattern) > 1:
            elements = getCombs(pattern[:-1])
            for elem in elements:
                elem.append(item)
                tup = tuple(elem)
                elem.pop()
                if tup not in globalDict.keys():
                    count = getCount(elem, patterns)
                    if count >= min_sup:
                        localDict[tup] = count
        globalDict.update(localDict)
    return globalDict

def getCombs(x):
    n = len(x)
    c = [list(comb) for i in range(n) for comb in combinations(x, i + 1)]
    return c

def getCount(elem, patterns):
    support = 0
    for pattern in patterns:
        flag = 1
        for ele in elem:
            if ele not in pattern:
                flag = 0
        if flag == 1:
            support += pattern[-1]
    return support

def main():
    df = loadData()
    print '---- Running FP-GROWTH.PY ----'
    min_sup = input('Enter the Support Threshold %: ')
    start_time = time.time()
    fpg(df, min_sup)
    run_time = time.time() - start_time
    print '\nExecution Time: ', run_time

main()
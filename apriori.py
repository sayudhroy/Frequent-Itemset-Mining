"""
Apriori Algorithm 
"""

# Importing the Libraries
import pandas as pd
import numpy as np
import itertools as it
import time

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

# (a) Problem 6.7 (1): Apriori Algorithm
def apriori(df, min_sup):
    min_sup = (min_sup / 100.0) * len(df.index)
    print 'Minimum Support Count: ', int(min_sup)
    
    # Generate Initial Set of Candidates
    print '\nPlease Wait. Calculating Frequent Itemsets.'
    candidates = getC1(df)
    
    # Generate Initial Set of Frequent Itemsets
    frequent = {k:v for k, v in candidates.items() if v >= min_sup}
    freq = len(frequent) # No. of Frequent Itemsets Generated
    step = 1
    total = freq
    display(frequent, step)
    
    while 1:
        step += 1
        print '\nPlease Wait. Calculating Frequent Itemsets.'
        candidates = join(frequent, step)
        frequent = prune(df, candidates, frequent, min_sup)
        freq = len(frequent)
        total += freq
        if freq == 0:
            break
        display(frequent, step)
        
    print '\nFrequent Itemsets Have Been Generated. End of Apriori Algorithm.'
    print 'No. of Frequent Itemsets Generated: ', total
    
def getC1(df):
    candidates = {}
    for index, row in df.iterrows():
        data = list(row)
        for item in data:
            if item in candidates.keys():
                candidates[item] += 1
            else:
                candidates[item] = 1
    return candidates
        
def display(frequent, k):
    print '\n---- Frequent [', k, '] Itemsets ----'
    for i in frequent:
        key = i.split(' ')
        val = frequent[i]
        print key, ' - ', val
        
def join(frequent, k):
    cand_sets = []
    items = frequent.keys()
    size = len(items)
    for i in range(size):
        for j in range(i, size):
            joined = list(set(items[i].split(' ')) | set(items[j].split(' ')))
            itemset = list(it.combinations(joined, k))
            if len(itemset) > 0:
                itemset = list(itemset[0])
                key = ' '.join(str(x) for x in itemset)
                cand_sets.append(key)
    return cand_sets

def sortInto(candidates):
    localCache = []
    for i in candidates:
        key = i.split(' ')
        key.sort()
        temp = tuple(key)
        if temp not in localCache:
            localCache.append(temp)
    localCache = [' '.join(item) for item in localCache]
    return localCache

def prune(df, candidates, frequent, min_sup):
    freq_sets = {}
    candidates = sortInto(candidates)
    for row in df.iterrows():
        index, data = row
        dataset = set(data)
        for i in candidates:
            itemset = i.split()
            if has_infrequent_subset(i, frequent) == 0:
                itemset_set = set(itemset)
                diff = itemset_set - dataset
                if len(diff) == 0:
                    if i not in freq_sets:
                        freq_sets[i] = 1
                    else:
                        freq_sets[i] += 1
    for key in freq_sets.keys():
        if freq_sets[key] < min_sup:
            del freq_sets[key]
    return freq_sets

def has_infrequent_subset(itemset, frequent):
    itemset = itemset.split()
    k = len(itemset)
    subsets = list(it.combinations(itemset, k-1))
    freq_sets = [set(x.split()) for x in frequent.keys()]
    for i in subsets:
        if set(i) not in freq_sets:
            return 1
    return 0

def main():
    df = loadData()
    print '---- Running APRIORI.PY ----'
    min_sup = input('Enter the Support Threshold %: ')
    start_time = time.time()
    apriori(df, min_sup)
    run_time = time.time() - start_time
    print '\nExecution Time: ', run_time

main()
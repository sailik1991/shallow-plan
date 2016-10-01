#!/usr/bin/python
from gensim import models
from copy import deepcopy
from math import ceil,floor
from itertools import permutations
import random
import sys, getopt
import random

blank_percentage = 0.05
pediction_set_size = 10
window_size = 1

""" NEEDED FOR TRAINING """
def remove_random_actions(plan):
    blank_count = int(ceil(len(plan) * blank_percentage + 0.5))
    incomplete_plan = deepcopy(plan)
    indices = []
    for i in range(blank_count):
        missing_action_index = random.randrange(0, len(plan))
        if missing_action_index in indices:
            # making sure that the indices generated are unique
            i -= 1
            continue
        else:
            incomplete_plan[ missing_action_index ] = u''
            indices.append(missing_action_index)
    return blank_count, indices, incomplete_plan

""" NEEDED FOR DUP """
def getActionsForBlanks(T):
    index = []
    for i in xrange(len(T)):
        v = max(T[i])
        index.append( random.choice([j for j in xrange(len(T[i])) if T[i][j] == v]) )
    return index

def verify(T, indices, actions, plan):
    correct = 0.0
    for i in xrange(len(T)):
        acts = sorted( range(len(T[i])), key=lambda x:T[i][x] )[-1*pediction_set_size:]
        if plan[indices[i]] in acts:
            correct += 1.0
    return correct

""" NEEDED FOR BRUTE FORCE """
# p = permutation of actions
# ip = incomplete plan
def getTentativePlan(p, ip, indices):
    for i in range(len(indices)):
        ip[indices[i]] = p[i]
    return ip

def permuteOverMissingActions(actions, blank_count, indices, incomplete_plan):
    ''' Exausts 64 GB of RAM when
        blank_count > 3,
        #( actions ) >= 1250
        precomputing this stuff also does not work
    '''
    action_set = []
    tentative_plans = []
    for p in permutations(actions, blank_count):
    #for p in precomputed_permutations(blank_count):
        action_set.append(p)
        tentative_plans.append(getTentativePlan(p, incomplete_plan, indices))
    return action_set, tentative_plans

def predictAndVerify(indices, tentative_plans, action_set, plan):
    for i in range(len(indices)):
        window_sized_plans = []
        for tp in tentative_plans:
            window_sized_plans.append( tp[indices[i]-window_size:indices[i]+window_size+1] )
        scores = model.score( window_sized_plans )
        best_indices = scores.argsort()[-1*pediction_set_size:][::-1]
        for j in best_indices:
            if action_set[j][i] == plan[indices[i]]:
                correct += 1
                break;
    return correct

def min_uncertainty_distance_in_window_size(indices):
    # Makes sure that within a window size there is only one missing action
    # Optimized code from http://stackoverflow.com/questions/15606537/finding-minimal-difference
    if len(indices) <= window_size:
        return window_size+1
    idx = deepcopy(indices)
    idx = sorted(idx)
    res = [ idx[i+window_size]-idx[i] for i in xrange(len(idx)) if i+window_size < len(idx) ]
    return min(res)

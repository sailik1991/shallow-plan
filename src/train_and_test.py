#!/usr/bin/python
from gensim import models
from copy import deepcopy
from math import ceil,floor
from itertools import permutations
import random
import sys, getopt

blank_percentage = 0.05
pediction_set_size = 10
window_size = 1

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

# p = permutation of actions
# ip = incomplete plan
def getTentativePlan(p, ip, indices):
    for i in range(len(indices)):
        ip[indices[i]] = p[i]
    return ip

def permuteOverMissingActions(actions, blank_count, indices):
    ''' Exausts 64 GB of RAM when
        blank_count >= 3,
        #( actions ) >= 1250
    '''
    action_set = []
    tentative_plans = []
    for p in permutations(actions, blank_count):
     action_set.append(p)
     tentative_plans.append(getTentativePlan(p, incomplete_plan, indices))
    return action_set, tentative_plans

def predictAndVerify(indices, tentative_plans, action_set):
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
        return 2
    idx = deepcopy(indices)
    idx = sorted(idx)
    res = [ idx[i+window_size]-idx[i] for i in xrange(len(idx)) if i+window_size < len(idx) ]
    return min(res)

def train_and_test(domain, shouldTrain, set_number):
    '''
    The function trains a model on training data and then tests the models accuracy on the testing data.
    Since training is time consuming, we save the model and load it later for further testing
    '''

    print "\n=== Set : %s ===\n" % str(set_number)

    # Train a model based on training data
    if shouldTrain == True:
        sentences = models.word2vec.LineSentence(domain+'/train'+str(set_number)+'.txt')
        model = models.Word2Vec(sentences=sentences, min_count=1, workers=4, hs=1, window=window_size, iter=10)
        model.save(domain+'/model.txt')
    else:
        # OR load a mode
        model = models.Word2Vec.load(domain+'/model'+str(set_number)+'.txt')

    print "Training : COMPLETE!"

    # Evaluate model on test data
    plans = open(domain+'/test'+str(set_number)+'.txt').read().split("\n")
    list_of_actions = [[unicode(actn, "utf-8") for actn in plan_i.split()] for plan_i in plans]
    actions = model.vocab.keys()

    correct = 0
    total = 0

    print "Testing : RUNNING . . ."
    list_of_actions = [x for x in list_of_actions if len(x) != 0]
    for itr in xrange(len(list_of_actions)):

        plan = list_of_actions[itr]
        # This reduces the combinatorial burst as all permutations do not need to be checked
        # This is the logic used for the paper's (http://rakaposhi.eas.asu.edu/aamas16-hankz.pdf) code
        while True:
            blank_count, indices, incomplete_plan = remove_random_actions(plan)
            if min_uncertainty_distance_in_window_size(indices) > window_size:
                break;

        total += blank_count
        for i in indices:
            tentative_plans = []
            tentative_actions = []
            temp_plan = deepcopy( incomplete_plan )
            for a in actions:
                temp_plan[i] = a
                tentative_plans.append( temp_plan[ max(0,i-window_size) : min(i+window_size+1,len(plan)) ] )
                tentative_actions.append(a)
            scores = model.score( tentative_plans )
            best_plan_args = scores.argsort()[-1*pediction_set_size:][::-1]
            for p in best_plan_args:
                if tentative_actions[p] == plan[i]:
                    correct += 1
                    break

        # Print at certain time intervals
        if (itr*100)/len(list_of_actions) % 10 == 0:
            sys.stdout.write( "\rProgress: %s %%" % str( (itr*100)/len(list_of_actions) ) )
            sys.stdout.flush()

        #action_set, tentative_plans = permuteOverMissingActions(actions, blank_count, indices)
        #correct = predictAndVerify( indices, tentativePlans, action_set)

    sys.stdout.write( "\r\rTesting : COMPLETE!\n")
    sys.stdout.flush()
    print "\nUnknown actions: %s; Correct predictions: %s" % (str(total), str(correct))
    print "Set Accuracy: %s\n" % str( float(correct*100)/total )
    return total, correct

def main(argv):
    #print argv
    domain = argv[0]
    train = True if len(argv)==2 and argv[1]=='t' else False
    k = 10

    print "\n=== Domain : %s ===\n" % domain

    total_unknown_actions = 0
    total_correct_predictions = 0
    for i in range(k):
        ua, cp = train_and_test( domain, train, i )
        total_unknown_actions += ua
        total_correct_predictions += cp

    print "\n==== FINAL STATISTICS ===="
    print "\nTotal unknown actions: %s; Total correct predictions: %s" % (str(total_unknown_actions), str(total_correct_predictions))
    print "ACCURACY: %s\n" % str( float(total_correct_predictions*100)/total_unknown_actions )

if __name__ == "__main__":
    main(sys.argv[1:])


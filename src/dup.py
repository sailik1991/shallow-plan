#!/usr/bin/python
from gensim import models
from copy import deepcopy
from utilities import *
from math import log

blank_percentage = 0.05
pediction_set_size = 10
window_size = 1

def train(domain, shouldTrain, setNumber):
    '''
    The function trains a model on training data and then tests the models accuracy on the testing data.
    Since training is time consuming, we save the model and load it later for further testing
    '''
    print "\n=== Set : %s ===\n" % str(setNumber)

    # Train a model based on training data
    if shouldTrain == True:
        sentences = models.word2vec.LineSentence(domain+'/train'+str(setNumber)+'.txt')
        model = models.Word2Vec(sentences=sentences, min_count=1, workers=4, hs=1, window=window_size, iter=10)
        model.save(domain+'/model'+str(setNumber)+'.txt')
    else:
        # OR load a mode
        model = models.Word2Vec.load(domain+'/model'+str(setNumber)+'.txt')

    print "Training : COMPLETE!"

    # Evaluate model on test data
    plans = open(domain+'/test'+str(setNumber)+'.txt').read().split("\n")
    list_of_actions = [[unicode(actn, "utf-8") for actn in plan_i.split()] for plan_i in plans]
    actions = model.vocab.keys()
    return [x for x in list_of_actions if len(x) > window_size*2], actions

def train_and_test(domain, shouldTrain, setNumber):

    list_of_actions, actions = train(domain, shouldTrain, setNumber)

    correct = 0
    total = 0
    tree_height = log( len(actions), 2 )
    
    print "Testing : RUNNING . . ."
    for itr in xrange(len(list_of_actions)):

        plan = list_of_actions[itr]

        blank_count, indices, incomplete_plan = remove_random_actions(plan)
        total += blank_count
        
        """ DUP algorithm """
        T = []
        for i in xrange(blank_count):
            t.append([1/len(actions) for j in xrange(len(actions)])
            
        i = 0
        while True:
            i += 1
            if i == 1500:
                break
            
            index = getActionForBlanks(T)
            for k in len(blank_count):
                T[k][index[k]] += 
        
        correct += predictAndVerify(indices, tentative_plans, action_set)

        """
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
        """
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

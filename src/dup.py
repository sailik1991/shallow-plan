#!/usr/bin/python
from gensim import models
from copy import deepcopy
from utilities import *
from math import log

blank_percentage = 0.05
pediction_set_size = 10
window_size = 4
gamma = 0.1

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
            T.append([1.0/len(actions) for j in xrange(len(actions))])

        i = 0
        while True:
            i += 1
            if i == 1500:
                break

            action_index = getActionsForBlanks(T)
            for k in xrange(blank_count):
                T[k][action_index[k]] += gamma*window_size*2
                for w in xrange( max(0,indices[k]-window_size), min(indices[k]+window_size+1,len(plan)) ):
                    if w in indices:
                        T[indices.index(w)][action_index[indices.index(w)]] += gamma*window_size*2

            # Normalize the T-values for each blank action
            for r in xrange(blank_count):
                rsum = sum(T[r])
                for c in xrange(len(actions)):
                    T[r][c] /= rsum

        correct += verify(T, indices, actions, plan)

        # Print at certain time intervals
        if (itr*100)/len(list_of_actions) % 10 == 0:
            sys.stdout.write( "\rProgress: %s %%" % str( (itr*100)/len(list_of_actions) ) )
            sys.stdout.flush()

    sys.stdout.write( "\r\rTesting : COMPLETE!\n")
    sys.stdout.flush()
    print "\nUnknown actions: %s; Correct predictions: %s" % (str(total), str(correct))
    print "Set Accuracy: %s\n" % str( float(correct*100)/total )
    return total, correct

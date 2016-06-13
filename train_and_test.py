#!/usr/bin/python
from gensim import models
from copy import deepcopy
from math import ceil,floor
from itertools import permutations
import random

blank_percentage = 0.05

def remove_random_actions(plan):
    blank_count = int(floor(len(plan) * blank_percentage + 0.5))
    incomplete_plan = deepcopy(plan)
    indices = []
    for i in range(blank_count):
        missing_action_index = random.randrange(0, len(plan))
        if incomplete_plan[ missing_action_index ] == u'':
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

# Train a model based on training data
sentences = models.word2vec.LineSentence('train.txt')
model = models.Word2Vec(sentences=sentences, min_count=1, workers=4, hs=1)
model.save_word2vec_format('model', fvocab='vocab')
#model = models.Word2Vec.load_word2vec_format('./model.file', fvocab='./vocab.file')
print "Model training complete"

# Evaluate model on test data
plans = open('test.txt').read().split("\n")
list_of_actions = [[unicode(actn, "utf-8") for actn in plan_i.split()] for plan_i in plans]
actions = model.vocab.keys()

pediction_set_size = 10

for plan in list_of_actions:
    blank_count, indices, incomplete_plan = remove_random_actions(plan)
    print "generating tentative plans for :" + str(incomplete_plan) + ": with blank count = " + str(blank_count)

    action_set = []
    tentative_plans = []
    for p in permutations(actions, blank_count):
        action_set.append(p)
        tentative_plans.append(getTentativePlan(p, incomplete_plan, indices))

    scores = model.score( tentative_plans )
    # Get the permutations that give the 3 highest scores
    best_permutations = scores.argsort()[-1*pediction_set_size:][::-1]
    correct = 0
    for j in best_permutations:
        print action_set[j]
        for i in range(len(indices)):
            print str(i), plan[indices[i]]
            if action_set[j][i] == plan[indices[i]]:
                correct += 1

    print (blank_count, correct)
    exit(0)

import bf
import dup
import sys

def main(argv):
    #print argv
    domain = argv[0]
    train = True if len(argv)==2 and argv[1]=='t' else False
    k = 10

    print "\n=== Domain : %s ===\n" % domain

    total_unknown_actions = 0
    total_correct_predictions = 0
    for i in range(k):
        ua, cp = dup.train_and_test( domain, train, i )
        total_unknown_actions += ua
        total_correct_predictions += cp

    print "\n==== FINAL STATISTICS ===="
    print "\nTotal unknown actions: %s; Total correct predictions: %s" % (str(total_unknown_actions), str(total_correct_predictions))
    print "ACCURACY: %s\n" % str( float(total_correct_predictions*100)/total_unknown_actions )

if __name__ == "__main__":
    main(sys.argv[1:])

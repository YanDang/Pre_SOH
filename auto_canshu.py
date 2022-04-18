import hyperopt
from hyperopt import hp
from hyperopt import fmin,tpe
def objective(args):
    case,val = args
    if case == 'case 1':
        return val
    else:
        return val ** 2
space = hp.choice('a',
                  [
                      ('case 1',1+hp.lognormal('c1',0,1)),
                      ('case 2',hp.uniform('c2',-10,10))
                  ])
best = fmin(objective,space,algo=tpe.suggest,max_evals=100)
print(best)
print(hyperopt.space_eval(space,best))
import random
import math
import sys


def T(TA):
    return -TA * math.log(random.uniform(0,1))

if __name__ == '__main__':
    print(T(int(sys.argv[1])))

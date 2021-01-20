#! /usr/bin/env python3

import os, sys, string, random

def get_randomfile(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

DATA_PATH = './data'
os.makedirs(DATA_PATH, exist_ok=True)

for i in range(int(sys.argv[1])):
    f = open(os.path.join(DATA_PATH, "data"+str(i)),'w')
    f.write(get_randomfile(102400)) #100kB
    f.close()

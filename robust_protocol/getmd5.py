#! /usr/bin/env python3
import hashlib
import os
filepath_list = []
received_list = []
with open("check.md5", 'w') as c:
    for file in os.listdir("./data"):
        filepath = os.path.join("./data", file)
        if os.path.isfile(filepath):
            filepath_list.append(filepath)
            
            with open(filepath, mode='rb') as f:
                c.write(hashlib.md5(f.read()).hexdigest() + '\n')
            

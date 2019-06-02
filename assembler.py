#import numpy as np
import sys

instruction = {
            'store':[0, 1, 0, 0, 0],
            'storeIndr':[0, 1, 1, 0, 0],
            'add': [0, 0, 0, 0, 0],
            'addi': [1, 0, 0, 0, 0],
            'addIndr':[0, 0, 1, 0, 0],
            'sub': [0, 0 ,0, 0, 1],
            'subi':[1, 0, 0, 0, 1],
            'subIndr': [0, 0, 1, 0, 1],
            'clear':[1, 0, 0, 1, 1],
            'branch':[1, 0, 0, 1, 0]}

def to_bin(d):
    if(d[0] == '-'):
        d = str(256 - int(d[1:]) )
    b = [int(x) for x in list('{0:0b}'.format(int(d)))][-8:]
    zero = [0 for i in range(8)]
    zero[-len(b):] = b
    return zero

def assemble(assembly):
    b_instructions = []
    i = 0
    define_dict = {}
    for l in assembly:
        i +=1
        if(len(l) <= 1):
            continue
        words = l.split('\n')[0].split(' ')
        if len(words) == 0:
            continue
        elif len(words) == 1:
            if(words[0] != 'clear'):
                raise Exception('Invalid Syntax on line', i)
            b_instructions += [instruction[words[0]] + [0 for i in range(8)]]
        else: 
            if words[0] not in instruction:
                if(words[0] == '#define'):
                    define_dict[words[1]] = to_bin(words[2])
                    continue
                else:
                    raise Exception('Invalid Syntax on line', i, words[0])
            if(words[1] in define_dict):
                b_instructions += [instruction[words[0]] + define_dict[words[1]]]
            else:
                b_instructions += [ instruction[words[0]] + to_bin(words[1])]
    return b_instructions    



def main():
    a_file = sys.argv[1]
    assembly = open(a_file, 'r')
    b_instructions = assemble(assembly)
 
    if(len(sys.argv) < 3):
        file_out = 'a.out'
    else:
        file_out = sys.argv[2]
    f_out = open(file_out, 'w')
    for b in b_instructions:
        s = ''
        for i in b:
            s+= str(i) + ' '
        f_out.write(s + '\n')
    f_out.close()

if __name__ == "__main__":
    main()
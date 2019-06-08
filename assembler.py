import itertools
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
            'branch':[1, 0, 0, 1, 0]
            }

def to_bin(d):
    if(d[0] == '-'):
        d = str(256 - int(d[1:]) )
    b = [int(x) for x in list('{0:0b}'.format(int(d)))][-8:]
    zero = [0 for i in range(8)]
    zero[-len(b):] = b
    return zero



def is_(i, f):
    try:
        val = f(i)
    except ValueError:
        return False
    return True
isInt = lambda i : is_(i, int)
isNumeric = lambda i : is_(i, float)

def assemble(assembly):
    b_instructions = []
    define_dict = {}
    
    for l, i in zip(assembly, itertools.count(1)):
        if(len(l) <= 1):
            continue
        words = l.split('\n')[0].split(' ')
        words = list(filter(lambda x : x is not '', words))
        if words[0] not in instruction: # not builtin instruction
            if(words[0] == '#define'):  # check for previously defined token
                if len(words) < 3:
                    raise SyntaxError('Invalid assembly syntax on line {}. Missing arguments for #define. Must have name followed by constant.'.format(i))
                elif isNumeric(words[1]):
                    raise SyntaxError('Invalid assembly syntax on line {}. #define name \'{}\' cannot be numeric.'.format(i, words[1])) 
                elif not isInt(words[2]):
                    raise SyntaxError('Invalid assembly syntax on line {}. #define value \'{}\' must be an integer.'.format(i, words[2]))
                else:
                    define_dict[words[1]] = to_bin(words[2])  
            else: 
                raise SyntaxError('Invalid assembly syntax on line {}. Token \'{}\' is not recognized.'.format(i, words[0]))
        
        elif len(words) > 1: # recognized instruction with at least one argument
            if words[1] in define_dict:
                b_instructions += [instruction[words[0]] + define_dict[words[1]]]        
            elif not isInt(words[1]): #argument must be integer, since other cases are handled above
                raise SyntaxError('Invalid assembly syntax on line {}. Argument \'{}\' must be an integer.'.format(i, words[1]))
            else: # argument is an integer, so the following will work
                b_instructions += [instruction[words[0]] + to_bin(words[1])]
        else: # if no argument is given, fill with zeros
              # this might be unintended, however, if the programmer is aware of this
              # s/he can use this to simplify code.
              # e.g. nop can be achieved with 'addi'
            b_instructions += [instruction[words[0]] + [0]*8]

    return b_instructions    

def main():
    a_file = sys.argv[1]
    with open(a_file, 'r') as assembly:
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
    import sys
    main()
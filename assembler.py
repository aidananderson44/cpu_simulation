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

def isInt(i):
    try:
        val = int(i)
    except ValueError:
        return False
    return True

def assemble(assembly):
    b_instructions = []
    i = 0
    define_dict = {}
    for l in assembly:
        i +=1
        if(len(l) <= 1):
            continue
        words = l.split('\n')[0].split(' ')
        words = list(filter(lambda x : x is not '', words))
        if words[0] not in instruction:
            if(words[0] == '#define'):
                if len(words) < 3:
                    raise SyntaxError('Invalid assembly syntax on line {}. Missing arguments for #define. Must have token followed by constant.'.format(i))
                if isInt(words[1]):
                    raise SyntaxError('Invalid assembly syntax on line {}. #define name \'{}\' cannot be numeric.'.format(i, words[1])) 
                if not isInt(words[2]):
                    raise SyntaxError('Invalid assembly syntax on line {}. #define value \'{}\' must be numeric.'.format(i, words[2]))
                define_dict[words[1]] = to_bin(words[2])  
            else:
                raise SyntaxError('Invalid assembly syntax on line {}. Token \'{}\' is not recognized.'.format(i, words[0]))
        
        elif(len(words) > 1 and words[1] in define_dict):
            b_instructions += [instruction[words[0]] + define_dict[words[1]]]        
        else:
            if len(words) > 1 and not isInt(words[1]):
                raise SyntaxError('Invalid assembly syntax on line {}. Argument \'{}\' must be numeric.'.format(i, words[1]))
            try:
                arg = to_bin(words[1])
            except:
                arg = [0]*8
            b_instructions += [instruction[words[0]] + arg]

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
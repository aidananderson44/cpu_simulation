import itertools
instruction = {
            'store':     [0, 1, 0, 0, 0],
            'storeIndr': [0, 1, 1, 0, 0],
            'add':       [0, 0, 0, 0, 0],
            'addi':      [1, 0, 0, 0, 0],
            'addIndr':   [0, 0, 1, 0, 0],
            'subi':      [1, 0, 0, 0, 0],
            'lsl':       [0, 0 ,0, 0, 1],
            'lsli':      [1, 0, 0, 0, 1],
            'lslIndr':   [0, 0, 1, 0, 1],
            'clear':     [1, 0, 0, 1, 1],
            'loadi':     [1, 0, 0, 1, 1],
            'load':      [0, 0, 0, 1, 1],
            'loadIndr':  [0, 0, 1, 1, 1],
            'branchi':   [1, 0, 0, 1, 0],
            'branch':    [0, 0, 0, 1, 0],
            'branchIndr':[0, 0, 1, 1, 0]
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

def syntax_adjust(instr, expr):
    if instr[:7] == 'branchi':
        expr = str(int(expr) - 2)
    if instr[:3] == 'subi':
        expr = str(256 - int(expr))
    return expr

def assemble(assembly):
    b_instructions = []
    eval_dict = {'len' : len, 'dir' : dir, 'PC' : 0}
    num_builtin = len(eval_dict) + 1
    eval_dict['num_builtin'] = num_builtin
    for l, i in zip(assembly, itertools.count(1)):
        
        if(len(l) <= 1):
            continue
        words = l.split('\n')[0].split(' ')
        words = list(filter(lambda x : x is not '', words))
        if words[0][0] is '#':
            continue
        if words[0] not in instruction: # not builtin instruction
            if(words[0] == 'DEFINE'):  # check for previously defined token
                if len(words) < 3:
                    raise SyntaxError('Invalid assembly syntax on line {}. Missing arguments for #define. Must have name followed by constant.'.format(i))
                expr_str = ' '.join(words[2:])
                try:
                    expr = str(eval(expr_str, {'__builtins__' : None}, eval_dict))
                except TypeError:
                    raise SyntaxError('Invalid expression on line {}.'.format(i))
                
                if isNumeric(words[1]):
                    raise SyntaxError('Invalid assembly syntax on line {}. #define name \'{}\' cannot be numeric.'.format(i, words[1])) 
                elif not isInt(expr):
                    raise SyntaxError('Invalid assembly syntax on line {}. #define value \'{}\' must be an integer.'.format(i, expr))
                else:     
                    eval_dict[words[1]] = int(expr)
            else: 
                raise SyntaxError('Invalid assembly syntax on line {}. Token \'{}\' is not recognized.'.format(i, words[0]))
        
        else: 
            instr = [instruction[words[0]] + [0]*8]
            if len(words) > 1 and words[1][0] is not '#': # recognized instruction with at least one argument     
                expr_str = ' '.join(words[1:])
                try:  
                    expr = str(eval(expr_str, {'__builtins__' : None}, eval_dict))
                    if not isInt(expr):
                        raise SyntaxError('Invalid expression on line {}. Expression {} evaluates to {} and not to an integer.'.format(i, expr_str, expr))
                    
                    expr = syntax_adjust(words[0], expr)
                        
                    instr = [instruction[words[0]] + to_bin(expr)]
                except TypeError:
                    instr = [['i', i, words[0], expr_str, eval_dict['PC']]] 
            b_instructions += instr
            eval_dict['PC'] += 1
    final_instr = []

    for instr in b_instructions:
        if instr[0] is not 'i':
            final_instr += [instr]
        else:
            ed = eval_dict.copy()
            ed['PC'] = instr[4]
            try:
                expr = str(eval(instr[3], {'__builtins__' : None}, ed))
            except TypeError:            
                raise SyntaxError('Invalid expression on line {}.'.format(instr[1]))
            if not isInt(expr):
                raise SyntaxError('Invalid expression on line {}. Expression {} evaluates to {} and not to an integer.'.format(i, expr_str, expr))
            expr = syntax_adjust(instr[2], expr)
            final_instr += [instruction[instr[2]] + to_bin(expr)] 
    return final_instr   

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
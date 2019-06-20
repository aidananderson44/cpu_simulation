import itertools
instruction = {
            'addi' : [0, 0, 0, 0, 0],
            'add' : [0, 1, 0, 0, 0],
            'addIndr' : [1, 0, 0, 0, 0],
            'subi' : [0, 0, 0, 0, 1],
            'sub' : [0, 1, 0, 0, 1],
            'subIndr' : [1, 0, 0, 0, 1],
            'muli' : [0, 0, 0, 1, 0],
            'mul' : [0, 1, 0, 1, 0],
            'mulIndr' : [1, 0, 0, 1, 0],
            'modi' : [0, 0, 0, 1, 1],
            'mod' : [0, 1, 0, 1, 1],
            'modIndr' : [1, 0, 0, 1, 1],
            'lsli' : [0, 0, 1, 0, 0],
            'lsl' : [0, 1, 1, 0, 0],
            'lslIndr' : [1, 0, 1, 0, 0],
            'andi' : [0, 0, 1, 0, 1],
            'and' : [0, 1, 1, 0, 1],
            'andIndr' : [1, 0, 1, 0, 1],
            'skipCondi' : [0, 0, 1, 1, 0],
            'skipCond' : [0, 1, 1, 1, 0],
            'skipCondIndr' : [1, 0, 1, 1, 0],
            'jmpi' : [0, 0, 1, 1, 1],
            'jmp' : [0, 1, 1, 1, 1],
            'jmpIndr' : [1, 0, 1, 1, 1],
            'store' : [1, 1, 0, 0, 1],
            'storeIndr' : [1, 1, 0, 0, 0],
            'clear' : [0, 0, 0, 1, 0],
            'divi' : [1, 1, 0, 1, 0],
            'div1' : [1, 1, 0, 1, 1],
            'divIndr' : [1, 1, 1, 0, 0],
            'powi' : [1, 1, 1, 0, 1],
            'pow' : [1, 1, 1, 1, 0],
            'powIndr' : [1, 1, 1, 1, 1],
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
    if instr[:7] == 'jmpi':
        expr = str(int(expr) - 2)
    if instr[:5] == 'clear':
        expr = '0'
    return expr

class AssemblyException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return str(self.message)

def assemble(assembly, breakpoints):
    b_instructions = []
    eval_dict = {'len' : len, 'dir' : dir, 'PC' : 0}
    num_builtin = len(eval_dict) + 1
    eval_dict['num_builtin'] = num_builtin
    macro_dict = {}
    assembly_list = []
    breakpoint_pc = []
    for i, j in zip(assembly, itertools.count(1)):
        assembly_list += [(i, j)]
    
    in_macro = None
    for (l, i), idx in zip(assembly_list, itertools.count(1)):

        if i in breakpoints:
            breakpoint_pc += [eval_dict['PC']]
        if(len(l) <= 1):
            continue
        words = l.split('\n')[0].split(' ')
        words = list(filter(lambda x : x is not '', words))
        if words[0][0] is '#':
            pass
        elif words[0] == 'BREAKPOINT':
            breakpoint_pc += [eval_dict['PC']]

        elif words[0] == 'STARTMACRO':
            if in_macro:
                raise AssemblyException('Error on line {}. Cannot nest macros'.format(i))
            if len(words) < 2:
                raise AssemblyException('Error on line {}. Macro definition must contantain a name.'.format(i))
            in_macro = words[1]
            m_vars = words[2:]
            macro_dict[words[1]] = [tuple(m_vars)]
        elif words[0] == 'ENDMACRO':
            in_macro = None

        elif words[0] in macro_dict:
            vals = ' '.join(words[1:])
            vals = vals.split(',')
            num_vars = len(macro_dict[words[0]][0])
            num_vals = len(vals)
            if num_vars != num_vals:
                raise AssemblyException('Error on line {}. Macro \'{}\' expected {} variables: {}.'.format(i, words[0], num_vars, macro_dict[words[0]][0]))
            v_dict = dict(zip(macro_dict[words[0]][0], vals))
            for instr, j in zip(macro_dict[words[0]][1:], itertools.count(0)):
                assembly_list.insert(idx + j, (instr.format(**v_dict), i)) 

        elif in_macro:
            if words[0] == 'DEFINE':
                raise AssemblyException('Invalid assembly syntax on line {}. Cannot put DEFINE statement in a macro'.format(i))
            macro_dict[in_macro] += [' '.join(words)] 
       
    
        elif(words[0] == 'DEFINE'):  # check for previously defined token
            if len(words) < 3:
                raise AssemblyException('Invalid assembly syntax on line {}. Missing arguments for #define. Must have name followed by constant.'.format(i))
            expr_str = ' '.join(words[2:])
            try:
                expr = str(eval(expr_str, {'__builtins__' : None}, eval_dict))
            except TypeError:
                raise AssemblyException('Invalid expression on line {}.'.format(i))
            
            if isNumeric(words[1]):
                raise AssemblyException('Invalid assembly syntax on line {}. #define name \'{}\' cannot be numeric.'.format(i, words[1])) 
            elif not isInt(expr):
                raise AssemblyException('Invalid assembly syntax on line {}. #define value \'{}\' must be an integer.'.format(i, expr))
            else:     
                eval_dict[words[1]] = int(expr)

        elif words[0] in instruction: 
            instr = [instruction[words[0]] + [0]*8]
            if len(words) > 1 and words[1][0] is not '#': # recognized instruction with at least one argument     
                expr_str = ' '.join(words[1:])
                try:  
                    expr = str(eval(expr_str, {'__builtins__' : None}, eval_dict))
                    if not isInt(expr):
                        raise AssemblyException('Invalid expression on line {}. Expression {} evaluates to {} and not to an integer.'.format(i, expr_str, expr))
                    
                    expr = syntax_adjust(words[0], expr)     
                    instr = [instruction[words[0]] + to_bin(expr)]
                except TypeError:
                    instr = [['i', i, words[0], expr_str, eval_dict['PC']]] 
            b_instructions += instr
            eval_dict['PC'] += 1
        else:
            raise AssemblyException('Invalid assembly syntax on line {}. Token \'{}\' is not recognized.'.format(i, words[0]))
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
                raise AssemblyException('Invalid expression on line {}.'.format(instr[1]))
            if not isInt(expr):
                raise AssemblyException('Invalid expression on line {}. Expression {} evaluates to {} and not to an integer.'.format(i, expr_str, expr))
            expr = syntax_adjust(instr[2], expr)
            final_instr += [instruction[instr[2]] + to_bin(expr)] 

    return final_instr, breakpoint_pc

def main():
    a_file = sys.argv[1]
    with open(a_file, 'r') as assembly:
        b_instructions, _ = assemble(assembly, [])
    
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
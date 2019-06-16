import numpy as np
from itertools import product
class component:
    def __init__(self):
        pass
    def update(self):
        pass
class control(component):
    def __init__(self, opcode_s, ALU_s):
        super().__init__()
        self.opcode_s = opcode_s
        self.ALU_s = ALU_s
        self.ALU_s_val = np.zeros(3, dtype = int)
        self.opcode_s_val = np.zeros(2, dtype = int)
        self.port_0 = lambda : self(0)
        self.port_1 = lambda : self(1)
        self.port_2 = lambda : self(2)
        self.port_3 = lambda : self(3)

        self.lookup_table = {}
        bin_3 = list(product([0, 1], repeat = 3))
        for b in bin_3:
            self.lookup_table[str([0, 0] + list(b))] = [[1], [0], [0, 0], [0, 0]]
        for b in bin_3:
            self.lookup_table[str([0, 1] + list(b))] = [[0], [0], [0, 0], [0, 0]]
        for b in bin_3:
            self.lookup_table[str([1, 0] + list(b))] = [[0], [0], [0, 1], [0, 0]]
                
        self.lookup_table[str([1, 1, 0, 0, 0])] = [[0], [0], [1, 1], [0, 0]]
        self.lookup_table[str([1, 1, 0, 0, 1])] = [[0], [1], [1, 0], [0, 0]]
        self.lookup_table[str([1, 1, 0, 1, 0])] = [[1], [0], [0, 0], [0, 1]]
        self.lookup_table[str([1, 1, 0, 1, 1])] = [[0], [0], [0, 0], [0, 1]]
        self.lookup_table[str([1, 1, 1, 0, 0])] = [[0], [0], [0, 1], [0, 1]]
        self.lookup_table[str([1, 1, 1, 0, 1])] = [[1], [0], [0, 0], [1, 0]]
        self.lookup_table[str([1, 1, 1, 1, 0])] = [[0], [0], [0, 0], [1, 0]]
        self.lookup_table[str([1, 1, 1, 1, 1])] = [[0], [0], [0, 1], [1, 0]]

    def update(self):
        self.opcode_s_val = self.opcode_s()
        self.ALU_s_val = self.ALU_s()
    def __call__(self, i):
        o = list(self.opcode_s_val)
        a = list(self.ALU_s_val)
        if str(o + a) in self.lookup_table:
            return self.lookup_table[str(o + a)][i]
        else:
            raise Exception('Invalid Control')
        

class instruction_memory(component):
    def __init__(self,source, word_size = 13, num_words = 256, mem = None, randomized = True):
        super().__init__()
        if mem is None:
            gen_f = np.random.rand if randomized else np.zeros
            self.mem = gen_f(word_size * num_words).reshape(num_words, word_size)
            self.mem = np.array(self.mem >= 0.5, dtype = int)
        else:
            self.mem = mem 
        self.source = source
        self.source_val = np.zeros(8)
    def update(self):
        self.source_val = self.source()
    def __call__(self):
        s = np.sum(self.source_val * 2**(7 - np.arange(8) ))
        return self.mem[s]

class register(component):
    def __init__(self, pc = None, source = None):
        super().__init__()
        self.pc = pc
        self.source = source
    def cycle(self):
        self.pc[:] = self.source()[:]
    def __call__(self):
        return self.pc[:]
    def __str__(self):
        return '{}'.format(self.pc)

class binary_op(component):
    def __init__(self, source1, source2, function):
        super().__init__()
        self.source1 = source1
        self.source2 = source2
        self.source1_val = np.zeros(8)
        self.source2_val = np.zeros(8)
        self.fun = function
    def update(self):
        self.source1_val = self.source1()
        self.source2_val = self.source2()
    def __call__(self):
        return self.fun(self.source1_val, self.source2_val)

class wire(component):
    def __init__(self,source,width = 8, length = 1):
        super().__init__()
        self.length = length
        self.width = width
        self.w = np.zeros(length*width, dtype = int).reshape(length, width)
        self.source = source
    
    def update(self):
        
        x = self.source()
        #w = np.zeros(self.length*self.width, dtype = int).reshape(self.length, self.width)
        #w[:self.length-1] = self.w[1:] 
        #w[self.length-1] = x
        self.w[:self.length-1] = self.w[1:] 
        self.w[self.length-1] = x
        
    def __call__(self):
        return self.w[0]
    

class instruction_buffer(component):
    def __init__(self, source):
        super().__init__()
        self.instr_b = np.zeros(13, dtype = int)
        self.IR = np.zeros(13, dtype = int)
        self.source = source

        port_names = ['opcode', 'ALU', 'Data']
        for i in port_names:
            def f_cr(self, x):
                return lambda : self(x)
            setattr(self, 'port_{}'.format(i), f_cr(self, i))

    def cycle(self):
      #  self.IR[:] = self.instr_b[:]
        self.IR[:] = self.source()[:]

    def __call__(self, ptype):
  
            if(ptype is 'opcode'):
                return self.IR[0:2]
            elif(ptype is 'ALU'):
                return self.IR[2:5]
            elif(ptype == 'Data'):
                return self.IR[-8:]
            else:
                raise Exception('Invalid port')
    def __str__(self):
        return '{}'.format(self.IR)

    def __repr__(self):
        return str(self.instr_b) + str(self.IR)

class demux(component):
    def __init__(self, dsource, csource, port_r = None,num = 2, width = 8):
        super().__init__()
        self.csource = csource
        self.csource_val = np.zeros(width)
        self.dsource = dsource
        self.dsource_val = np.zeros(num)
        self.control = None

        self.width = width
        if(port_r is not None):
            num = len(port_r)
        if(port_r is None):
            port_r = range(num)
        for i, j in zip(port_r, range(num)):
            def f_cr(self, x):
                return lambda : self(x)
            setattr(self, 'port_{}'.format(j), f_cr(self, i))

    def update(self):
        self.dsource_val = self.dsource()
        self.csource_val = self.csource()
    def __call__(self, i):
        control = list(self.csource_val)

        if(type(i) is not list):
            i = [i]

        if(i == control):
            return self.dsource_val
        else:
            return np.zeros(self.width)


def to_dec(b):
    return np.sum(b * 2**(7 - np.arange(8) ))
def to_bin(d, w_len = 8):
    if d < 0:
        d = 256 + d
    try:
        b = [int(x) for x in list('{0:0b}'.format(d))]
    except:
        return np.zeros(8)

    l = min(w_len, len(b))
    x = np.zeros(w_len, dtype = int)
    x[-l:] = b[-l:]
    return x

class main_mem(component):
    def __init__(self, source1, source2, source3,source4 = None, randomized = True):
        super().__init__()
        self.source1 = source1
        self.source2 = source2
        self.source1_val = np.zeros(8)
        self.source2_val = np.zeros(8)
        self.source3 = source3
        self.source4 = source4
        gen_f = np.random.rand if randomized else np.zeros
        self.mem = gen_f(8*256).reshape(256, 8)
        self.mem = np.array(self.mem >= 0.5, dtype = int)
        self.mem[0] = np.zeros(8)
        self.port_0 = lambda : self(1)
        self.port_1 = lambda : self(2)

        
    def update(self):
        self.source1_val = self.source1()
        self.source2_val = self.source2()

    def cycle(self):
        addr = self.source3()
        val = self.source4()
        i = to_dec(addr)
        if i == 0:
            return
        self.mem[i] = val
    def __call__(self, i):
        s = to_dec(getattr(self, 'source{}_val'.format(i)))
        return self.mem[s]

class ALU(component):
    def __init__(self, csource, csource_extra, dsource, acc_source):
        super().__init__()
        self.csource = csource
        self.csource_extra = csource_extra
        self.dsource = dsource
        self.acc_source = acc_source
        self.csource_val = np.zeros(3)
        self.csource_extra_val = np.zeros(2)
        self.dsource_val = np.zeros(8)
        self.acc_source_val = np.zeros(8)
        self.acc_port = lambda : self(0)
        self.skip_port = lambda : self(1)

        self.acc_lookup = {
            str([0, 0, 0]) : lambda x, y, acc : to_bin(x + y),
            str([0, 0, 1]) : lambda x, y, acc : to_bin(x - y),
            str([0, 1, 0]) : lambda x, y, acc : to_bin(x * y),
            str([0, 1, 1]) : lambda x, y, acc : to_bin(x % y),
            str([1, 0, 0]) : lambda x, y, acc : to_bin((a >> (256 - d))) if d > 7 else to_bin(a << d),
            str([1, 0, 1]) : lambda x, y, acc : to_bin(x & y),
            str([1, 1, 0]) : lambda x, y, acc : acc,
            str([1, 1, 1]) : lambda x, y, acc : acc
        }

    def update(self):
        self.csource_val = self.csource()
        self.csource_extra_val = self.csource_extra()
        self.dsource_val = self.dsource()
        self.acc_source_val = self.acc_source()
    def __call__(self, i):
        control = list(self.csource_val)
        control_extra = list(self.csource_extra_val)
        acc = self.acc_source_val
        data = self.dsource_val
      #  print(control)
        a = to_dec(acc)
        d = to_dec(data)

        if(i == 0):
            if 1 in control_extra:
                if control_extra[1]:
                    a = to_dec(acc)
                    d = to_dec(data)
                    return to_bin(a // d)
                if control_extra[0]:
                    a = to_dec(acc)
                    d = to_dec(data)
                    return to_bin(int(a ** (d / 10.0)))
            elif str(control) in self.acc_lookup:
                return self.acc_lookup[str(control)](a, d, acc)
            else:
                raise Exception('Invalid Control')
            
        elif(i == 1):
            if 1 in control_extra:
                return np.zeros(8)
            elif(control == [1, 1, 0]):
                a = to_dec(acc)
                d = to_dec(data)
               
                if d == 0:
                    return to_bin(1) if a == 0 else np.zeros(8)
                elif d < 128:
                    return to_bin(1) if a <= 0xf and a > 0 else np.zeros(8)
                elif d < 256 and d >= 128:
                    return to_bin(1) if a <= 0xff and a > 0 else np.zeros(8)
                else:
                    raise Exception('Invalid Data') 

                    
            elif control == [1, 1, 1]: 
                return data
            else:
                return np.zeros(8) 
            
class minecraft_machine:
    def __init__(self, randomized = True):
        self.PC = register(np.zeros(8))
        self.ACC = register(np.zeros(8))
        self.Instruction_Memory = instruction_memory(source = None, randomized = randomized)
        self.Instruction_Register = instruction_buffer(source = None)
        self.control = control(opcode_s = None, ALU_s = None)
        self.im_demux = demux(dsource = None, csource = None)
        self.ls_ret_demux = demux(dsource = None, csource = None)
        self.fmux = demux(dsource = None, csource = None, port_r = [[0,0], [0,1], [1,1]])
        self.ALU = ALU(csource = None, csource_extra = None, dsource = None, acc_source = None)
        self.Main_Memory = main_mem(source1 = None, source2 = None, source3 = None, source4 = None, randomized = randomized)
        self.add1 = binary_op(source1 = None, source2 = lambda : to_bin(1), function = lambda x, y : to_bin(to_dec(x) + to_dec(y)))
        self.adder = binary_op(source1 = None, source2 = None, function = lambda x, y : to_bin(to_dec(x) + to_dec(y)))
        self.store_merge = binary_op(source1 = None, source2 = None, function = lambda x, y : x | y)
        self.ALU_merge1 = binary_op(source1 = None, source2 = None, function = lambda x, y : x | y)
        self.ALU_merge2 = binary_op(source1 = None, source2 = None, function = lambda x, y : x | y)

        self.PC_port = wire(self.PC)
        self.ACC_port = wire(self.ACC)
        self.Instruction_Memory_port = wire(self.Instruction_Memory, width = 13)
        self.Instruction_Register_port_opcode = wire(self.Instruction_Register.port_opcode, width = 2)
        self.Instruction_Register_port_ALU = wire(self.Instruction_Register.port_ALU, width = 3)
        self.Instruction_Register_port_Data = wire(self.Instruction_Register.port_Data)
        self.control_port_0 = wire(self.control.port_0, width = 1)
        self.control_port_1 = wire(self.control.port_1, width = 1)
        self.control_port_2 = wire(self.control.port_2, width = 2)
        self.control_port_3 = wire(self.control.port_3, width = 2)
        self.im_demux_port_0 = wire(self.im_demux.port_0)
        self.im_demux_port_1 = wire(self.im_demux.port_1)
        self.ls_ret_demux_port_0 = wire(self.ls_ret_demux.port_0)
        self.ls_ret_demux_port_1 = wire(self.ls_ret_demux.port_1)
        self.fmux_port_0 = wire(self.fmux.port_0)
        self.fmux_port_1 = wire(self.fmux.port_1)
        self.fmux_port_2 = wire(self.fmux.port_2)
        self.ALU_port_acc = wire(self.ALU.acc_port)
        self.ALU_port_skip = wire(self.ALU.skip_port)
        self.Main_Memory_port_0 = wire(self.Main_Memory.port_0)
        self.Main_Memory_port_1 = wire(self.Main_Memory.port_1)
        self.add1_port = wire(self.add1)
        self.adder_port = wire(self.adder)
        self.store_merge_port = wire(self.store_merge)
        self.ALU_merge1_port = wire(self.ALU_merge1)
        self.ALU_merge2_port = wire(self.ALU_merge2)

        self.PC.source = self.adder_port
        self.ACC.source = self.ALU_port_acc
        self.Instruction_Memory.source = self.PC_port
        self.Instruction_Register.source = self.Instruction_Memory_port
        self.control.ALU_s = self.Instruction_Register_port_ALU
        self.control.opcode_s = self.Instruction_Register_port_opcode
        self.im_demux.dsource = self.Instruction_Register_port_Data
        self.im_demux.csource = self.control_port_0
        self.ls_ret_demux.dsource = self.im_demux_port_0
        self.ls_ret_demux.csource = self.control_port_1
        self.fmux.dsource = self.Main_Memory_port_0
        self.fmux.csource = self.control.port_2
        self.ALU.csource = self.Instruction_Register_port_ALU
        self.ALU.csource_extra = self.control.port_3
        self.ALU.dsource = self.ALU_merge2_port
        self.ALU.acc_source = self.ACC_port
        self.Main_Memory.source1 = self.ls_ret_demux_port_0
        self.Main_Memory.source2 = self.fmux_port_1
        self.Main_Memory.source3 = self.store_merge_port
        self.Main_Memory.source4 = self.ACC_port
        self.add1.source1 = self.ALU_port_skip
        self.adder.source1 = self.PC_port
        self.adder.source2 = self.add1_port
        self.store_merge.source1 = self.ls_ret_demux_port_1
        self.store_merge.source2 = self.fmux_port_2
        self.ALU_merge1.source1 = self.fmux_port_0
        self.ALU_merge1.source2 = self.Main_Memory_port_1
        self.ALU_merge2.source1 = self.ALU_merge1_port
        self.ALU_merge2.source2 = self.im_demux_port_1


    def __str__(self):
        return 'Acc {}\nPC {}\nIR {}'.format(str(self.ACC), str(self.PC), str(self.Instruction_Register))

    def _update(self):
        for attr in dir(self):
            f = getattr(self, attr)

            if(not issubclass(type(f), component)):
                continue
            f.update()



    def cycle(self):
        for i in range(3):
            #print('instruction_mem:', self.Instruction_Memory_port())
            self._update()
        self.PC.cycle()
        self.Instruction_Register.cycle()
        self.ACC.cycle()
        self.Main_Memory.cycle()

    def load_instructions(self, instructions):
        self.Instruction_Memory.mem[:len(instructions)] = instructions

def print_mem(config, mcm):
    for i in mcm.Main_Memory.mem[config.lb : config.ub]:
        if config.print_dec:
            print(to_dec(i), end =' ')
        if config.print_bin:
            print(i, end = ' ')
        print()    

def main(config):
    with open(config.assembly, 'r') as assembly:
        try:
            instructions, breakpoints = assemble(assembly, config.breakpoints)
        except AssemblyException as e:
            print(e)
            exit()
    mcm = minecraft_machine(randomized = False)
    mcm.load_instructions(instructions)



    for j in myrange(config.num_cycles):
        try:
            if to_dec(mcm.PC.pc) in breakpoints:
                if not config.nb:
                    print()
                    print('cycle', j)
                    print(mcm)
                    print_mem(config, mcm)
                    input()
            mcm.cycle()
            if config.verbose:
                print('cycle', j)
                print(mcm)
                print_mem(config, mcm)
                input()
        except IndexError as e:
            print()
            print('cycle', j)
            print('Memory contents')
            print_mem(config, mcm)
            print(e)
            exit()
    print_mem(config, mcm)
      
if __name__ == "__main__":
    from assembler import assemble, AssemblyException
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description= 'Simulate CPU')
    parser.add_argument('assembly', type = str, help = 'path to assembly file to run')
    parser.add_argument('-lb','--lower_bound', dest = 'lb', default = 0,type = int, help = 'lower bound on memory to print')
    parser.add_argument('-ub','--upper_bound', dest = 'ub',default = 20,type = int, help = 'upper bound on memory to print')
    parser.add_argument('-nc', '--num_cycles', dest = 'num_cycles', default = 296, type = int, help = 'number of cycles to run simulation for')
    parser.add_argument('-rd', '--rm_dec', dest = 'print_dec', action = 'store_false', help = 'whether it prints memory in decimal')
    parser.add_argument('-pb', '--print_bin', dest = 'print_bin', action = 'store_true', help = 'whether it prints memory in binary')
    parser.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true' )
    parser.add_argument('-bp', '--breakpoint',default = [], dest = 'breakpoints', nargs = '+', type = int, help = 'Line numbers to set a break poinnt at' )
    parser.add_argument('-nb', '--no_breakpoint', dest = 'nb', action = 'store_true' )
    config = parser.parse_args()
    if not config.verbose:
        from tqdm import trange as myrange 
    else:
        myrange = range
    main(config)
import numpy as np
import assembler as ass
import sys
class component:
    def __init__(self, source):
        self.source = source
    def update(self):
        pass
    def __call__(self):
        return self.source()

class instruction_memory(component):
    def __init__(self,source, word_size = 13, num_words = 256, mem = None):
        if mem is None:
            self.mem = np.zeros(word_size * num_words, dtype = int).reshape(num_words, word_size)
        else:
            self.mem = mem 
        self.source = source

    def __call__(self):
        s = np.sum(self.source() * 2**(7 - np.arange(8) ))
        return self.mem[s]

class register(component):
    def __init__(self, pc = None, source = None):
        self.pc = pc
        self.source = source
    def cycle(self):
        self.pc[:] = self.source()[:]
    def __call__(self):
        return self.pc[:]
    def __str__(self):
        return '{}'.format(self.pc)

class merge(component):
    def __init__(self, source1, source2):
        self.source1 = source1
        self.source2 = source2
    def __call__(self):
        return self.source1() + self.source2()

class wire(component):
    def __init__(self,source,width = 8, length = 1):
        self.length = length
        self.width = width
        self.w = np.zeros(length*width, dtype = int).reshape(length, width)
        self.source = source
    def update(self):
        
        x = self.source()

        self.w[:self.length-1] = self.w[1:] 
        self.w[self.length-1] = x
    def __call__(self):
        return self.w[0]

class instruction_buffer(component):
    def __init__(self, source):
        self.instr_b = np.zeros(13, dtype = int)
        self.IR = np.zeros(13, dtype = int)
        self.source = source

        
        port_names = ['Im', 'Ls_Ret',  'ALU', 'Data']


        for i in port_names:
            def f_cr(self, x):
                return lambda : self(x)
            setattr(self, 'port_{}'.format(i), f_cr(self, i))


    def update(self):
        self.instr_b = self.source()

    def cycle(self):
      #  self.IR[:] = self.instr_b[:]
        self.IR[:] = self.source()[:]

    def __call__(self, ptype):
  
            if(ptype is 'Im'):
                return self.IR[0]
            elif(ptype is 'Ls_Ret'):
                return self.IR[1:3]
            elif(ptype is 'ALU'):
                return self.IR[3:5]
            elif(ptype is 'Data'):
                return self.IR[5:]
            else:
                raise Exception('Invalid port')
    def __str__(self):
        return '{}'.format(self.IR)

    def __repr__(self):
        return str(self.instr_b) + str(self.IR)

class demux(component):
    def __init__(self, dsource, csource, port_r = None,num = 2, width = 8):
        self.csource = csource
        self.dsource = dsource
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

    def __call__(self, i):
        control = list(self.csource())

        if(type(i) is not list):
            i = [i]

        if(i == control):
            return self.dsource()
        else:
            return np.zeros(self.width)
class gate1(component):
    def __init__(self, source):
        self.source = source
    def __call__(self):
        s = self.source()
        ls = s[0]
        ret = s[1]
        return (ls ^ ret) & ls
class store_c(component):
    def __init__(self, source, acc_source):
        self.source = source
        self.acc_source = acc_source
    def __call__(self):
        x = np.append(self.source(), self.acc_source())
        return x

class load_c(component):
    def __init__(self, addr_source, data_source = None):
        self.addr_source = addr_source
        self.data_source = data_source
        self.port_0 = lambda : self(0)
        self.port_1 = lambda : self(1)
    def __call__(self, i):
        if(i == 0):
            return self.addr_source()
        elif(i == 1):
            return self.data_source()

def to_dec(b):
    return np.sum(b * 2**(7 - np.arange(8) ))
def to_bin(d, w_len = 8):
  #  print(d)
    try:
        b = [int(x) for x in list('{0:0b}'.format(d))]
    except:
        return np.zeros(8)
    l = np.arange(len(b)) + (w_len - len(b))
    x = np.empty(w_len, dtype = int)
    x[l] = b
    return x

class main_mem(component):
    def __init__(self, source1, source2, source3):
        self.source1 = source1
        self.source2 = source2
        self.source3 = source3
        self.mem = np.zeros(8*256).reshape(256, 8)
        self.port_0 = lambda : self(0)
        self.port_1 = lambda : self(1)
    def update(self):
        s = self.source3()
        i = to_dec(s[0:8])
        if i == 0:
            return
        self.mem[i] = s[8:16]
    def __call__(self, i):
        if(i == 0):
            s = np.sum(self.source1() * 2**(7 - np.arange(8) ))
            return self.mem[s]
        if(i == 1):
            s = np.sum(self.source2() * 2**(7 - np.arange(8) ))
            return self.mem[s]

class adder(component):
    def __init__(self, source1, source2 = lambda : np.array([0,0,0,0,0,0,0,1]) ):
        self.source1 = source1
        self.source2 = source2
    def __call__(self):
      #  print(self.source1, self.source2)
        s1 = to_dec(self.source1())
        s2 = to_dec(self.source2())
        b = to_bin(s1 + s2)

        return b

class ALU(component):
    def __init__(self, csource, dsource, acc_source):
        self.csource = csource
        self.dsource = dsource
        self.acc_source = acc_source
        self.acc_port = lambda : self(0)
        self.skip_port = lambda : self(1)
    def __call__(self, i):
        control = list(self.csource())
       
        acc = self.acc_source()
        data = self.dsource()
        if(i == 0):
            #print(control)
            if(control == [0, 0]):
               # print('data', data)
                a = to_dec(acc)
                d = to_dec(data)
                return to_bin(a + d)
            elif(control == [0, 1]):
                a = to_dec(acc)
                d = to_dec(data)
               # print(a, d)
                return to_bin(a - d)
            elif(control == [1, 0]):
                return acc
            elif(control == [1, 1]):
                return np.zeros(8)
            else:
                raise Exception('Invalid control')
        elif(i == 1):
            if(control == [1, 0]):
                s = np.sum(acc)
                if(s):
                    return data
                else:
                    return np.zeros(8)
            else:
                return np.zeros(8)
            
class minecraft_machine:
    def __init__(self):
        self.PC = register(np.zeros(8))
        self.ACC = register(np.zeros(8))

        self.mm = main_mem(None, None, None)
        self.IR = instruction_buffer(source = None)


        self.instr_mem = instruction_memory(source = None)
        self.PC2add1_wire = wire(self.PC)
        self.PC_add_1 = adder(source1 = self.PC2add1_wire)
        self.add12skip_wire = wire(self.PC_add_1)

        self.pc2instr_wire = wire(self.PC)
        self.instr_mem.source = self.pc2instr_wire

        self.instr2IR_wire = wire(self.instr_mem, width = 13)
        self.IR.source = self.instr2IR_wire

        self.im_wire = wire(self.IR.port_Im, width = 1)
        self.ls_ret1_wire = wire(self.IR.port_Ls_Ret, width = 2)
        self.ls_ret2_wire = wire(self.IR.port_Ls_Ret, width = 2)
        self.ALU_wire = wire(self.IR.port_ALU, width = 2)
        self.data_wire = wire(self.IR.port_Data, width = 8)

        self.im_demux = demux(dsource = self.data_wire, csource = self.im_wire)
        self.im2ALU_wire = wire(self.im_demux.port_1)
        self.im2LS_wire = wire(self.im_demux.port_0)

        self.gate = gate1(self.ls_ret1_wire)
        self.gate2mux_wire = wire(self.gate, width = 1)

        self.ls_mux = demux(dsource = self.im2LS_wire, csource = self.gate2mux_wire)

        self.ls_mux2load_wire = wire(self.ls_mux.port_0)
        self.ls_mux2store_wire = wire(self.ls_mux.port_1)

       # self.load1 = load_c(addr_source = self.ls_mux2load_wire)
       # self.load1mm_wire = (self.load1.port_0)
       # self.mm.source1 = self.load1mm_wire
        self.mm.source1 = self.ls_mux2load_wire

        self.mm2load1_wire = wire(self.mm.port_0)
      #  self.load1.data_source = self.mm2load1_wire
      #  self.load12demux_wire = self.load1.port_1

     #   self.fmux = demux(dsource = self.load12demux_wire, csource = self.ls_ret2_wire, port_r = [[0,0], [0,1], [1,1]])
        self.fmux = demux(dsource = self.mm2load1_wire, csource = self.ls_ret2_wire, port_r = [[0,0], [0,1], [1,1]])
        self.fmux2store_wire = wire(self.fmux.port_2)
      
        self.store_merge = merge(self.fmux2store_wire, self.ls_mux2store_wire)
        self.storemerge2Store_wire = wire(self.store_merge)
        self.Acc2Store_wire = wire(self.ACC)
        self.store = store_c(source = self.storemerge2Store_wire, acc_source = self.Acc2Store_wire)
        self.store2mm_wire = wire(self.store, width = 16)
        self.mm.source3 = self.store2mm_wire

        self.fmux2load2_wire = self.fmux.port_1

        self.mm2load2_wire = wire(self.mm.port_1)
        self.load2 = load_c(addr_source = self.fmux2load2_wire, data_source=self.mm2load2_wire)
        self.load22mm_wire = wire(self.load2.port_0)
        self.mm.source2 = self.load22mm_wire

        self.load22alu_wire = wire(self.load2.port_1)
        self.fmux2alu_wire = wire(self.fmux.port_0)
        self.fmerge = merge(self.load22alu_wire, self.fmux2alu_wire)
        self.fmerge2ALU_wire = wire(self.fmerge)
        self.fmerge_22ALU = merge(self.fmerge2ALU_wire, self.im2ALU_wire)
        
        self.toALU_wire = wire(self.fmerge_22ALU)

        self.acc2ALU_wire = wire(self.ACC)
        self.ALU = ALU(csource = self.ALU_wire, dsource = self.toALU_wire, acc_source = self.acc2ALU_wire)
        self.ALU2ACC_wire = wire(self.ALU.acc_port)
        self.ACC.source = self.ALU2ACC_wire
        self.ALU2PC_wire = wire(self.ALU.skip_port)

        self.skip_adder = adder(self.add12skip_wire, self.ALU2PC_wire)
        self.skip2PC_wire = wire(self.skip_adder)
        self.PC.source = self.skip2PC_wire



    def __str__(self):
        return 'Acc {}\nPC {}\nIR {}'.format(str(self.ACC), str(self.PC), str(self.IR))

    def update(self):
        for attr in dir(self):
            f = getattr(self, attr)

            if(not issubclass(type(f), component)):
                continue
            f.update()


    def cycle(self):
        self.PC.cycle()
        self.IR.cycle()
        self.ACC.cycle()

def main():

    with open(sys.argv[1], 'r') as assembly:
        instructions = ass.assemble(assembly)
        
    mcm = minecraft_machine()
    mcm.instr_mem.mem[:len(instructions)] = instructions[:]
    num_iter = 12
    for j in range(25*num_iter):
        for i in range(6):
            mcm.update()
        mcm.cycle()
    for i in mcm.mm.mem[int(sys.argv[2]):int(sys.argv[3])]:
        print(to_dec(i))
    
 

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print('must include assembly file and memory range')
        exit()
    main()
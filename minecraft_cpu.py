from cpu_components import *
from itertools import product

class minecraft_machine(machine):
    def __init__(self, randomized = True, num_ticks = 30):
        super().__init__(num_ticks)
        lookup_table = {}
        bin_3 = list(product([0, 1], repeat = 3))
        for b in bin_3:
            lookup_table[str([0, 0] + list(b))] = [[1], [0], [0, 0], [0, 0]]
        for b in bin_3:
            lookup_table[str([0, 1] + list(b))] = [[0], [0], [0, 0], [0, 0]]
        for b in bin_3:
            lookup_table[str([1, 0] + list(b))] = [[0], [0], [0, 1], [0, 0]]
                
        lookup_table[str([1, 1, 0, 0, 0])] = [[0], [0], [1, 1], [0, 0]]
        lookup_table[str([1, 1, 0, 0, 1])] = [[0], [1], [1, 0], [0, 0]]
        lookup_table[str([1, 1, 0, 1, 0])] = [[1], [0], [0, 0], [0, 1]]
        lookup_table[str([1, 1, 0, 1, 1])] = [[0], [0], [0, 0], [0, 1]]
        lookup_table[str([1, 1, 1, 0, 0])] = [[0], [0], [0, 1], [0, 1]]
        lookup_table[str([1, 1, 1, 0, 1])] = [[1], [0], [0, 0], [1, 0]]
        lookup_table[str([1, 1, 1, 1, 0])] = [[0], [0], [0, 0], [1, 0]]
        lookup_table[str([1, 1, 1, 1, 1])] = [[0], [0], [0, 1], [1, 0]]

        self.PC = register()
        self.ACC = register()
        self.Instruction_Memory = memory(source_names = ['source'], word_len = 13, randomized = randomized, port_widths = (13,))
        self.Instruction_Register = register(width = 13, port_widths = (13,))
        self.Instruction_Splitter = splitter(source_names = ['source'], 
                                            source_widths = (13,), 
                                            port_names = ['opcode', 'ALU', 'Data'],
                                            port_ranges = [(0, 2), (2, 5), (5, 13)],
                                            port_widths = (2, 3, 8))
        self.control = control(source_names=['opcode_s','ALU_s'], source_widths=(2, 3), num_ports = 4, lookup_table = lookup_table, port_widths = (1, 1, 2, 2))
        self.im_demux = demux(source_names = ['dsource', 'csource'], source_widths = (8, 1), num_ports = 2)
        self.ls_ret_demux = demux(source_names = ['dsource', 'csource'], source_widths = (8, 1), num_ports = 2)
        self.fmux = demux(source_names = ['dsource', 'csource'], source_widths = (8, 2), port_args = [[0,0], [0,1], [1,1]])
        self.ALU = ALU(source_names = ['acc_source', 'dsource', 'csource', 'csource_extra'], 
                    source_widths = (8, 8, 3, 2), port_names = ['acc', 'skip'])
        self.Main_Memory = memory(source_names = ['source0', 'source1'], num_ports= 2, randomized=randomized)
        self.add1 = binary_op(source_names = ['source1', 'source2'], sources = (None, to_bin(1)),fun = int.__add__)
        self.adder = binary_op(source_names = ['source1', 'source2'],fun= int.__add__)
        self.store_merge = binary_op(source_names = ['source1', 'source2'],fun= int.__or__)
        self.ALU_merge1 = binary_op(source_names = ['source1', 'source2'],fun= int.__or__)
        self.ALU_merge2 = binary_op(source_names = ['source1', 'source2'],fun= int.__or__)

        self.PC_port1 = wire(self.PC.port_0)
        self.PC_port2 = wire(self.PC.port_0)
        self.ACC_port1 = wire(self.ACC.port_0)
        self.ACC_port2 = wire(self.ACC.port_0)
        self.Instruction_Memory_port = wire(self.Instruction_Memory.port_0, width = 13)
        self.Instruction_Register_port = wire(self.Instruction_Register.port_0, width = 13)
        self.Instruction_Register_port_opcode = wire(self.Instruction_Splitter.port_opcode, width = 2)
        self.Instruction_Register_port_ALU1 = wire(self.Instruction_Splitter.port_ALU, width = 3)
        self.Instruction_Register_port_ALU2 = wire(self.Instruction_Splitter.port_ALU, width = 3)
        self.Instruction_Register_port_Data = wire(self.Instruction_Splitter.port_Data)
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
        self.ALU_port_acc = wire(self.ALU.port_acc)
        self.ALU_port_skip = wire(self.ALU.port_skip)
        self.Main_Memory_port_0 = wire(self.Main_Memory.port_0)
        self.Main_Memory_port_1 = wire(self.Main_Memory.port_1)
        self.add1_port = wire(self.add1.port_0)
        self.adder_port = wire(self.adder.port_0)
        self.store_merge_port = wire(self.store_merge.port_0)
        self.ALU_merge1_port = wire(self.ALU_merge1.port_0)
        self.ALU_merge2_port = wire(self.ALU_merge2.port_0)

        self.PC.source = self.adder_port.port_0
        self.ACC.source = self.ALU_port_acc.port_0
        self.Instruction_Memory.source = self.PC_port1.port_0
        self.Instruction_Register.source = self.Instruction_Memory_port.port_0
        self.Instruction_Splitter.source = self.Instruction_Register_port.port_0
        self.control.ALU_s = self.Instruction_Register_port_ALU1.port_0
        self.control.opcode_s = self.Instruction_Register_port_opcode.port_0
        self.im_demux.dsource = self.Instruction_Register_port_Data.port_0
        self.im_demux.csource = self.control_port_0.port_0
        self.ls_ret_demux.dsource = self.im_demux_port_0.port_0
        self.ls_ret_demux.csource = self.control_port_1.port_0
        self.fmux.dsource = self.Main_Memory_port_0.port_0
        self.fmux.csource = self.control_port_2.port_0
        self.ALU.csource = self.Instruction_Register_port_ALU2.port_0
        self.ALU.csource_extra = self.control_port_3.port_0
        self.ALU.dsource = self.ALU_merge2_port.port_0
        self.ALU.acc_source = self.ACC_port1.port_0
        self.Main_Memory.source0 = self.ls_ret_demux_port_0.port_0
        self.Main_Memory.source1 = self.fmux_port_1.port_0
        self.Main_Memory.write_addr_s = self.store_merge_port.port_0
        self.Main_Memory.write_val_s = self.ACC_port2.port_0
        self.add1.source1 = self.ALU_port_skip.port_0
        self.adder.source1 = self.PC_port2.port_0
        self.adder.source2 = self.add1_port.port_0
        self.store_merge.source1 = self.ls_ret_demux_port_1.port_0
        self.store_merge.source2 = self.fmux_port_2.port_0
        self.ALU_merge1.source1 = self.fmux_port_0.port_0
        self.ALU_merge1.source2 = self.Main_Memory_port_1.port_0
        self.ALU_merge2.source1 = self.ALU_merge1_port.port_0
        self.ALU_merge2.source2 = self.im_demux_port_1.port_0
        
    def __str__(self):
        return 'Acc {}\nPC {}\nIR {}'.format(str(self.ACC), str(self.PC), str(self.Instruction_Register))

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
    mcm = minecraft_machine(randomized = False, num_ticks = config.num_ticks)
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
        except CPUException as e:
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
    parser.add_argument('-nt', '--num_ticks', dest = 'num_ticks', type = int, default = 30)
    config = parser.parse_args()
    if not config.verbose:
        from tqdm import trange as myrange 
    else:
        myrange = range
    main(config)
import numpy as np
from multiprocessing import Pool
class CPUException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return str(self.message)

def to_dec(b):
    width = len(b)
    return int(np.sum(b * 2**((width - 1) - np.arange(width) )))
def to_bin(d, w_len = 8):
    if d < 0:
        d = 256 + d
    b = [int(x) for x in list('{0:0b}'.format(d))]
    l = min(w_len, len(b))
    x = np.zeros(w_len, dtype = int)
    x[-l:] = b[-l:]
    return x

class component():
    def __init__(self, width = 8, source_names = None, source_widths = None, sources = None, 
                port_names = None, port_args = None, num_ports = 1, port_widths = None, **kwargs):
        self.__dict__ = {**self.__dict__, **kwargs}
        self.source_names = source_names
        self.width = width
        if sources is None:
            sources = [None]*len(source_names)
        if source_widths is None:
            source_widths = [8]*len(source_names)
        init_vals = [(s, np.zeros(i, dtype = int)) for s, i in zip(sources, source_widths)]
        update_dict = dict(zip(source_names, init_vals))
        self.update_list = update_dict.keys()
        for k in update_dict:
            source, init_val = update_dict[k]
            setattr(self, k + '_val', init_val)
            setattr(self, k + '_val_i', init_val)
            setattr(self, k, source)

        if port_names:
            port_args = range(len(port_names))
        elif port_args:
            port_names = range(len(port_args))
        else:
            port_names = range(num_ports)
            port_args  = range(num_ports)
        if not port_widths:
            port_widths = (self.width,)*len(port_names)
        if len(port_widths) != len(port_names):
            raise CPUException('Invalid port_widths') 
        self.port_args = port_args
        self.port_names = port_names   
        for name, width in zip(port_names,  port_widths):
        #    f_cr = lambda x: lambda : self(x)
            setattr(self, 'port_{}'.format(name), np.zeros(width))
    def update_i(self):
        for attr in self.update_list:
            self.__dict__[attr + '_val_i'][:] = getattr(self, attr)[:]
    def update(self):
        for attr in self.update_list:
            self.__dict__[attr + '_val'][:] = getattr(self, attr + '_val_i')[:]
    def cycle(self):
        pass

class control(component):
    def update(self):
        super().update()
        for port, i in zip(self.port_names, self.port_args):
            control_list = []
            for l in self.source_names:
                control_list += list(getattr(self, l + '_val'))
            if str(control_list) in self.lookup_table:
                self.__dict__['port_{}'.format(port)][:] = self.lookup_table[str(control_list)][i]
            else:
                raise CPUException('Invalid Control in control. Received {}'.format(control_list))
        
class register(component):
    def __init__(self, width = 8, source = None, **kwargs):
        self.pc = np.zeros(width)
        super().__init__(source_names=['source'], sources = [source], source_widths=(width,), **kwargs)
    def update_i(self):
        pass
    def update(self):
        for port, i in zip(self.port_names, self.port_args):
            self.__dict__['port_{}'.format(port)][:] = self.pc[:]
    def cycle(self):
        self.pc[:] = self.source[:]

    def __str__(self):
        return '{}'.format(self.pc)

class binary_op(component):
    def update(self):
        super().update()
        for port, i in zip(self.port_names, self.port_args):
            self.__dict__['port_{}'.format(port)][:] = to_bin(self.fun(to_dec(self.source1_val), to_dec(self.source2_val)))[:]

class wire(component):
    def __init__(self,source,width = 8, length = 1):
        self.length = length
        self.width = width
        self.w = np.zeros(length*width, dtype = int).reshape(length, width) 
        super().__init__(source_names=['source'], sources = [source], source_widths=(width,), port_widths=(width,))
    def update(self):
        super().update()
        for port, i in zip(self.port_names, self.port_args):
            self.w[:self.length-1] = self.w[1:] 
            self.w[self.length-1] = self.source_val[:]
            self.__dict__['port_{}'.format(port)][:] = self.w[0]


class splitter(component):
    def update(self):
        super().update()
        for port, i in zip(self.port_names, self.port_args):
            self.__dict__['port_{}'.format(port)][:] = self.source_val[self.port_ranges[i][0] : self.port_ranges[i][1]]

class demux(component):
    def update(self):
        super().update()
        for port, i in zip(self.port_names, self.port_args):
            control = list(self.csource_val)
            if(type(i) is not list):
                i = [i]
            if(i == control):
                self.__dict__['port_{}'.format(port)][:] = self.dsource_val[:]
            else:
                self.__dict__['port_{}'.format(port)][:] = np.zeros(self.width)[:]

class memory(component):
    def __init__(self, word_len = 8, addr_len = 8, write_addr_s = to_bin(0), write_val_s = to_bin(0), randomized = False, **kwargs):
        super().__init__(**kwargs)
        self.write_addr_s = write_addr_s
        self.write_val_s = write_val_s
        gen_f = np.random.rand if randomized else np.zeros
        self.mem = gen_f(word_len * (2 ** addr_len)).reshape(2**addr_len, word_len)
        self.mem = np.array(self.mem >= 0.5, dtype = int)
        self.mem[0] = np.zeros(word_len, dtype = int)

    def cycle(self):
        addr = self.write_addr_s
        val = self.write_val_s
        i = to_dec(addr)
        if i == 0:
            return
        self.mem[i] = val
    def update(self):
        super().update()
        for port, i in zip(self.port_names, self.port_args):
            s = to_dec(getattr(self, self.source_names[i] + '_val'))
            self.__dict__['port_{}'.format(port)][:] = self.mem[s]

class ALU(component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        super().update()
        for port, i in zip(self.port_names, self.port_args):
            control = list(self.csource_val)
            control_extra = list(self.csource_extra_val)
            acc = self.acc_source_val
            data = self.dsource_val
            a = to_dec(acc)
            d = to_dec(data)

            if(i == 0):
                if 1 in control_extra:
                    if control_extra[1]:
                        a = to_dec(acc)
                        d = to_dec(data)
                        self.__dict__['port_{}'.format(port)][:] = to_bin(a // d)
                    if control_extra[0]:
                        a = to_dec(acc)
                        d = to_dec(data)
                        self.__dict__['port_{}'.format(port)][:] = to_bin(int(a ** (d / 10.0)))
                elif str(control) in self.acc_lookup:
                    self.__dict__['port_{}'.format(port)][:] = self.acc_lookup[str(control)](a, d, acc)
                else:
                    raise CPUException('Invalid Control in ALU received {} for control_extra'.format(control_extra))
                
            elif(i == 1):
                if 1 in control_extra:
                    self.__dict__['port_{}'.format(port)][:] = np.zeros(8)
                elif(control == [1, 1, 0]):
                    a = to_dec(acc)
                    d = to_dec(data)
                
                    if d == 0:
                        self.__dict__['port_{}'.format(port)][:] = to_bin(1) if a == 0 else np.zeros(8)
                    elif d < 128:
                        self.__dict__['port_{}'.format(port)][:] = to_bin(1) if a <= 0xf and a > 0 else np.zeros(8)
                    elif d < 256 and d >= 128:
                        self.__dict__['port_{}'.format(port)][:] = to_bin(1) if a <= 0xff and a > 0 else np.zeros(8)
                    else:
                        raise CPUException('Invalid Data in ALU') 
                        
                elif control == [1, 1, 1]: 
                    self.__dict__['port_{}'.format(port)][:] = data
                else:
                    self.__dict__['port_{}'.format(port)][:] = np.zeros(8) 



def _call(args):
    C, obj, attr = args
    getattr(C, attr)(obj)

class machine():
    def __init__(self, num_ticks):
        self.num_ticks = num_ticks
        self.component_attributes = None

     #   self.num_comps = 0
    def _pseudo_update(self, fun):
        if self.component_attributes:
            for attr in self.component_attributes:
                getattr(attr, fun)()
            #print('here')
         #   with Pool(4) as p:
         #       p.map(_call, zip(self.component_class, self.component_attributes, [fun]*self.num_comps))
        else:
            self.component_attributes = [] 
            self.component_class = []        
            for attr in dir(self): 
                f = getattr(self, attr)
                if issubclass(type(f), component):
                    getattr(f, fun)()
                    self.component_attributes += [f]

         #   self.num_comps = len(self.component_attributes)
       
    def _update(self):
        
        self._pseudo_update('update_i')
        self._pseudo_update('update')
    
    def cycle(self):
        for i in range(self.num_ticks):
            self._update()


        self._pseudo_update('cycle')
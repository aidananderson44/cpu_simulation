# cpu_simulation

This project Simulates an original 8-bit CPU design. 
The CPU design is an accumulator cpu, which means there is only one register that is accesible to the programmer.
The simulation is done at a component level, where each component does a simple task such as logical operation or control lookup.
Each component is modeled as having one or more input streams, and one or more output streams. 
These streams are connected together to simulate the CPU. The contents of a component are updated in 3 different ways:
1. update_i: This tells each compoent to read the contents of their input buffer, and store it in a place only they can access.
1. update: This tells each component to update their output buffer.
1. cycle: For componets that do something special on a cycle.

These 3 operations allow for each individual operation to be done in parallel for each component. 
This pure python implementation does not take advantage of this property, however, [this c++ implementation](https://github.com/aidananderson44/c_cpu_simulation) 
of the project does.

The syntax for some operation o, and some integer x is simply: "o x".
Most operations o come in 3 variants:
1. o x means it will treat x as an address, and fetch the value at memory location x for the operation o.
1. oi x means it will treat x as a value for operation o.
1. oIndr x means it will treat x as an address to a pointer p in memory, and fetch the value at address p for the operation o.
A list of operations can be found below.

The included assembler also supports the assembler directives: 
1. DEFINE [Token] [Val]: This tells the assembler to replace every instace of [Token] with [Val].
1. STARTMACRO name arg1 arg2, ...: This creates a macro with an arbitrary number of arguments. Arguments inside of the macro must be surrounded by {}.
1. ENDMACRO: end the macro.



The following operations are supported
* addi : [0, 0, 0, 0, 0]
* add : [0, 1, 0, 0, 0]
* addIndr : [1, 0, 0, 0, 0]
* subi : [0, 0, 0, 0, 1]
* sub : [0, 1, 0, 0, 1]
* subIndr : [1, 0, 0, 0, 1]
* muli : [0, 0, 0, 1, 0]
* mul : [0, 1, 0, 1, 0]
* mulIndr : [1, 0, 0, 1, 0]
* modi : [0, 0, 0, 1, 1]
* mod : [0, 1, 0, 1, 1]
* modIndr : [1, 0, 0, 1, 1]
* lsli : [0, 0, 1, 0, 0]
* lsl : [0, 1, 1, 0, 0]
* lslIndr : [1, 0, 1, 0, 0]
* andi : [0, 0, 1, 0, 1]
* and : [0, 1, 1, 0, 1]
* andIndr : [1, 0, 1, 0, 1]
* skipCondi : [0, 0, 1, 1, 0]
* skipCond : [0, 1, 1, 1, 0]
* skipCondIndr : [1, 0, 1, 1, 0]
* jmpi : [0, 0, 1, 1, 1]
* jmp : [0, 1, 1, 1, 1]
* jmpIndr : [1, 0, 1, 1, 1]
* store : [1, 1, 0, 0, 1]
* storeIndr : [1, 1, 0, 0, 0]
* clear : [0, 0, 0, 1, 0]
* divi : [1, 1, 0, 1, 0]
* div1 : [1, 1, 0, 1, 1]
* divIndr : [1, 1, 1, 0, 0]
* powi : [1, 1, 1, 0, 1]
* pow : [1, 1, 1, 1, 0]
* powIndr : [1, 1, 1, 1, 1]


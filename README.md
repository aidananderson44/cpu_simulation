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
1. BREAKPOINT: sets a breakpoint in the execution

The token PC is replaced by the current line number. Therefore, it is possible to make function calls. Consider the following:
~~~
STARTMACRO jal function ra
clear
addi PC + 4
store {ra}
jmpi {function} - PC
addi
ENDMACRO

STARTMACRO return ra
clear
load {ra}
addi -PC - 4
store j
jmp j
addi
ENDMACRO

jal FOO 1 #Jump and link. Jumps to foo, and links return address

DEFINE FOO PC #Function definition
# Do STUFF
return 1 #returns to return address at location 1
~~~

This code will store the address immediately following the jal call in memory location 1. 
Then the function foo will return to that address stored at location 1.

The assembler interprets everything written after the first token of each line as python code. 
The only included funtions are len, and dir. Therefore, the assembler will try to evaluate everything after the token
into an integer. If it does not receive an integer, then an assembler error will be thrown. 
This means operators such as +, -, *, \/\/ can be used as long as it statically evaluates to an integer. 
It also means that the assembler uses python's '#' comments character.

The following operations are supported
* addi         : 0x00
* add          : 0x08
* addIndr      : 0x10
* subi         : 0x01
* sub          : 0x09
* subIndr      : 0x11
* muli         : 0x02
* mul          : 0x0a
* mulIndr      : 0x12
* modi         : 0x03
* mod          : 0x0b
* modIndr      : 0x13
* lsli         : 0x04
* lsl          : 0x0c
* lslIndr      : 0x14
* andi         : 0x05
* and          : 0x0d
* andIndr      : 0x15
* skipCondi    : 0x06
* skipCond     : 0x0e
* skipCondIndr : 0x16
* jmpi         : 0x07
* jmp          : 0x0f
* jmpIndr      : 0x17
* store        : 0x19
* storeIndr    : 0x18
* clear        : 0x02
* divi         : 0x1a
* div1         : 0x1b
* divIndr      : 0x1c
* powi         : 0x1d
* pow          : 0x1e
* powIndr      : 0x1f


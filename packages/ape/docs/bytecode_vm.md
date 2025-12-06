# APE Bytecode Virtual Machine Documentation (v1.0.0)

**Author:** David Van Aelst  
**Status:** Scaffold - implementation pending  
**Version:** 1.0.0

---

## Overview

APE's bytecode virtual machine is a stack-based interpreter that executes compiled APE programs. It provides deterministic, sandboxed execution with full observability.

## Architecture

### Stack-Based Execution

The VM uses an operand stack for all operations:

```
Operation: 2 + 3

Bytecode:
  LOAD_CONST 2    # Stack: [2]
  LOAD_CONST 3    # Stack: [2, 3]
  ADD             # Stack: [5]
```

### Call Stack

Function calls maintain separate stack frames:

```
Frame Structure:
  - Local variables
  - Instruction pointer
  - Operand stack
  - Return address
```

## Instruction Set

### Constants

**LOAD_CONST** - Push constant onto stack
```
LOAD_CONST 42    # Stack: [..., 42]
```

**LOAD_NULL** - Push null onto stack
```
LOAD_NULL        # Stack: [..., null]
```

### Variables

**LOAD_VAR** - Load variable value
```
LOAD_VAR x       # Stack: [..., value_of_x]
```

**STORE_VAR** - Store value to variable
```
STORE_VAR x      # Pop top of stack, store in x
```

### Arithmetic

**ADD** - Addition
```
ADD              # Pop 2, push sum
```

**SUB** - Subtraction
```
SUB              # Pop b, pop a, push a - b
```

**MUL** - Multiplication
```
MUL              # Pop 2, push product
```

**DIV** - Division
```
DIV              # Pop divisor, pop dividend, push quotient
```

**MOD** - Modulo
```
MOD              # Pop divisor, pop dividend, push remainder
```

**NEG** - Negation
```
NEG              # Pop value, push -value
```

### Comparison

**EQ** - Equality
```
EQ               # Pop 2, push true if equal
```

**NE** - Inequality
```
NE               # Pop 2, push true if not equal
```

**LT, LE, GT, GE** - Comparisons
```
LT               # Pop b, pop a, push a < b
```

### Logical

**AND** - Logical AND
```
AND              # Pop 2, push logical AND result
```

**OR** - Logical OR
```
OR               # Pop 2, push logical OR result
```

**NOT** - Logical NOT
```
NOT              # Pop value, push logical negation
```

### Control Flow

**JUMP** - Unconditional jump
```
JUMP address     # Set instruction pointer to address
```

**JUMP_IF_FALSE** - Conditional jump
```
JUMP_IF_FALSE address  # Jump if top of stack is false
```

**JUMP_IF_TRUE** - Conditional jump
```
JUMP_IF_TRUE address   # Jump if top of stack is true
```

### Functions

**CALL** - Call function
```
CALL n_args      # Pop function and n_args arguments, call function
```

**RETURN** - Return from function
```
RETURN           # Return top of stack to caller
```

### Collections

**BUILD_LIST** - Build list
```
BUILD_LIST n     # Pop n items, push list
```

**BUILD_MAP** - Build map
```
BUILD_MAP n      # Pop n*2 items (key-value pairs), push map
```

**INDEX** - Index into collection
```
INDEX            # Pop index, pop collection, push collection[index]
```

### Stack Operations

**POP** - Discard top of stack
```
POP              # Remove top item
```

**DUP** - Duplicate top of stack
```
DUP              # Duplicate top item
```

**HALT** - Stop execution
```
HALT             # Terminate program
```

## Example Programs

### Simple Arithmetic

**Source:**
```ape
result = (2 + 3) * 4
```

**Bytecode:**
```
0  LOAD_CONST 2
1  LOAD_CONST 3
2  ADD
3  LOAD_CONST 4
4  MUL
5  STORE_VAR result
6  HALT
```

### Conditional Logic

**Source:**
```ape
if x > 10:
    result = "big"
else:
    result = "small"
```

**Bytecode:**
```
0  LOAD_VAR x
1  LOAD_CONST 10
2  GT
3  JUMP_IF_FALSE 7
4  LOAD_CONST "big"
5  STORE_VAR result
6  JUMP 9
7  LOAD_CONST "small"
8  STORE_VAR result
9  HALT
```

### Function Call

**Source:**
```ape
task add(a, b):
    return a + b

result = add(2, 3)
```

**Bytecode:**
```
# Function 'add' at address 0
0  LOAD_VAR a
1  LOAD_VAR b
2  ADD
3  RETURN

# Main program
4  LOAD_CONST add
5  LOAD_CONST 2
6  LOAD_CONST 3
7  CALL 2
8  STORE_VAR result
9  HALT
```

## Using the VM

### Basic Execution

```python
from ape.vm import VirtualMachine
from ape.compiler.bytecode import BytecodeProgram

# Create VM
vm = VirtualMachine()

# Execute bytecode
result = vm.execute(bytecode_program)
```

### Step Execution (Debugging)

```python
vm = VirtualMachine()

# Execute one instruction at a time
while vm.step():
    context = vm.get_context()
    print(f"Stack: {context.call_stack[-1].operand_stack}")
```

### Configuration

```python
# Set maximum call stack depth
vm = VirtualMachine(max_stack_depth=1000)
```

## Execution Guarantees

### Determinism

The VM guarantees deterministic execution:
- Same bytecode → same result
- No non-deterministic operations
- Predictable resource usage

### Sandboxing

The VM executes in a sandbox:
- No file system access (unless explicitly allowed)
- No network access (unless explicitly allowed)
- No system calls
- Controlled memory usage

### Error Handling

The VM catches and reports errors:
- Stack overflow
- Division by zero
- Index out of bounds
- Type errors

## Performance Characteristics

### Time Complexity

| Operation | Complexity |
|-----------|-----------|
| Arithmetic | O(1) |
| Variable access | O(1) |
| Function call | O(1) |
| List indexing | O(1) |
| Map lookup | O(1) average |

### Space Complexity

- **Stack frame**: O(local variables + operand stack depth)
- **Call stack**: O(call depth × frame size)
- **Heap**: O(allocated objects)

## Bytecode Format

### Binary Encoding

```
Instruction:
  [Opcode: 1 byte] [Arg: variable length]

Example:
  LOAD_CONST 42
  [0x01] [0x2A 0x00 0x00 0x00]  # 32-bit integer
```

### Disassembly

```python
from ape.compiler.bytecode import disassemble

# Get human-readable bytecode
assembly = disassemble(bytecode_program)
print(assembly)
```

## Debugging

### Execution Trace

```python
vm = VirtualMachine()

# Enable tracing
trace = []
while vm.step():
    context = vm.get_context()
    trace.append({
        'ip': context.call_stack[-1].instruction_pointer,
        'stack': context.call_stack[-1].operand_stack.copy()
    })
```

### Breakpoints

```python
# Execute until instruction pointer reaches address
while vm.step():
    context = vm.get_context()
    if context.call_stack[-1].instruction_pointer == breakpoint_address:
        print("Breakpoint hit")
        break
```

## Future Enhancements

Planned VM improvements:
- JIT compilation
- Register-based variant
- Parallel execution
- Native extension interface
- Hardware acceleration

---

**Note:** This feature is scaffolded in v1.0.0. Full implementation is planned for a future release.

# Control Flow in Ape

**Version:** v0.3.0  
**Status:** ✅ Implemented

## Overview

Ape supports three control flow constructs:

- **If/else if/else** - Conditional branching based on boolean expressions
- **While loops** - Repeated execution while a condition is true
- **For loops** - Iteration over collections (lists, ranges, etc.)

All control flow is executed by an **AST-based runtime** that operates without using Python's `exec()`, `eval()`, or `compile()`. This design ensures:

- **Deterministic execution** - Same input always produces same output
- **Sandbox safety** - No filesystem, network, or environment access
- **Iteration limits** - Configurable guards prevent infinite loops

## Syntax

### If/Else If/Else

```ape
if condition:
    - step1
    - step2
else if another_condition:
    - step3
else:
    - step4
```

**Rules:**
- Conditions must be boolean expressions
- Colon (`:`) is required after condition
- Steps must be indented
- `else if` and `else` are optional
- Multiple `else if` branches are allowed

**Example:**

```ape
module main

task classify_number:
    inputs:
        x: Integer
    outputs:
        result: String
    constraints:
        - deterministic
    steps:
        if x < 0:
            - set result to "negative"
        else if x == 0:
            - set result to "zero"
        else:
            - set result to "positive"
        - return result
```

### While Loops

```ape
while condition:
    - step1
    - step2
```

**Rules:**
- Condition is evaluated before each iteration
- Loop terminates when condition becomes false
- Iteration limit enforced (default: 10,000 iterations)
- Colon (`:`) required after condition
- Body must be indented

**Example:**

```ape
module main

task sum_to_n:
    inputs:
        n: Integer
    outputs:
        total: Integer
    constraints:
        - deterministic
    steps:
        - set count to 0
        - set total to 0
        
        while count < n:
            - set count to count + 1
            - set total to total + count
        
        - return total
```

### For Loops

```ape
for variable in iterable:
    - step1
    - step2
```

**Rules:**
- Iterator variable is scoped to the loop body
- Iterable can be a list, range, or other collection
- Iteration limit enforced (default: 10,000 iterations)
- Colon (`:`) required after iterator declaration
- Body must be indented

**Example:**

```ape
module main

task sum_list:
    inputs:
        numbers: List[Integer]
    outputs:
        total: Integer
    constraints:
        - deterministic
    steps:
        - set total to 0
        
        for num in numbers:
            - set total to total + num
        
        - return total
```

## Expressions

Control flow conditions and expressions support:

### Comparison Operators

| Operator | Meaning              | Example     |
|----------|----------------------|-------------|
| `<`      | Less than            | `x < 10`    |
| `>`      | Greater than         | `x > 0`     |
| `<=`     | Less than or equal   | `x <= 100`  |
| `>=`     | Greater than or equal| `x >= 5`    |
| `==`     | Equal to             | `x == 0`    |
| `!=`     | Not equal to         | `x != -1`   |

### Arithmetic Operators

| Operator | Meaning        | Example      |
|----------|----------------|--------------|
| `+`      | Addition       | `x + 1`      |
| `-`      | Subtraction    | `x - 1`      |
| `*`      | Multiplication | `x * 2`      |
| `/`      | Division       | `x / 2`      |
| `%`      | Modulo         | `x % 10`     |

### Logical Operators

| Operator | Meaning     | Example          |
|----------|-------------|------------------|
| `and`    | Logical AND | `x > 0 and x < 10` |
| `or`     | Logical OR  | `x < 0 or x > 10`  |
| `not`    | Logical NOT | `not x == 0`       |

### Expression Examples

```ape
# Comparison
if count < 10:
    - step

# Arithmetic in condition
if (x + y) > 100:
    - step

# Complex expression
if x * 2 >= y / 3:
    - step

# Logical operators
if x > 0 and x < 100:
    - step

if x == 0 or x == 1:
    - step
```

## Runtime Behavior

### Execution Model

Ape's runtime uses an **AST-based executor** that directly interprets the abstract syntax tree:

1. **Parse** - Source code → AST nodes (IfNode, WhileNode, ForNode)
2. **Execute** - AST nodes → runtime actions via ExecutionContext
3. **Evaluate** - Expressions → values using operator handlers

**No Python code is executed** during runtime. This provides complete control over:
- Variable scoping and lifetime
- Iteration limits and safety checks
- Deterministic behavior guarantees

### Variable Scoping

Variables follow lexical scoping rules:

```ape
steps:
    - set x to 10          # x in parent scope
    
    if x > 5:
        - set y to 20      # y in child scope
        - set x to 30      # updates parent x
    
    - call print with x    # x is 30
    - call print with y    # ERROR: y not in scope
```

**Rules:**
- Variables declared in parent scope are visible in child scopes
- Variables declared in child scope are not visible in parent scope
- Assignments in child scope update parent variables if they exist
- Loop iterator variables are scoped to the loop body

### Safety Guarantees

#### 1. Iteration Limits

All loops enforce a maximum iteration count (default: 10,000):

```ape
while true:  # Will raise MaxIterationsExceeded after 10,000 iterations
    - step
```

Configure limit:
```python
from ape.runtime import ExecutionContext, RuntimeExecutor

context = ExecutionContext(max_iterations=5000)
executor = RuntimeExecutor()
executor.execute(ast_node, context)
```

#### 2. No Side Effects

The runtime executor has **no access to**:
- Filesystem operations (no file reads/writes)
- Network operations (no HTTP requests)
- Environment variables
- System commands

This ensures:
- Deterministic execution
- Safe sandbox for untrusted code
- Reproducible results

#### 3. No Python Exec

The runtime **never uses**:
- `exec()` - Execute arbitrary Python code
- `eval()` - Evaluate Python expressions
- `compile()` - Compile Python code objects

All execution goes through controlled AST traversal.

### Determinism

Given the same inputs, Ape programs produce the same outputs:

```ape
task add_numbers:
    inputs:
        a: Integer
        b: Integer
    outputs:
        result: Integer
    constraints:
        - deterministic
    steps:
        if a > b:
            - set result to a + b
        else:
            - set result to b - a
        - return result
```

**Determinism guarantees:**
- Same input values → same execution path
- Same execution path → same output values
- No randomness, no timestamps, no external state

## Testing

Control flow implementation includes 20 comprehensive tests:

### Parsing Tests (5)
- If statements
- If-else statements
- If-elif-else statements
- While loops
- For loops

### Execution Tests (12)
- If branch execution
- Else branch execution
- While loop iteration
- For loop iteration
- Iteration limit enforcement
- Expression evaluation
- Nested scoping
- Variable updates

### Safety Tests (3)
- No exec/eval/compile verification
- Context isolation
- Deterministic behavior

Run tests:
```bash
python -m pytest tests/runtime/test_control_flow.py -v
```

## Implementation Details

### AST Nodes

**IfNode:**
```python
@dataclass
class IfNode:
    condition: Any
    body: List[Any]
    elif_blocks: List[Tuple[Any, List[Any]]]
    else_body: Optional[List[Any]]
```

**WhileNode:**
```python
@dataclass
class WhileNode:
    condition: Any
    body: List[Any]
```

**ForNode:**
```python
@dataclass
class ForNode:
    iterator: str
    iterable: Any
    body: List[Any]
```

### Runtime Executor

**Key methods:**

```python
class RuntimeExecutor:
    def execute(self, node: Any, context: ExecutionContext) -> Any:
        """Execute an AST node."""
        
    def execute_if(self, node: IfNode, context: ExecutionContext) -> None:
        """Execute if/elif/else branches."""
        
    def execute_while(self, node: WhileNode, context: ExecutionContext) -> None:
        """Execute while loop with iteration limit."""
        
    def execute_for(self, node: ForNode, context: ExecutionContext) -> None:
        """Execute for loop with iteration limit."""
        
    def evaluate_expression(self, expr: Any, context: ExecutionContext) -> Any:
        """Evaluate expression to a value."""
```

### Execution Context

```python
class ExecutionContext:
    def __init__(self, parent: Optional['ExecutionContext'] = None,
                 max_iterations: int = 10000):
        """Create execution context with optional parent scope."""
        
    def get(self, name: str) -> Any:
        """Get variable value, checking parent if not found."""
        
    def set(self, name: str, value: Any) -> None:
        """Set variable in current or parent scope."""
        
    def has(self, name: str) -> bool:
        """Check if variable exists in this or parent scope."""
        
    def create_child_scope(self) -> 'ExecutionContext':
        """Create child context inheriting from this one."""
```

## Future Enhancements

Planned improvements for future versions:

1. **Break/Continue** - Early loop termination
2. **Match/Case** - Pattern matching (Python 3.10+ style)
3. **Try/Except** - Exception handling
4. **List Comprehensions** - `[x * 2 for x in numbers if x > 0]`
5. **Optimizations** - Constant folding, loop unrolling
6. **Debugging** - Step-through execution, breakpoints

## See Also

- [Module System](modules_and_imports.md)
- [Standard Library](stdlib_v0.1.md)
- [Philosophy](philosophy.md)
- [APE Spec](../spec/APE_Spec_v0.1.md)

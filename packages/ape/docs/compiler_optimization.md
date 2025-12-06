# APE Compiler Optimization Documentation (v1.0.0)

**Author:** David Van Aelst  
**Status:** Scaffold - implementation pending  
**Version:** 1.0.0

---

## Overview

APE's compiler includes multiple optimization passes that transform the AST to improve runtime performance without changing program semantics.

## Optimization Passes

### Constant Folding

Evaluates constant expressions at compile time.

**Transformations:**
```
Before:  2 + 3
After:   5

Before:  "hello" + " " + "world"
After:   "hello world"

Before:  true and false
After:   false
```

**Benefits:**
- Eliminates runtime arithmetic
- Reduces instruction count
- Improves startup time

### Dead Code Elimination

Removes unreachable or unused code.

**Transformations:**
```ape
# Before
if true:
    process_data()
else:
    never_executed()

# After
process_data()
```

```ape
# Before
task example():
    unused_var = expensive_calculation()
    return 42

# After
task example():
    return 42
```

**Benefits:**
- Smaller bytecode size
- Faster execution
- Clearer compiled output

### Common Subexpression Elimination (CSE)

Identifies and eliminates redundant calculations.

**Transformation:**
```ape
# Before
a = b * c + d
e = b * c + f

# After
temp = b * c
a = temp + d
e = temp + f
```

**Benefits:**
- Reduces redundant computations
- Improves performance for complex expressions
- Better register/variable usage

### Loop Unrolling

Expands loops with known iteration counts.

**Transformation:**
```ape
# Before
for i in range(3):
    process(i)

# After
process(0)
process(1)
process(2)
```

**Benefits:**
- Eliminates loop overhead
- Better for small, fixed iterations
- Enables further optimizations

**Trade-offs:**
- Increases code size
- Only beneficial for small loops

### Tail Call Optimization (TCO)

Converts tail-recursive calls to iteration.

**Transformation:**
```ape
# Before (recursive)
task factorial(n: Integer, acc: Integer):
    if n == 0:
        return acc
    return factorial(n - 1, n * acc)

# After (iterative)
task factorial(n: Integer, acc: Integer):
    while n != 0:
        acc = n * acc
        n = n - 1
    return acc
```

**Benefits:**
- Prevents stack overflow
- Constant stack space usage
- Better performance for deep recursion

## Using the Optimizer

### Basic Usage

```python
from ape.compiler.optimizer import Optimizer, ConstantFolding, DeadCodeElimination

# Create optimizer
optimizer = Optimizer()

# Add optimization passes
optimizer.add_pass(ConstantFolding())
optimizer.add_pass(DeadCodeElimination())

# Run optimizer
optimized_ast = optimizer.run(ast)
```

### Optimization Levels

**Level 0: No Optimization**
- Fastest compilation
- No transformations
- Good for debugging

**Level 1: Basic Optimization**
- Constant folding
- Dead code elimination
- Minimal impact on compile time

**Level 2: Standard Optimization (Default)**
- All Level 1 passes
- Common subexpression elimination
- Loop unrolling for small loops
- Balanced performance/compile time

**Level 3: Aggressive Optimization**
- All Level 2 passes
- Tail call optimization
- Multiple optimization iterations
- Longer compile time

### Configuration

```python
from ape.compiler.pipeline import CompilationPipeline

# Disable optimization
pipeline = CompilationPipeline(optimize=False)

# Set optimization level
pipeline = CompilationPipeline(optimization_level=3)
```

## Optimization Safety

All optimizations preserve program semantics:
- Deterministic behavior maintained
- Side effects preserved
- Observable behavior unchanged
- Error conditions consistent

## Performance Impact

Typical performance improvements:

| Optimization | Typical Speedup |
|-------------|-----------------|
| Constant Folding | 5-10% |
| Dead Code Elimination | 2-5% |
| CSE | 10-20% |
| Loop Unrolling | 15-30% (small loops) |
| TCO | 2-5x (recursive algorithms) |

**Note:** Actual improvements depend on code characteristics.

## Debugging Optimized Code

### Disabling Optimizations

```python
# For debugging, disable optimizations
pipeline = CompilationPipeline(optimize=False)
```

### Viewing Optimization Log

```python
result = pipeline.compile(source)
for entry in result.optimization_log:
    print(entry)
```

### Source Mapping

Optimized bytecode maintains source mapping for debugging:

```python
# Get original source location from bytecode instruction
source_line = result.source_map[instruction.line]
```

## Custom Optimization Passes

### Creating Custom Pass

```python
from ape.compiler.optimizer import OptimizationPass, OptimizationResult

class MyOptimization(OptimizationPass):
    @property
    def name(self):
        return "My Custom Optimization"
    
    def optimize(self, ast):
        # Transform AST
        transformed_ast = transform(ast)
        
        return OptimizationResult(
            optimized_ast=transformed_ast,
            changes_made=True,
            description="Applied my optimization"
        )

# Use custom pass
optimizer = Optimizer()
optimizer.add_pass(MyOptimization())
```

## Best Practices

### 1. Use Default Optimization Level

The default (Level 2) provides good balance:
```python
pipeline = CompilationPipeline()  # Uses level 2
```

### 2. Profile Before Aggressive Optimization

```python
# Profile first
from ape.benchmarks import BenchmarkRunner
runner = BenchmarkRunner()
baseline = runner.benchmark("baseline", lambda: run_program())

# Then try level 3
pipeline_aggressive = CompilationPipeline(optimization_level=3)
```

### 3. Test Optimized Code

Always test that optimizations don't break functionality:
```python
# Run test suite on optimized code
result_optimized = pipeline.compile(source)
assert test_suite(result_optimized) == expected
```

## Future Enhancements

Planned optimizations:
- Inline expansion
- Partial evaluation
- Strength reduction
- Vectorization
- Profile-guided optimization

---

**Note:** This feature is scaffolded in v1.0.0. Full implementation is planned for a future release.

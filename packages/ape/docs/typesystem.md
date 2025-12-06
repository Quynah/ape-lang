# APE Type System Documentation (v1.0.0)

**Author:** David Van Aelst  
**Status:** Scaffold - implementation pending  
**Version:** 1.0.0

---

## Overview

APE provides a gradual type system with structured data types, generic type parameters, and type inference. The type system ensures safety while maintaining the simplicity of APE's natural language syntax.

## Structured Types

### List\<T>

Ordered, mutable collections with type constraints.

**Syntax:**
```ape
my_list: List<Integer> = [1, 2, 3, 4, 5]
names: List<String> = ["Alice", "Bob", "Charlie"]
```

**Operations:**
```ape
# Indexing
first_item = my_list[0]

# Length
count = my_list.length()

# Append
my_list.append(6)

# Iteration
for item in my_list:
    print(item)
```

**Methods:**
- `append(item: T)` - Add item to end
- `insert(index: Integer, item: T)` - Insert at position
- `remove(index: Integer)` - Remove by index
- `pop()` - Remove and return last item
- `length()` - Get number of items
- `contains(item: T)` - Check if item exists

### Map\<K, V>

Key-value mappings with type constraints.

**Syntax:**
```ape
scores: Map<String, Integer> = {
    "Alice": 100,
    "Bob": 95,
    "Charlie": 87
}
```

**Operations:**
```ape
# Get value
alice_score = scores["Alice"]

# Set value
scores.set("David", 92)

# Check key existence
if scores.has("Alice"):
    print("Alice's score: " + scores["Alice"])

# Iterate
for key in scores.keys():
    print(key + ": " + scores[key])
```

**Methods:**
- `set(key: K, value: V)` - Set key-value pair
- `get(key: K)` - Get value by key (raises KeyError if not found)
- `has(key: K)` - Check if key exists
- `remove(key: K)` - Remove key-value pair
- `keys()` - Get all keys
- `values()` - Get all values
- `items()` - Get key-value pairs

### Record

Named field structures (similar to structs or dataclasses).

**Syntax:**
```ape
record Person:
    name: String
    age: Integer
    email: String

record Point:
    x: Number
    y: Number
```

**Usage:**
```ape
person = Person(
    name="Alice",
    age=30,
    email="alice@example.com"
)

# Field access
print(person.name)
print(person.age)

# Field assignment
person.age = 31
```

**Features:**
- Named fields with type constraints
- Dot notation for field access
- Immutable by default (use `mutable record` for mutable)
- Automatic equality and hashing

### Tuple

Fixed-size heterogeneous collections.

**Syntax:**
```ape
point: Tuple<Integer, Integer> = (10, 20)
result: Tuple<String, Boolean, Integer> = ("success", true, 42)
```

**Operations:**
```ape
# Indexing
x = point[0]
y = point[1]

# Unpacking
(status, success, code) = result

# Length
size = len(result)
```

**Features:**
- Immutable (cannot modify after creation)
- Heterogeneous (different types per position)
- Fixed size determined at creation

## Type Annotations

### Variable Annotations

```ape
name: String = "Alice"
age: Integer = 30
scores: List<Integer> = [85, 90, 95]
```

### Task Parameter Annotations

```ape
task calculate_total(prices: List<Number>, tax_rate: Number):
    subtotal = sum(prices)
    total = subtotal * (1 + tax_rate)
    return total
```

### Return Type Annotations

```ape
task get_user(user_id: Integer) -> Map<String, String>:
    # Implementation
    return user_data
```

## Type Inference

APE infers types when not explicitly annotated:

```ape
# Type inferred as Integer
count = 10

# Type inferred as List<String>
names = ["Alice", "Bob", "Charlie"]

# Type inferred from expression
total = count * 2  # Integer
```

## Generic Type Parameters

### Single Type Parameter

```ape
task first_item(list: List<T>) -> T:
    return list[0]

# Usage
number = first_item([1, 2, 3])  # Returns Integer
name = first_item(["Alice", "Bob"])  # Returns String
```

### Multiple Type Parameters

```ape
task get_or_default(map: Map<K, V>, key: K, default: V) -> V:
    if map.has(key):
        return map[key]
    else:
        return default
```

## Type Constraints

### Not Null

```ape
name: String! = "Alice"  # Cannot be null
optional_name: String? = null  # Can be null
```

### Type Unions

```ape
result: Integer | String = 42
result = "error"  # Valid
```

### Numeric Types

```ape
count: Integer = 10
price: Number = 19.99  # Floating point
```

## Type Validation

Types are validated at runtime:

```ape
scores: List<Integer> = [85, 90, 95]
scores.append(100)  # OK
scores.append("invalid")  # Error: Type mismatch
```

## Type Compatibility

### Numeric Coercion

```ape
x: Number = 10  # Integer -> Number is allowed
y: Integer = 10.5  # Error: Number -> Integer requires explicit conversion
```

### Generic Covariance

```ape
integers: List<Integer> = [1, 2, 3]
numbers: List<Number> = integers  # OK (covariant)
```

## Examples

### Typed Data Processing

```ape
task process_orders(orders: List<Map<String, Any>>):
    results: List<String> = []
    
    for order in orders:
        order_id = order["id"]
        customer = order["customer"]
        results.append("Order " + order_id + " for " + customer)
    
    return results
```

### Generic Helper Functions

```ape
task map_list(list: List<T>, transform: Task<T -> U>) -> List<U>:
    results: List<U> = []
    for item in list:
        results.append(transform(item))
    return results
```

### Type-Safe Configuration

```ape
record DatabaseConfig:
    host: String
    port: Integer
    username: String
    password: String
    ssl_enabled: Boolean

task connect_database(config: DatabaseConfig):
    # Type-safe configuration access
    connection = create_connection(
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password
    )
    return connection
```

## Best Practices

### 1. Use Type Annotations for Public Interfaces

```ape
# Good
task calculate_tax(amount: Number, rate: Number) -> Number:
    return amount * rate

# Less clear
task calculate_tax(amount, rate):
    return amount * rate
```

### 2. Prefer Specific Types Over Generic

```ape
# Good
scores: List<Integer>

# Less specific
data: List<Any>
```

### 3. Use Records for Structured Data

```ape
# Good
record User:
    id: Integer
    name: String
    email: String

# Less structured
user: Map<String, Any>
```

### 4. Leverage Type Inference for Local Variables

```ape
# No need for explicit annotation (inferred as Integer)
count = 0
for item in items:
    count = count + 1
```

## Future Enhancements

Planned for future versions:
- Algebraic data types (Sum types)
- Pattern matching on types
- Type classes/traits
- Dependent types
- Refinement types

---

**Note:** This feature is scaffolded in v1.0.0. Full implementation is planned for a future release.

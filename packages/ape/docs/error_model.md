# APE Error Model Documentation (v1.0.0)

**Author:** David Van Aelst  
**Status:** Scaffold - implementation pending  
**Version:** 1.0.0

---

## Overview

The APE error model provides structured exception handling with `try`, `catch`, and `finally` constructs, allowing tasks and flows to gracefully handle errors and ensure cleanup operations.

## Syntax

### Try-Catch-Finally

```ape
try:
    risky_operation()
catch ErrorType as error_variable:
    handle_error(error_variable)
finally:
    cleanup()
```

### Basic Try-Catch

```ape
try:
    result = parse_data(input)
    return result
catch ParseError as e:
    log_error(e.message)
    return default_value()
```

### Multiple Catch Clauses

```ape
try:
    process_file(filename)
catch FileNotFoundError as e:
    print("File not found: " + filename)
catch PermissionError as e:
    print("Permission denied: " + filename)
catch Error as e:
    print("Unexpected error: " + e.message)
```

### Try-Finally (No Catch)

```ape
try:
    open_resource()
    use_resource()
finally:
    close_resource()
```

## Error Types

### Built-in Errors

- **Error** - Base error type, catches all errors
- **TypeError** - Type validation errors
- **ValueError** - Invalid value errors
- **IndexError** - List/tuple index out of bounds
- **KeyError** - Map key not found
- **ParseError** - Parsing/compilation errors

### User-Defined Errors

You can raise custom errors using the `raise` statement:

```ape
task validate_age(age: Integer):
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age unrealistically high")
    return age
```

## Error Objects

When catching an error, the error object provides:

- `message` - Error message string
- `type` - Error type name
- `line` - Line number where error occurred (if available)
- `context` - Additional context information

Example:

```ape
try:
    process_data(input)
catch Error as e:
    print("Error: " + e.message)
    print("Type: " + e.type)
    log_error(e)
```

## Error Propagation

Errors propagate up the call stack until caught:

```ape
task inner_operation():
    raise Error("Something went wrong")

task outer_operation():
    try:
        inner_operation()  # Error propagates here
    catch Error as e:
        print("Caught error from inner operation")
```

## Finally Block Semantics

The `finally` block **always executes**, regardless of:
- Whether an exception occurred
- Whether the exception was caught
- Whether a `return` statement was executed

```ape
task process_with_cleanup(filename: String):
    file = null
    try:
        file = open_file(filename)
        return process_file(file)
    catch FileError as e:
        log_error(e)
        return null
    finally:
        if file != null:
            close_file(file)  # Always executes
```

## Best Practices

### 1. Catch Specific Errors First

Place more specific error types before general ones:

```ape
try:
    operation()
catch SpecificError as e:
    # Handle specific error
catch Error as e:
    # Handle general error
```

### 2. Use Finally for Cleanup

Always use `finally` for resource cleanup:

```ape
try:
    resource = acquire_resource()
    use_resource(resource)
finally:
    release_resource(resource)
```

### 3. Provide Meaningful Error Messages

```ape
if input.length() == 0:
    raise ValueError("Input cannot be empty")
```

### 4. Don't Catch and Ignore

Avoid empty catch blocks:

```ape
# BAD
try:
    risky_operation()
catch Error as e:
    # Silent failure

# GOOD
try:
    risky_operation()
catch Error as e:
    log_error(e)
    notify_admin(e)
```

## Examples

### File Processing with Error Handling

```ape
task read_config_file(filename: String):
    try:
        content = read_file(filename)
        config = parse_json(content)
        return config
    catch FileNotFoundError as e:
        print("Config file not found, using defaults")
        return default_config()
    catch ParseError as e:
        raise Error("Invalid config file format: " + e.message)
```

### Transaction Pattern

```ape
task execute_transaction(operations: List<Operation>):
    transaction = begin_transaction()
    try:
        for operation in operations:
            execute_operation(operation)
        commit_transaction(transaction)
        return "success"
    catch Error as e:
        rollback_transaction(transaction)
        raise Error("Transaction failed: " + e.message)
```

### Nested Error Handling

```ape
task robust_process(data: List<String>):
    results = []
    for item in data:
        try:
            result = process_item(item)
            results.append(result)
        catch ProcessError as e:
            print("Failed to process item: " + item)
            results.append(null)
    return results
```

## Integration with Types

Error handling works seamlessly with structured types:

```ape
task safe_list_access(list: List<Integer>, index: Integer):
    try:
        return list[index]
    catch IndexError as e:
        return 0  # Return default value
```

## Future Enhancements

Planned for future versions:
- Stack trace information
- Error chaining (caused by)
- Custom error types with fields
- Async error handling

---

**Note:** This feature is scaffolded in v1.0.0. Full implementation is planned for a future release.

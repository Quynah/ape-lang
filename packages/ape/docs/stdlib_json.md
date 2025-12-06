# APE JSON Module Documentation (v1.0.0)

**Author:** David Van Aelst  
**Status:** Scaffold - implementation pending  
**Version:** 1.0.0

---

## Overview

The JSON module provides functions for parsing, serializing, and manipulating JSON data in APE programs.

## Functions

### parse(json_string: String) -> Any

Parse a JSON string into APE data structures.

**Arguments:**
- `json_string` - Valid JSON string

**Returns:**
- Map for JSON objects
- List for JSON arrays
- Primitive values (String, Integer, Number, Boolean, null)

**Example:**
```ape
import json

task load_config(json_string: String):
    config = json.parse(json_string)
    host = config["database"]["host"]
    port = config["database"]["port"]
    return create_connection(host, port)
```

**Errors:**
- Raises `ParseError` if JSON is malformed

### stringify(data: Any, indent: Integer?) -> String

Convert APE data structures to JSON string.

**Arguments:**
- `data` - Data to serialize (Map, List, or primitive)
- `indent` - Optional number of spaces for indentation (null for compact)

**Returns:**
- JSON string representation

**Example:**
```ape
import json

task save_config(config: Map<String, Any>):
    json_string = json.stringify(config, indent=2)
    write_file("config.json", json_string)
```

### get(data: Map, path: String, default: Any?) -> Any

Get value from nested JSON using dot notation path.

**Arguments:**
- `data` - JSON object (Map)
- `path` - Dot-separated path (e.g., "user.address.city")
- `default` - Optional default value if path not found (default: null)

**Returns:**
- Value at path, or default if not found

**Example:**
```ape
import json

task get_user_city(user_data: Map<String, Any>):
    city = json.get(user_data, "address.city", "Unknown")
    return city
```

### set(data: Map, path: String, value: Any) -> Map

Set value in nested JSON using dot notation path.

**Arguments:**
- `data` - JSON object (Map)
- `path` - Dot-separated path
- `value` - Value to set

**Returns:**
- Updated data structure (creates nested objects as needed)

**Example:**
```ape
import json

task update_user_email(user_data: Map<String, Any>, email: String):
    updated = json.set(user_data, "contact.email", email)
    return updated
```

### has(data: Map, path: String) -> Boolean

Check if a path exists in JSON data.

**Arguments:**
- `data` - JSON object (Map)
- `path` - Dot-separated path

**Returns:**
- True if path exists, False otherwise

**Example:**
```ape
import json

task validate_config(config: Map<String, Any>):
    if not json.has(config, "database.host"):
        raise Error("Missing database host in config")
    
    if not json.has(config, "database.port"):
        raise Error("Missing database port in config")
```

## Complete Example

```ape
import json
import io

task process_api_response(response_text: String):
    # Parse JSON response
    data = json.parse(response_text)
    
    # Extract nested values
    status = json.get(data, "response.status", "unknown")
    
    if status == "success":
        items = json.get(data, "response.data.items", [])
        return items
    else:
        error_msg = json.get(data, "response.error.message", "Unknown error")
        raise Error("API error: " + error_msg)

task create_api_request(user_id: Integer, action: String):
    # Build request object
    request = {
        "user_id": user_id,
        "action": action,
        "timestamp": get_current_time()
    }
    
    # Add optional fields
    request = json.set(request, "metadata.client", "APE")
    request = json.set(request, "metadata.version", "1.0.0")
    
    # Serialize to JSON
    json_string = json.stringify(request, indent=2)
    
    return json_string
```

## Best Practices

### 1. Validate JSON Before Parsing

```ape
task safe_parse(json_string: String):
    try:
        data = json.parse(json_string)
        return data
    catch ParseError as e:
        print("Invalid JSON: " + e.message)
        return null
```

### 2. Use Default Values for Missing Paths

```ape
# Good
port = json.get(config, "server.port", 8080)

# Less safe
port = config["server"]["port"]  # May fail if path missing
```

### 3. Check Path Existence for Optional Fields

```ape
if json.has(data, "optional_field"):
    value = json.get(data, "optional_field")
    process_value(value)
```

### 4. Use Indentation for Human-Readable Output

```ape
# Pretty-print for logs/debugging
json_string = json.stringify(data, indent=2)

# Compact for network transmission
json_string = json.stringify(data)
```

## Type Mapping

### APE → JSON

| APE Type | JSON Type |
|----------|-----------|
| String | string |
| Integer | number |
| Number | number |
| Boolean | boolean |
| null | null |
| List | array |
| Map | object |

### JSON → APE

| JSON Type | APE Type |
|-----------|----------|
| string | String |
| number | Integer or Number |
| boolean | Boolean |
| null | null |
| array | List |
| object | Map<String, Any> |

## Limitations

Current limitations (to be addressed in future versions):
- No support for custom serialization
- No support for JSON Schema validation
- No streaming parser for large files
- Path notation limited to dot-separated strings (no array indexing)

---

**Note:** This feature is scaffolded in v1.0.0. Full implementation is planned for a future release.

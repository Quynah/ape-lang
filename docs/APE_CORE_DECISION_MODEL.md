# APE Core Decision Model

## Overview

APE has been upgraded to a **full decision engine** capable of expressing complex business logic, temporal reasoning, and data aggregation workflows.

**Philosophy:** Decisions are deterministic computations over structured data with explicit policies.

## Primitives

### 1. Records & Maps

**Record:** Named field structure (entity/data object)
```ape
entity Customer:
    id: String
    age: Integer
    joined: DateTime
```

**Map Literal:** Key-value pairs
```ape
payload = { "name": "Alice", "score": 100 }
```

**Runtime:** Both serialize to Python `dict`

### 2. Lists

**List Literal:** Ordered collections
```ape
items = [1, 2, 3]
records = [
    { "id": "a", "value": 10 },
    { "id": "b", "value": 20 }
]
```

**Operations:** `count`, `filter`, `map`, `unique`, `max`, `min`, `any`, `all`

### 3. DateTime & Duration

**DateTime:** Temporal points (always UTC)
```ape
now = datetime.now()
past = datetime.parse_iso8601("2024-01-01T00:00:00Z")
week_ago = now.subtract_days(7)
is_recent = past > week_ago
```

**Duration:** Time spans
```ape
d = duration.days(30)
h = duration.hours(48)
```

**Contract:** DateTime → ISO-8601 string, Duration → seconds (int)

### 4. Nested Data Access

**JSON Path Access:**
```ape
city = json.get(payload, "address.city", "Unknown")
owner = json.get(data, "metadata.owner", "system")
```

**Guarantees:**
- Never fails silently
- Always returns value or default
- Supports lists: `json.get(items, "0.name")`

## Decision Patterns

### Grouping & Aggregation

```python
# Group records by field
grouped = group_by(transactions, lambda t: t["category"])

# Count per group
counts = { k: count(v) for k, v in grouped.items() }

# Find max
top = max_value(counts.values())
```

**Functions:** `group_by`, `count`, `unique`, `max_value`, `min_value`, `sum_values`

### Temporal Logic

```python
# Check if event is recent
cutoff = datetime.now().subtract_days(30)
is_recent = event.timestamp > cutoff

# Filter old records
recent_only = filter(records, lambda r: r["date"] > cutoff)
```

### Collection Intelligence

```python
# Any match
has_high_risk = any_match(items, lambda x: x["risk"] > 0.8)

# All match
all_approved = all_match(items, lambda x: x["status"] == "approved")

# Unique values
departments = unique([r["dept"] for r in records])
```

### Nested Payload Parsing

```python
# Extract nested field with fallback
api_response = { "data": { "user": { "id": "123" } } }
user_id = json.get(api_response, "data.user.id", "unknown")

# Check if path exists
if json.has_path(response, "error.code"):
    # Handle error
```

## Type System

### Built-in Types
- **Scalars:** Integer, Float, String, Boolean
- **Collections:** List, Map
- **Temporal:** DateTime, Duration
- **Polymorphic:** Any, Value (untyped containers)

### Type Rules
1. **No implicit conversions** – explicit casts required
2. **Nullable via Optional** – `Optional<String>` allows null
3. **Generic-free syntax** – use base types (List, Map) not `List<T>`

## Policies

**Policy:** Declarative rules governing behavior
```ape
policy risk_assessment:
    rules:
        - Transactions above $10,000 require dual approval
        - High-risk customers trigger additional checks
        - Outdated data must be flagged
```

**Integration:** Policies are documentation + runtime validation targets

## Execution Model

### Determinism
- All operations are **pure** (no side effects)
- Same inputs → same outputs (always)
- Datetime uses explicit `now()` calls (injectable in tests)

### Tracing
- Execution produces audit trail
- All data access logged
- Decision path reconstructable

### Error Handling
- **Hard failures:** Type errors, invalid data → immediate exception
- **Graceful degradation:** `json.get` with defaults, `Optional` types

## Standard Library Modules

### std.collections
- `map(list, fn)` – Transform
- `filter(list, pred)` – Select
- `reduce(list, fn, init)` – Fold
- `group_by(list, key_fn)` – Categorize
- `unique(list)` – Deduplicate
- `count(list)`, `max_value(list)`, `min_value(list)`, `sum_values(list)`
- `any_match(list, pred)`, `all_match(list, pred)`

### std.datetime
- `now()` – Current UTC time
- `parse_iso8601(str)` – Parse timestamp
- `subtract_days(dt, n)`, `add_days(dt, n)`, `add_hours(dt, n)`
- `compare(dt1, dt2)` – Returns -1/0/1

### json (payload module)
- `get(data, path, default)` – Dotted path access
- `set(data, path, value)` – Immutable update
- `has_path(data, path)` – Path existence check
- `flatten(data)` – Nested → flat dict

### std.strings
- `contains_text(text, fragment)` – Substring check
- `upper(text)`, `lower(text)`, `trim(text)`
- `starts_with(text, prefix)`, `ends_with(text, suffix)`

## Example: Risk Scoring Decision

```ape
entity Transaction:
    amount: Float
    timestamp: DateTime
    customer_id: String

task assess_risk:
    inputs:
        transaction: Transaction
    outputs:
        risk_score: Float
    constraints:
        - deterministic
    steps:
        - get recent_transactions for customer
        - group by customer_id
        - count transactions in last 30 days
        - if count > 10 or amount > 10000 then high_risk
        - calculate risk_score
        - return risk_score
```

**Runtime:**
1. Fetch data (via capability adapter)
2. Group & count using `group_by` + `count`
3. Apply temporal filter with `datetime.subtract_days`
4. Compute score deterministically
5. Return structured result

## Migration from v1.0.4 to v1.0.5

### New Capabilities
✅ Map/Record literals  
✅ DateTime type system  
✅ Collection aggregations  
✅ JSON path access  
✅ Policy expressivity (any/all)

### Breaking Changes
❌ None – all new features are additive

### Limitations
⚠️ Multi-line maps require single-line syntax  
⚠️ Qualified calls (`std.module.func`) not yet in parser  
⚠️ Generic syntax (`List<T>`) not implemented

## Future Roadmap

- **Streaming aggregations** for large datasets
- **Incremental computation** for re-evaluation efficiency
- **Multi-tenancy** with isolated decision contexts
- **Capability adapters** for external data sources
- **Policy verification** at compile time

---

**Version:** Decision Engine v2024  
**Status:** Production-ready for Quynah workflows  
**Author:** David Van Aelst  
**Date:** 2024-12-17

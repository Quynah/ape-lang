# Ape Language Specification v1.0

> Status: **Normative** for public v1.0 features.  
> Implementations must keep this document and `language_spec.py` in sync.

## 1. Goals and Scope

Ape is a deterministic, AI-first language designed for unambiguous
human–AI collaboration. This document describes:

- the core syntax used by the v1.0 reference implementation,
- the keywords and structural constructs that are guaranteed to be supported,
- the "steps language" used inside tasks and flows,
- the multi-language control word mappings.

Anything not covered here is considered implementation detail and may change
without notice.

## 2. Source Files and Lexical Structure

### 2.1 File format

- Source files use the `.ape` extension.
- Encoding is UTF-8.
- Line endings follow the host platform convention but should be treated
  as plain line breaks.

### 2.2 Indentation and blocks

Ape uses **indentation** to define blocks.

- A line that ends with a colon (`:`) starts a new block.
- All lines in that block must be indented with spaces.
- Indentation must be consistent within a file (the reference examples use 4 spaces).

Examples:

```ape
module file_processor

entity Stats:
    count: Integer
    doubled_count: Integer
```

### 2.3 Comments

A line starting with `#` (after optional indentation) is a comment.

Comments extend to the end of the line and are ignored by the compiler.

```ape
# Email policy example
# Shows entities, enums, tasks and policies.
```

### 2.4 Identifiers

Identifiers name modules, entities, tasks, flows, policies, fields, etc.

- Must start with a letter (A–Z or a–z) or underscore `_`.
- May continue with letters, digits or underscores.
- Are case-sensitive.
- Must not be a reserved keyword listed in this specification.

Examples:

```
Stats
EmailAssessment
file_processor
calculator_demo
email_threat_policy
```

### 2.5 Literals

Ape reuses familiar literal forms:

- **Integers:** `0`, `1`, `42`
- **Floats:** `3.14`, `0.5`, `10.0`
- **Booleans:** `true`, `false`, `True`, `False`
- **Strings:** double-quoted or single-quoted, implementation-defined escape handling.

Strings appear in constraints, rationale and other descriptive fields:

```ape
rationale: "Formatting of the human-readable summary can vary"
```

## 3. Keywords

This section lists the canonical keywords as exposed via `language_spec.py`.
These are reserved and must not be used as identifiers.

### 3.1 Top-level keywords

Top-level keywords introduce declarations at the module level:

```python
TOP_LEVEL_KEYWORDS = {
    "entity",
    "enum",
    "flow",
    "from",
    "import",
    "module",
    "policy",
    "task",
}
```

Their syntactic roles are:

- **module** – declares a module name.
- **import** / **from** – import other modules.
- **enum** – declares an enumeration.
- **entity** – declares a record-like data type.
- **task** – declares a deterministic unit of work with inputs, outputs and steps.
- **flow** – declares a high-level orchestration of tasks.
- **policy** – declares policy rules, typically human-readable, for governance.

### 3.2 Section keywords

Section keywords appear inside declarations such as entities, tasks, flows and policies:

```python
SECTION_KEYWORDS = {
    "allow",
    "bounds",
    "constraints",
    "deviation",
    "inputs",
    "mode",
    "outputs",
    "rationale",
    "rules",
    "scope",
    "steps",
}
```

Their roles:

- **inputs** – lists named inputs and their types for a task.
- **outputs** – lists named outputs and their types for a task or flow.
- **constraints** – lists constraints on a task or flow
  (e.g. `- deterministic` or an `allow deviation` block).
- **steps** – introduces the ordered steps that define behaviour.
- **rules** – introduces a list of policy rules.
- **allow** / **deviation** / **scope** / **mode** / **bounds** / **rationale** – used together in
  a structured "allow deviation" block inside constraints.

### 3.3 Control-flow keywords

Control-flow keywords are primarily used inside the steps language:

```python
CONTROL_FLOW_KEYWORDS = {
    "elif",
    "else",
    "for",
    "if",
    "in",
    "while",
}
```

Examples:

```ape
- if operation is add then compute left plus right
- if domain is trusted return LOW threat level
```

### 3.4 Boolean keywords

Boolean keywords recognise common boolean literals and operators:

```python
BOOLEAN_KEYWORDS = {
    "False",
    "True",
    "and",
    "false",
    "not",
    "or",
    "true",
}
```

These appear both in expressions and in natural-language steps.

## 4. Types

### 4.1 Primitive types

The core primitive types are:

```python
PRIMITIVE_TYPES = {
    "Any",
    "Boolean",
    "Float",
    "Integer",
    "String",
}
```

Examples:

```ape
count: Integer
prompt_text: String
success: Boolean
```

### 4.2 Structured types

Structured types describe composite shapes:

```python
STRUCTURED_TYPES = {
    "Dict",
    "List",
    "Map",
    "Optional",
    "Record",
    "Tuple",
}
```

These are used by the type system and runtime, and may be surfaced in future
examples and libraries. Entities and enums themselves are also usable as types:

```ape
entity Email:
    from_domain: String
    subject: String
    body: String

entity EmailAssessment:
    email: Email
    level: ThreatLevel
    reason: String
```

### 4.3 Operators

The canonical operator set for v1.0 is:

```python
OPERATORS = {
    "!=",
    "%",
    "*",
    "+",
    ",",
    "-",
    "->",
    ".",
    "/",
    ":",
    "<",
    "<=",
    "==",
    ">",
    ">=",
    "|",
}
```

Not all operators are used directly in the high-level examples, but they form
the basis for expressions in the IR and generated code.

## 5. Modules and Imports

### 5.1 Module declaration

A file may declare a module:

```ape
module file_processor
```

The module name is an identifier.

### 5.2 Imports

Ape supports simple imports:

```ape
import sys
import io
import math
```

as well as `from` imports in the IR / runtime layer. The exact import resolution
strategy is implementation-specific but the lexical forms `import` and `from`
are reserved and documented here.

## 6. Declarations

### 6.1 Enums

Enums are declared as:

```ape
enum Operation:
    - add
    - subtract
    - multiply
    - divide
```

Each bullet after the enum header defines a literal value of the enum.

### 6.2 Entities

Entities define record-like data types:

```ape
entity CalculationRequest:
    left: Float
    right: Float
    op: Operation

entity CalculationResult:
    left: Float
    right: Float
    op: Operation
    result: Float
```

### 6.3 Tasks

Tasks encapsulate deterministic work:

```ape
task process_file:
    inputs:
        input_path: String
        output_path: String
    outputs:
        stats: Stats
    constraints:
        - deterministic
    steps:
        - call io.read_file with input_path to get content
        - count lines in content to get count
        - call math.multiply with count and 2 to get doubled_count
        - create Stats with count and doubled_count
        - call io.write_file with output_path and content
        - return stats
```

### 6.4 Flows

Flows orchestrate tasks and other operations:

```ape
flow calculator_demo:
    steps:
        - create CalculationRequest with left equals 1 and right equals 2 and op equals add
        - call calculate task with the request
        - output the result to console
    constraints:
        - deterministic
```

### 6.5 Policies

Policies capture rules in a more narrative form:

```ape
policy email_threat_policy:
    rules:
        - Emails from trusted domains are always assessed as LOW
        - Emails with HIGH assessment must be quarantined immediately
        - Emails with MEDIUM assessment require manual review within 24 hours
        - All email assessments must be logged with timestamp and assessor
        - Safelist must be reviewed quarterly
```

## 7. The Steps Language

Inside `steps:` sections, Ape uses a constrained natural-language style.

### 7.1 Step sentences

Each step is a bullet starting with a step verb:

```ape
steps:
    - check request operation type
    - if operation is add then compute left plus right
    - create CalculationResult with left and right and op from request
    - set result field to computed value
    - return result
```

The reference implementation recognises the following step verbs:

```python
STEP_VERBS = {
    "add",
    "allow",
    "call",
    "check",
    "compute",
    "convert",
    "copy",
    "count",
    "create",
    "divide",
    "ensure",
    "exit",
    "filter",
    "generate",
    "if",
    "map",
    "multiply",
    "otherwise",
    "output",
    "parse",
    "power",
    "print",
    "read",
    "reduce",
    "return",
    "run",
    "set",
    "sort",
    "store",
    "subtract",
    "transform",
    "validate",
    "verify",
    "write",
}
```

This set is exhaustive for the v1.0 examples and public documentation.

### 7.2 Connectors

Common connectors inside step sentences include:

```python
STEP_CONNECTORS = {
    "a",
    "an",
    "and",
    "as",
    "equals",
    "from",
    "into",
    "is",
    "or",
    "the",
    "then",
    "to",
    "with",
}
```

These words help shape the sentence but do not change the core semantics.

### 7.3 Constraints and "allow deviation"

Constraints often include a pure deterministic marker:

```ape
constraints:
    - deterministic
```

Tasks may allow constrained deviation:

```ape
constraints:
    - deterministic
    - allow deviation:
        scope: steps
        mode: creative
        bounds:
            - result.result must always equal the mathematically correct outcome
            - summary must describe the operation and result using request.left, request.right and result.result
            - no additional side effects are allowed
        rationale: "Formatting of the human-readable summary can vary"
```

The section keywords `allow`, `deviation`, `scope`, `mode`, `bounds` and
`rationale` are reserved for this structured pattern.

## 8. Multi-language control words

Ape supports multi-language control words for `if`, `else`, `while`, `for`,
`in`, `and`, `or`, `not`. They are normalised back to the canonical English
forms via `MULTI_LANGUAGE_KEYWORDS` in `language_spec.py`.

The v1.0 mappings are:

### Dutch (nl)

- **als** → if
- **anders** → else
- **zolang** → while
- **voor** → for
- **in** → in
- **en** → and
- **of** → or
- **niet** → not

### French (fr)

- **si** → if
- **sinon** → else
- **tant que** → while
- **pour** → for
- **dans** → in
- **et** → and
- **ou** → or
- **pas** → not

### German (de)

- **wenn** → if
- **sonst** → else
- **solange** → while
- **für** → for
- **in** → in
- **und** → and
- **oder** → or
- **nicht** → not

### Spanish (es)

- **si** → if
- **sino** → else
- **mientras** → while
- **para** → for
- **en** → in
- **y** → and
- **o** → or
- **no** → not

### Italian (it)

- **se** → if
- **altrimenti** → else
- **mentre** → while
- **per** → for
- **in** → in
- **e** → and
- **o** → or
- **non** → not

### Portuguese (pt)

- **se** → if
- **senão** → else
- **enquanto** → while
- **para** → for
- **em** → in
- **e** → and
- **ou** → or
- **não** → not

Implementations may add further languages, but must update both
`MULTI_LANGUAGE_KEYWORDS` and this document to remain compliant.

## 9. Versioning and Compatibility

This specification describes **Ape v1.0** as implemented by the reference
compiler and examples.

- New features must be added to `language_spec.py` first.
- This document must then be updated to reflect the new constructs.
- Deprecated constructs should be clearly marked in both places.

The real parser and validator remain the final authority for what a particular
build accepts, but any public Ape implementation should aim to keep behaviour
aligned with this specification.

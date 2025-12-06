# Ape Language Specification v1.0

> **Status:** v1.0 (describes the language as implemented in Ape 1.0.0)  
> **Scope:** This document describes the syntax and core concepts of the Ape language as used by the official examples:
> - `calculator_basic.ape`
> - `calculator_smart.ape`
> - `email_policy_basic.ape`
> - `hello_imports.ape`
> - `stdlib_complete.ape`

Ape is a **deterministic, AI-first domain language** designed for declarative descriptions of tasks, flows and policies in clear natural language, while still remaining strictly parseable and compilable to a safe target language (e.g. Python).

This document answers the question:

> "Which words, constructs and blocks are allowed in Ape, and how can I write a valid `.ape` file?"

It is deliberately **conservative**: it documents what is **guaranteed** to work in Ape 1.0.0 based on the shipped compiler and examples.

---

## 1. Source Files, Encoding & Comments

- Ape source files use the extension: **`.ape`**
- Text encoding: **UTF-8**
- Line endings: any standard platform line endings are accepted; the language is **line- and indentation-aware**.

### 1.1 Comments

Ape uses `#` for single-line comments:

```ape
# This is a comment
# Everything after `#` on the same line is ignored.
```

Comments can appear:

- On their own line
- Above declarations (modules, entities, tasks, flows, policies, enums)
- Inside blocks, above sections like inputs, outputs, steps, etc.

There is no special syntax for block comments in v1.0.

---

## 2. Top-Level Structure

A `.ape` file consists of a sequence of top-level declarations, optionally preceded by an optional module declaration and one or more import statements:

1. **Optional:** `module` declaration
2. **Optional:** one or more `import` statements
3. **Zero or more of:**
   - `enum` declarations
   - `entity` declarations
   - `task` declarations
   - `flow` declarations
   - `policy` declarations

### 2.1 `module` (optional)

Declares the logical module name of the file.

```ape
module main
```

- The `module` line is optional. Some examples use it (e.g. `hello_imports.ape`, `stdlib_complete.ape`), some do not (`calculator_basic.ape`).
- At most one `module` declaration is expected per file.
- The module name is a bare identifier (letters, digits, underscore; must start with a letter or underscore).

### 2.2 `import`

Imports another module by name.

```ape
import sys
import math
import io
```

- `import` must appear at the top level (no indentation).
- The imported name is a bare identifier.
- Imports from the Ape standard library (e.g. `sys`, `math`, `io`) are resolved by the compiler/runtime.

---

## 3. Core Declarations

The following top-level declarations are recognized in v1.0:

- `enum`
- `entity`
- `task`
- `flow`
- `policy`

All of them:

- Start at the left margin (no indentation).
- Use a colon (`:`) after the declaration header line.
- Introduce an indented block.

Indentation rules are similar to Python: consistent indentation inside a block is required.

### 3.1 `enum`

Defines a closed set of named values.

**Syntax:**

```ape
enum ThreatLevel:
    - LOW
    - MEDIUM
    - HIGH
```

Or:

```ape
enum Operation:
    - add
    - subtract
    - multiply
    - divide
```

**Rules:**

- The enum name is a type identifier (e.g. `ThreatLevel`, `Operation`).
- Each enum member is given as a list item:
  - Starts with `-` followed by a name.
  - The name can be upper-case (`LOW`) or lower-case (`add`), depending on the domain.
- Enum types can then be used as field types in entity definitions and elsewhere.

### 3.2 `entity`

Defines a structured data type with named fields.

**Syntax:**

```ape
entity Email:
    from_domain: String
    subject: String
    body: String

entity CalculationResult:
    left: Float
    right: Float
    op: Operation
    result: Float
```

**Rules:**

- The entity name is a type identifier (PascalCase is recommended).
- Each field is declared on its own line as:
  ```
  field_name: TypeName
  ```
- Indentation is required under the entity block.
- `TypeName` can be:
  - A primitive type (see §4).
  - An enum type.
  - Another entity type.

Entities are used for input/output structures of tasks, to represent emails, stats, calculation requests/results, etc.

### 3.3 Primitive Types

Ape v1.0 defines at least the following primitive scalar types, as used in the official examples:

- `String`
- `Integer`
- `Float`
- `Boolean`

These types are used in:

- `entity` field declarations
- `inputs` and `outputs` sections of tasks and flows

### 3.4 `task`

A task describes a deterministic unit of work with structured inputs, structured outputs, and a step-by-step specification.

**High-level structure:**

```ape
task assess_email_threat:
    inputs:
        email: Email
    outputs:
        assessment: EmailAssessment
    constraints:
        - deterministic
    steps:
        - check sender domain against safelist
        - if domain is trusted return LOW threat level
        - check subject for suspicious keywords
        - ...
```

**Sections:**

- **`inputs:`** (optional but recommended)
  - Each line: `name: TypeName`
  - Describes data the task expects.

- **`outputs:`** (optional but recommended)
  - Each line: `name: TypeName`
  - Describes the result values.

- **`constraints:`** (optional)
  - A list of constraint bullet points:
    ```ape
    constraints:
        - deterministic
    ```
  - In v1.0, `- deterministic` is the primary constraint used in the examples, indicating the task must be deterministic.

- **`steps:`** (required for executable tasks)
  - A list of natural-language instructions, each starting with `-`.
  - Typical step patterns seen in v1.0 examples:
    - `- set x to 10`
    - `- create CalculationRequest with left equals 1 and right equals 2 and op equals add`
    - `- call calculate task with the request`
    - `- check subject for suspicious keywords`
    - `- if body is empty then return MEDIUM threat level`
    - `- return result`

Ape's compiler maps these steps to an internal IR, which is then compiled to a target language.

### 3.5 `flow`

A flow describes a higher-level orchestration: a sequence of steps that glue together tasks and operations.

**Example (simplified):**

```ape
flow calculator_demo:
    steps:
        - create CalculationRequest with left equals 1 and right equals 2 and op equals add
        - call calculate task with the request
        - output the result to console
    constraints:
        - deterministic
```

**Rules:**

- `flow` has a name (identifier).
- Required section: `steps:`
- Optional section: `constraints:`
- Step lines use the same bullet syntax as in `task.steps`.

Flows are typically used to demonstrate example usage (e.g. demo calculators, file processors).

### 3.6 `policy`

A policy expresses declarative rules, often as natural-language sentences.

**Example from `email_policy_basic.ape`:**

```ape
policy email_threat_policy:
    rules:
        - Emails from trusted domains are always assessed as LOW
        - Emails with HIGH assessment must be quarantined immediately
        - Emails with MEDIUM assessment require manual review within 24 hours
        - All email assessments must be logged with timestamp and assessor
        - Safelist must be reviewed quarterly
```

**Rules:**

- `policy` has a name (identifier).
- Inside the block, a `rules:` section is used.
- `rules:` contains a bullet list of natural-language statements.

Policies are primarily declarative; they guide how tasks and flows should be interpreted and audited.

---

## 4. Sections and Indentation

Sections such as `inputs:`, `outputs:`, `constraints:`, `steps:`, `rules:`:

- Must appear inside a containing declaration block (`task`, `flow`, `policy`).
- Are followed by an indented block.
- Use bullet lines (`- ...`) for lists, or `name: TypeName` for structured field lists.

**Example:**

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
        - read file from input_path
        - count lines in content to get count
        - call math.multiply with count and 2 to get doubled_count
        - create Stats with count and doubled_count
        - call io.write_file with output_path and content
        - return stats
```

Consistency of indentation is required. Mixing different indentation widths within the same block is undefined and should be avoided.

---

## 5. Keywords and Reserved Words

The following words are reserved at the language level in Ape v1.0 and must not be used as identifiers:

**Top-level and structural keywords:**
- `module`
- `import`
- `enum`
- `entity`
- `task`
- `flow`
- `policy`
- `inputs`
- `outputs`
- `constraints`
- `steps`
- `rules`

**Primitive types (when used as type names):**
- `String`
- `Integer`
- `Float`
- `Boolean`

In addition, certain step verbs are treated specially by the compiler/IR builder in v1.0, for example:

- `set`
- `create`
- `call`
- `check`
- `compute`
- `convert`
- `return`
- conditional patterns like `if ... then ...`

Concrete patterns can be seen in the official examples. Future versions of this specification may add a more formal grammar for step sentences as the language evolves.

---

## 6. Line-Based Grammar (Informal EBNF)

This section provides a line-oriented, informal grammar to understand the shape of valid files.

```ebnf
File          ::= (Comment | ModuleDecl | ImportDecl | TopLevelDecl)*

Comment       ::= "#" <any text>

ModuleDecl    ::= "module" Identifier NEWLINE
ImportDecl    ::= "import" Identifier NEWLINE

TopLevelDecl  ::= EnumDecl
                | EntityDecl
                | TaskDecl
                | FlowDecl
                | PolicyDecl

EnumDecl      ::= "enum" TypeIdentifier ":" NEWLINE
                  Indent EnumItem+ Dedent

EnumItem      ::= "-" EnumValue NEWLINE

EntityDecl    ::= "entity" TypeIdentifier ":" NEWLINE
                  Indent EntityField+ Dedent

EntityField   ::= Identifier ":" TypeIdentifier NEWLINE

TaskDecl      ::= "task" Identifier ":" NEWLINE
                  Indent TaskSection+ Dedent

TaskSection   ::= InputsSection
                | OutputsSection
                | ConstraintsSection
                | StepsSection

InputsSection ::= "inputs:" NEWLINE
                  Indent EntityField+ Dedent

OutputsSection ::= "outputs:" NEWLINE
                   Indent EntityField+ Dedent

ConstraintsSection ::= "constraints:" NEWLINE
                       Indent BulletLine+ Dedent

StepsSection  ::= "steps:" NEWLINE
                  Indent StepLine+ Dedent

FlowDecl      ::= "flow" Identifier ":" NEWLINE
                  Indent FlowSection+ Dedent

FlowSection   ::= StepsSection
                | ConstraintsSection

PolicyDecl    ::= "policy" Identifier ":" NEWLINE
                  Indent RulesSection+ Dedent

RulesSection  ::= "rules:" NEWLINE
                  Indent BulletLine+ Dedent

BulletLine    ::= "-" <free text> NEWLINE
StepLine      ::= "-" <free text> NEWLINE
```

**Note:** `<free text>` lines are still interpreted by the compiler with additional pattern matching, but from a syntax perspective they follow the same indentation and bullet rules.

---

## 7. Versioning and Compatibility

This document describes **Ape Language v1.0** as implemented by the Ape 1.0.0 compiler.

Newer versions may extend:

- additional primitive types,
- additional section kinds,
- richer step grammars,
- new declaration kinds.

Where possible, new versions should remain backwards compatible with the constructs and patterns shown here.

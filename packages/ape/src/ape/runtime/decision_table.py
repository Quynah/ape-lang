"""
APE Decision Table Engine

Tabular decision logic execution with hit policies.

Author: David Van Aelst
Status: Decision Engine v2024 - Complete
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class HitPolicy(Enum):
    """Decision table hit policies (DMN-compatible)"""
    UNIQUE = "U"       # Only one rule can match
    FIRST = "F"        # First matching rule wins
    PRIORITY = "P"     # Priority-based selection
    ANY = "A"          # Any match (all must agree on output)
    COLLECT = "C"      # Collect all matching outputs
    RULE_ORDER = "R"   # Rule order determines precedence


@dataclass
class DecisionTableColumn:
    """Column definition in decision table"""
    name: str
    type: str  # "input" or "output"
    expression: Optional[str] = None  # For input columns
    default_value: Any = None  # For output columns


@dataclass
class DecisionTableRow:
    """Single row (rule) in decision table"""
    row_id: int
    inputs: List[Any]  # Input conditions (one per input column)
    outputs: List[Any]  # Output values (one per output column)
    priority: int = 0
    annotation: str = ""  # Human-readable description


@dataclass
class DecisionTableResult:
    """Result of decision table evaluation"""
    matched_rows: List[int]  # Row IDs that matched
    outputs: Dict[str, Any]  # Final output values
    hit_policy: HitPolicy
    unique_match: bool  # True if exactly one row matched
    conflict_detected: bool  # True if multiple rows with different outputs
    reason: str


class DecisionTable:
    """
    Decision table for tabular decision logic.

    Implements DMN-style decision tables with hit policies.

    Example:
        table = DecisionTable(
            name="loan_approval",
            hit_policy=HitPolicy.PRIORITY
        )

        # Define columns
        table.add_input_column("age", "customer.age")
        table.add_input_column("income", "customer.annual_income")
        table.add_output_column("approved", default_value=False)
        table.add_output_column("rate", default_value=0.0)

        # Add rules (rows)
        table.add_row([">= 25", ">= 50000"], [True, 0.05], priority=10)
        table.add_row([">= 18", ">= 30000"], [True, 0.08], priority=5)
        table.add_row(["< 18", "*"], [False, 0.0], priority=1)

        # Evaluate
        context = {"customer": {"age": 30, "annual_income": 60000}}
        result = table.evaluate(context)
        # result.outputs = {"approved": True, "rate": 0.05}
    """

    def __init__(self, name: str, hit_policy: HitPolicy = HitPolicy.FIRST):
        self.name = name
        self.hit_policy = hit_policy
        self.input_columns: List[DecisionTableColumn] = []
        self.output_columns: List[DecisionTableColumn] = []
        self.rows: List[DecisionTableRow] = []
        self.enabled = True

    def add_input_column(self, name: str, expression: str) -> None:
        """
        Add an input column.

        Args:
            name: Column name
            expression: APE expression to extract value from context
        """
        col = DecisionTableColumn(
            name=name,
            type="input",
            expression=expression
        )
        self.input_columns.append(col)

    def add_output_column(self, name: str, default_value: Any = None) -> None:
        """
        Add an output column.

        Args:
            name: Column name
            default_value: Default value if no rules match
        """
        col = DecisionTableColumn(
            name=name,
            type="output",
            default_value=default_value
        )
        self.output_columns.append(col)

    def add_row(self, inputs: List[Any], outputs: List[Any],
                priority: int = 0, annotation: str = "") -> None:
        """
        Add a decision rule (table row).

        Args:
            inputs: Input conditions (one per input column)
            outputs: Output values (one per output column)
            priority: Priority level (for PRIORITY hit policy)
            annotation: Human-readable description
        """
        if len(inputs) != len(self.input_columns):
            raise ValueError(
                f"Input count mismatch: expected {len(self.input_columns)}, got {len(inputs)}"
            )

        if len(outputs) != len(self.output_columns):
            raise ValueError(
                f"Output count mismatch: expected {len(self.output_columns)}, got {len(outputs)}"
            )

        row = DecisionTableRow(
            row_id=len(self.rows) + 1,
            inputs=inputs,
            outputs=outputs,
            priority=priority,
            annotation=annotation
        )
        self.rows.append(row)

        # Sort by priority if using PRIORITY hit policy
        if self.hit_policy == HitPolicy.PRIORITY:
            self.rows.sort(key=lambda r: r.priority, reverse=True)

    def evaluate(self, context: Dict[str, Any],
                 executor: Optional[Any] = None) -> DecisionTableResult:
        """
        Evaluate decision table against context.

        Args:
            context: Input variables
            executor: RuntimeExecutor instance

        Returns:
            DecisionTableResult with matched rows and outputs
        """
        if not self.enabled:
            return self._default_result("Table disabled")

        if not self.rows:
            return self._default_result("No rules defined")

        # Extract input values from context
        input_values = self._extract_inputs(context, executor)

        # Find matching rows
        matched_rows = []
        for row in self.rows:
            if self._row_matches(row, input_values, context, executor):
                matched_rows.append(row)

                # Stop at first match for FIRST or UNIQUE policies
                if self.hit_policy in (HitPolicy.FIRST, HitPolicy.UNIQUE):
                    break

        # No matches = return defaults
        if not matched_rows:
            return self._default_result("No rules matched")

        # Apply hit policy to determine final outputs
        return self._apply_hit_policy(matched_rows, context)

    def _extract_inputs(self, context: Dict[str, Any],
                       executor: Optional[Any]) -> List[Any]:
        """Extract input values from context using column expressions"""
        values = []

        for col in self.input_columns:
            if col.expression is None:
                values.append(None)
                continue

            if executor is None:
                # Fallback: convert dicts to objects for dot notation support
                try:
                    class DictWrapper:
                        def __init__(self, data):
                            for k, v in data.items():
                                if isinstance(v, dict):
                                    setattr(self, k, DictWrapper(v))
                                else:
                                    setattr(self, k, v)

                    namespace = {}
                    for key, value in context.items():
                        if isinstance(value, dict):
                            namespace[key] = DictWrapper(value)
                        else:
                            namespace[key] = value

                    value = eval(col.expression, {"__builtins__": {}}, namespace)
                    values.append(value)
                except Exception:
                    values.append(None)
            else:
                # Use APE executor
                try:
                    value = executor.eval_expression_with_context(
                        col.expression,
                        context
                    )
                    values.append(value)
                except Exception:
                    values.append(None)

        return values

    def _flatten_context(self, context: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested dicts for expression evaluation"""
        result = {}
        for key, value in context.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten_context(value, full_key))
                result[key if not prefix else full_key] = value
            else:
                result[full_key] = value
                if not prefix:
                    result[key] = value
        return result

    def _row_matches(self, row: DecisionTableRow, input_values: List[Any],
                    context: Dict[str, Any], executor: Optional[Any]) -> bool:
        """Check if a row matches the input values"""
        for i, (condition, value) in enumerate(zip(row.inputs, input_values)):
            if not self._condition_matches(condition, value, context, executor):
                return False
        return True

    def _condition_matches(self, condition: Any, value: Any,
                          context: Dict[str, Any], executor: Optional[Any]) -> bool:
        """
        Check if a condition matches a value.

        Supports:
        - Exact match: "premium" matches "premium"
        - Wildcard: "*" or "-" matches anything
        - Comparison: ">= 18" evaluates against value
        - Range: "18..65" checks if value in range
        - List: "[A,B,C]" checks if value in list
        """
        # Wildcard always matches
        if condition in ("*", "-", None):
            return True

        # Exact match
        if condition == value:
            return True

        # String-based conditions
        if isinstance(condition, str):
            # Comparison operators
            for op in [">=", "<=", ">", "<", "==", "!="]:
                if condition.startswith(op):
                    try:
                        threshold = condition[len(op):].strip()
                        # Try to convert to number
                        try:
                            threshold_num = float(threshold)
                            value_num = float(value)
                        except (ValueError, TypeError):
                            threshold_num = threshold
                            value_num = value

                        # Evaluate comparison
                        expr = f"{value_num} {op} {threshold_num}"
                        result = eval(expr, {"__builtins__": {}}, {})
                        return bool(result)
                    except Exception:
                        return False

            # Range: "18..65"
            if ".." in condition:
                try:
                    parts = condition.split("..")
                    low = float(parts[0])
                    high = float(parts[1])
                    val = float(value)
                    return low <= val <= high
                except (ValueError, TypeError, IndexError):
                    return False

            # List: "[A,B,C]"
            if condition.startswith("[") and condition.endswith("]"):
                try:
                    items = [item.strip() for item in condition[1:-1].split(",")]
                    return value in items
                except Exception:
                    return False

        return False

    def _apply_hit_policy(self, matched_rows: List[DecisionTableRow],
                         context: Dict[str, Any]) -> DecisionTableResult:
        """Apply hit policy to determine final outputs"""
        if self.hit_policy == HitPolicy.UNIQUE:
            if len(matched_rows) > 1:
                return DecisionTableResult(
                    matched_rows=[r.row_id for r in matched_rows],
                    outputs=self._get_default_outputs(),
                    hit_policy=self.hit_policy,
                    unique_match=False,
                    conflict_detected=True,
                    reason=f"UNIQUE policy violated: {len(matched_rows)} rules matched"
                )

        # For FIRST, PRIORITY, RULE_ORDER: use first matched row
        if self.hit_policy in (HitPolicy.FIRST, HitPolicy.PRIORITY, HitPolicy.RULE_ORDER):
            row = matched_rows[0]
            return DecisionTableResult(
                matched_rows=[row.row_id],
                outputs=self._build_output_dict(row),
                hit_policy=self.hit_policy,
                unique_match=len(matched_rows) == 1,
                conflict_detected=False,
                reason=f"Rule {row.row_id} matched"
            )

        # For ANY: check all outputs agree
        if self.hit_policy == HitPolicy.ANY:
            first_outputs = self._build_output_dict(matched_rows[0])
            for row in matched_rows[1:]:
                row_outputs = self._build_output_dict(row)
                if row_outputs != first_outputs:
                    return DecisionTableResult(
                        matched_rows=[r.row_id for r in matched_rows],
                        outputs=self._get_default_outputs(),
                        hit_policy=self.hit_policy,
                        unique_match=False,
                        conflict_detected=True,
                        reason="ANY policy violated: outputs disagree"
                    )
            return DecisionTableResult(
                matched_rows=[r.row_id for r in matched_rows],
                outputs=first_outputs,
                hit_policy=self.hit_policy,
                unique_match=len(matched_rows) == 1,
                conflict_detected=False,
                reason=f"{len(matched_rows)} rules matched with same output"
            )

        # For COLLECT: collect all outputs into lists
        if self.hit_policy == HitPolicy.COLLECT:
            collected = {}
            for col in self.output_columns:
                collected[col.name] = []

            for row in matched_rows:
                for i, col in enumerate(self.output_columns):
                    collected[col.name].append(row.outputs[i])

            return DecisionTableResult(
                matched_rows=[r.row_id for r in matched_rows],
                outputs=collected,
                hit_policy=self.hit_policy,
                unique_match=len(matched_rows) == 1,
                conflict_detected=False,
                reason=f"Collected outputs from {len(matched_rows)} rules"
            )

        # Default: return first match
        row = matched_rows[0]
        return DecisionTableResult(
            matched_rows=[row.row_id],
            outputs=self._build_output_dict(row),
            hit_policy=self.hit_policy,
            unique_match=len(matched_rows) == 1,
            conflict_detected=False,
            reason=f"Rule {row.row_id} matched"
        )

    def _build_output_dict(self, row: DecisionTableRow) -> Dict[str, Any]:
        """Build output dictionary from a row"""
        return {
            col.name: row.outputs[i]
            for i, col in enumerate(self.output_columns)
        }

    def _get_default_outputs(self) -> Dict[str, Any]:
        """Get default output values"""
        return {
            col.name: col.default_value
            for col in self.output_columns
        }

    def _default_result(self, reason: str) -> DecisionTableResult:
        """Create a default result with no matches"""
        return DecisionTableResult(
            matched_rows=[],
            outputs=self._get_default_outputs(),
            hit_policy=self.hit_policy,
            unique_match=False,
            conflict_detected=False,
            reason=reason
        )

    def get_row(self, row_id: int) -> Optional[DecisionTableRow]:
        """Get a row by ID"""
        for row in self.rows:
            if row.row_id == row_id:
                return row
        return None

    def remove_row(self, row_id: int) -> bool:
        """Remove a row by ID"""
        original_len = len(self.rows)
        self.rows = [r for r in self.rows if r.row_id != row_id]
        return len(self.rows) < original_len

    def clear_rows(self) -> None:
        """Remove all rows"""
        self.rows.clear()

    def validate_completeness(self) -> List[str]:
        """
        Validate table completeness.

        Returns:
            List of validation warnings/errors
        """
        warnings = []

        if not self.input_columns:
            warnings.append("No input columns defined")

        if not self.output_columns:
            warnings.append("No output columns defined")

        if not self.rows:
            warnings.append("No rules defined")

        if self.hit_policy == HitPolicy.UNIQUE and len(self.rows) > 1:
            # Check for overlapping conditions
            # (Simplified check - full implementation would need constraint solver)
            warnings.append("UNIQUE policy with multiple rules - verify no overlaps")

        return warnings


__all__ = [
    'DecisionTable', 'HitPolicy',
    'DecisionTableColumn', 'DecisionTableRow', 'DecisionTableResult'
]



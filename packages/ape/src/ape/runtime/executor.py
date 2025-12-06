"""
Ape Runtime Executor

AST-based execution engine without using exec() or eval().
Deterministic, sandbox-safe execution of Ape control flow structures.
"""

import re
from typing import Any, List, Optional
from ape.parser.ast_nodes import (
    ASTNode, IfNode, WhileNode, ForNode, ExpressionNode,
    StepNode, TaskDefNode, FlowDefNode, ModuleNode
)
from ape.runtime.context import ExecutionContext, ExecutionError, MaxIterationsExceeded
from ape.runtime.trace import TraceCollector, TraceEvent, create_snapshot
from ape.errors import CapabilityError
from ape.std import logic, collections, strings, math


class RuntimeExecutor:
    """
    AST-based runtime executor for Ape programs.
    
    Executes control flow (if/while/for) without using Python exec().
    All execution is deterministic and sandbox-safe.
    
    Design principles:
    - No filesystem, network, or environment access
    - No exec(), eval(), or compile()
    - All state in ExecutionContext
    - Iteration limits for safety
    - Optional execution tracing for observability
    - Dry-run mode for safe analysis
    - Capability gating for side effects
    - Standard library intrinsics (pure functions, no capabilities needed)
    """
    
    # Standard library module mapping
    STDLIB_MODULES = {
        'std.logic': logic,
        'std.collections': collections,
        'std.strings': strings,
        'std.math': math,
    }
    
    def __init__(
        self, 
        max_iterations: int = 10_000,
        trace: Optional[TraceCollector] = None,
        dry_run: bool = False
    ):
        """
        Initialize runtime executor.
        
        Args:
            max_iterations: Maximum loop iterations (safety limit)
            trace: Optional trace collector for execution observability
            dry_run: If True, run in dry-run mode (no mutations)
        """
        self.max_iterations = max_iterations
        self.trace = trace
        self.dry_run = dry_run
    
    def execute(self, node: ASTNode, context: Optional[ExecutionContext] = None) -> Any:
        """
        Execute an AST node with given context.
        
        Args:
            node: AST node to execute
            context: Execution context (creates new if None)
            
        Returns:
            Execution result (depends on node type)
            
        Raises:
            ExecutionError: If execution fails
        """
        if context is None:
            context = ExecutionContext(
                max_iterations=self.max_iterations,
                dry_run=self.dry_run
            )
        
        # Record trace entry if tracing enabled
        node_type = type(node).__name__
        if self.trace:
            self.trace.record(TraceEvent(
                node_type=node_type,
                phase="enter",
                context_snapshot=create_snapshot(context)
            ))
        
        # Dispatch to appropriate handler
        try:
            if isinstance(node, IfNode):
                result = self.execute_if(node, context)
            elif isinstance(node, WhileNode):
                result = self.execute_while(node, context)
            elif isinstance(node, ForNode):
                result = self.execute_for(node, context)
            elif isinstance(node, ExpressionNode):
                result = self.evaluate_expression(node, context)
            elif isinstance(node, StepNode):
                result = self.execute_step(node, context)
            elif isinstance(node, ModuleNode):
                result = self.execute_module(node, context)
            elif isinstance(node, TaskDefNode):
                result = self.execute_task(node, context)
            elif isinstance(node, list):
                result = self.execute_block(node, context)
            else:
                raise ExecutionError(f"Unsupported node type: {type(node).__name__}", node)
            
            # Record trace exit if tracing enabled
            if self.trace:
                self.trace.record(TraceEvent(
                    node_type=node_type,
                    phase="exit",
                    context_snapshot=create_snapshot(context),
                    result=result
                ))
            
            return result
        except Exception as e:
            # Record trace exit with error if tracing enabled
            if self.trace:
                self.trace.record(TraceEvent(
                    node_type=node_type,
                    phase="exit",
                    context_snapshot=create_snapshot(context),
                    metadata={"error": str(e)}
                ))
            raise
    
    def execute_if(self, node: IfNode, context: ExecutionContext) -> Any:
        """
        Execute if/else if/else statement.
        
        Args:
            node: IfNode to execute
            context: Execution context
            
        Returns:
            Result of executed branch (or None)
        """
        # Evaluate main condition
        if self.evaluate_condition(node.condition, context):
            return self.execute_block(node.body, context)
        
        # Try elif blocks
        for elif_condition, elif_body in node.elif_blocks:
            if self.evaluate_condition(elif_condition, context):
                return self.execute_block(elif_body, context)
        
        # Execute else block if present
        if node.else_body:
            return self.execute_block(node.else_body, context)
        
        return None
    
    def execute_while(self, node: WhileNode, context: ExecutionContext) -> Any:
        """
        Execute while loop with iteration limit.
        
        Args:
            node: WhileNode to execute
            context: Execution context
            
        Returns:
            Result of last iteration (or None)
            
        Raises:
            MaxIterationsExceeded: If loop exceeds max_iterations
        """
        iterations = 0
        result = None
        
        while self.evaluate_condition(node.condition, context):
            iterations += 1
            if iterations > context.max_iterations:
                raise MaxIterationsExceeded(
                    f"While loop exceeded maximum iterations ({context.max_iterations})",
                    node
                )
            
            # Execute body in child scope
            result = self.execute_block(node.body, context.create_child_scope())
        
        return result
    
    def execute_for(self, node: ForNode, context: ExecutionContext) -> Any:
        """
        Execute for loop over iterable.
        
        Args:
            node: ForNode to execute
            context: Execution context
            
        Returns:
            Result of last iteration (or None)
            
        Raises:
            MaxIterationsExceeded: If loop exceeds max_iterations
        """
        # Evaluate iterable expression
        iterable = self.evaluate_expression(node.iterable, context)
        
        if not hasattr(iterable, '__iter__'):
            raise ExecutionError(
                f"For loop iterable must be iterable, got {type(iterable).__name__}",
                node
            )
        
        iterations = 0
        result = None
        
        for item in iterable:
            iterations += 1
            if iterations > context.max_iterations:
                raise MaxIterationsExceeded(
                    f"For loop exceeded maximum iterations ({context.max_iterations})",
                    node
                )
            
            # Create child scope and bind iterator variable
            loop_context = context.create_child_scope()
            loop_context.set(node.iterator, item)
            
            # Execute body
            result = self.execute_block(node.body, loop_context)
        
        return result
    
    def execute_block(self, block: List[ASTNode], context: ExecutionContext) -> Any:
        """
        Execute a block of statements.
        
        Args:
            block: List of AST nodes
            context: Execution context
            
        Returns:
            Result of last statement (or None)
        """
        result = None
        for statement in block:
            result = self.execute(statement, context)
        return result
    
    def execute_step(self, node: StepNode, context: ExecutionContext) -> Any:
        """
        Execute a step node with basic assignment and return support.
        
        Supports two patterns:
        1. "set VARIABLE to ATOM" - Variable assignment
        2. "return ATOM" - Return value from task
        
        Where ATOM is: string literal, integer literal, boolean, or variable name.
        
        Respects dry-run mode: assignments are skipped (no mutations).
        
        Args:
            node: StepNode to execute
            context: Execution context
            
        Returns:
            Value for return statements, None for assignments
            
        Raises:
            CapabilityError: If required capability not granted
            ExecutionError: If expression cannot be evaluated
        """
        action = node.action.strip() if hasattr(node, "action") else ""
        
        # Pattern: set VARIABLE to VALUE
        m = re.match(r"set\s+(\w+)\s+to\s+(.+)", action)
        if m:
            var_name, expr_text = m.groups()
            value = self._eval_atom(expr_text.strip(), context)
            
            # Respect dry-run mode: skip mutations
            if not self.dry_run and not context.dry_run:
                context.set(var_name, value)
            # In dry-run mode, trace the intent but don't mutate
            elif self.trace:
                self.trace.record(TraceEvent(
                    node_type="DryRunAssignment",
                    phase="would_set",
                    context_snapshot={var_name: value}
                ))
            
            return None
        
        # Pattern: return VALUE
        m = re.match(r"return\s+(.+)", action)
        if m:
            expr_text = m.group(1)
            
            # In dry-run mode, handle missing variables gracefully
            if self.dry_run or context.dry_run:
                try:
                    return self._eval_atom(expr_text.strip(), context)
                except NameError:
                    # Variable doesn't exist (assignment was skipped in dry-run)
                    # Return None as placeholder
                    return None
            
            return self._eval_atom(expr_text.strip(), context)
        
        # Original capability-gated no-op behavior
        if hasattr(node, 'function_name'):
            required_capability = self._get_required_capability(node.function_name)
            if required_capability and not context.has_capability(required_capability):
                raise CapabilityError(
                    required_capability,
                    f"call to {node.function_name}"
                )
        
        return None
    
    def _eval_atom(self, text: str, context: ExecutionContext) -> Any:
        """
        Evaluate a simple atomic expression or basic arithmetic.
        
        Supports:
        - String literals: "text"
        - Integer literals: 42
        - Boolean literals: true, false
        - Variable references: variable_name
        - Simple arithmetic: var + 10, total + v1, score - 5
        
        Uses existing evaluate_expression infrastructure for arithmetic (sandbox-safe).
        
        Args:
            text: Expression text to evaluate
            context: Execution context for variable lookup
            
        Returns:
            Evaluated value
            
        Raises:
            ExecutionError: If expression is unsupported
        """
        text = text.strip()
        
        # String literal
        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        
        # Integer literal
        if text.isdigit() or (text.startswith('-') and text[1:].isdigit()):
            return int(text)
        
        # Boolean literal
        if text == "true":
            return True
        if text == "false":
            return False
        
        # Variable reference
        if text.isidentifier():
            return context.get(text)
        
        # Simple arithmetic expression (delegate to parser + evaluator)
        # This reuses existing sandbox-safe arithmetic evaluation
        if any(op in text for op in ['+', '-', '*', '/', '<', '>', '=']):
            try:
                # Parse expression into AST node
                from ape.tokenizer.tokenizer import Tokenizer
                from ape.parser.parser import Parser
                
                # Create minimal task wrapper for parsing
                wrapper = f"task t:\n    steps:\n        if {text}:\n            - noop"
                tokenizer = Tokenizer(wrapper)
                tokens = tokenizer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                
                # Extract condition expression from if statement
                expr_node = ast.tasks[0].steps[0].condition
                
                # Evaluate using existing infrastructure
                return self.evaluate_expression(expr_node, context)
            except Exception as e:
                raise ExecutionError(f"Cannot evaluate expression '{text}': {e}")
        
        raise ExecutionError(f"Unsupported expression in step: {text}")
    
    def execute_module(self, node: ModuleNode, context: ExecutionContext) -> Any:
        """
        Execute a module node.
        
        For now, this is a placeholder that executes tasks in the module.
        
        Args:
            node: ModuleNode to execute
            context: Execution context
            
        Returns:
            Result of executing module tasks
        """
        # Execute all tasks in module
        result = None
        if hasattr(node, 'tasks'):
            for task in node.tasks:
                result = self.execute(task, context)
        return result
    
    def execute_task(self, node: TaskDefNode, context: ExecutionContext) -> Any:
        """
        Execute a task definition node.
        
        For now, this executes the task's steps.
        
        Args:
            node: TaskDefNode to execute
            context: Execution context
            
        Returns:
            Result of executing task steps
        """
        # Execute task steps
        if hasattr(node, 'steps') and node.steps:
            return self.execute_block(node.steps, context)
        return None
    
    def _get_required_capability(self, function_name: str) -> Optional[str]:
        """
        Get required capability for a function call.
        
        Args:
            function_name: Name of function being called
            
        Returns:
            Required capability name, or None if no capability needed
        """
        # Standard library functions don't require capabilities
        if self._is_stdlib_call(function_name):
            return None
        
        # Map function names to required capabilities
        # This is a simple mapping for v0.3.0
        capability_map = {
            'read_file': 'io.read',
            'write_file': 'io.write',
            'print': 'io.stdout',
            'read_line': 'io.stdin',
            'exit': 'sys.exit',
        }
        return capability_map.get(function_name)
    
    def _is_stdlib_call(self, function_name: str) -> bool:
        """
        Check if a function call is a stdlib intrinsic.
        
        Args:
            function_name: Name of function (e.g., "std.math.abs_value")
            
        Returns:
            True if function is a stdlib intrinsic, False otherwise
        """
        if not function_name.startswith('std.'):
            return False
        
        parts = function_name.split('.')
        if len(parts) != 3:
            return False
        
        module_path = f"{parts[0]}.{parts[1]}"
        return module_path in self.STDLIB_MODULES
    
    def _call_stdlib_function(self, function_name: str, args: List[Any]) -> Any:
        """
        Call a stdlib intrinsic function.
        
        Args:
            function_name: Full function name (e.g., "std.math.abs_value")
            args: Arguments to pass to function
            
        Returns:
            Result of function call
            
        Raises:
            ExecutionError: If function not found or call fails
        """
        parts = function_name.split('.')
        if len(parts) != 3:
            raise ExecutionError(f"Invalid stdlib function name: {function_name}")
        
        module_path = f"{parts[0]}.{parts[1]}"
        func_name = parts[2]
        
        module = self.STDLIB_MODULES.get(module_path)
        if module is None:
            raise ExecutionError(f"Unknown stdlib module: {module_path}")
        
        func = getattr(module, func_name, None)
        if func is None:
            raise ExecutionError(f"Unknown stdlib function: {func_name} in {module_path}")
        
        try:
            return func(*args)
        except (TypeError, ValueError) as e:
            raise ExecutionError(f"Error calling {function_name}: {e}")
    
    def evaluate_condition(self, expr: ExpressionNode, context: ExecutionContext) -> bool:
        """
        Evaluate condition expression to boolean.
        
        Args:
            expr: Expression to evaluate
            context: Execution context
            
        Returns:
            Boolean result
            
        Raises:
            ExecutionError: If expression doesn't evaluate to boolean
        """
        result = self.evaluate_expression(expr, context)
        
        if not isinstance(result, bool):
            raise ExecutionError(
                f"Condition must evaluate to boolean, got {type(result).__name__}",
                expr
            )
        
        return result
    
    def evaluate_expression(self, expr: ExpressionNode, context: ExecutionContext) -> Any:
        """
        Evaluate an expression to a value.
        
        Supports:
        - Literals (values)
        - Identifiers (variable lookup)
        - Binary operations (+, -, *, /, <, >, ==, !=, etc.)
        
        Args:
            expr: Expression to evaluate
            context: Execution context
            
        Returns:
            Evaluated value
        """
        # Literal value
        if expr.value is not None:
            return expr.value
        
        # Variable reference
        if expr.identifier:
            return context.get(expr.identifier)
        
        # Binary operation
        if expr.operator and expr.left and expr.right:
            left_val = self.evaluate_expression(expr.left, context)
            right_val = self.evaluate_expression(expr.right, context)
            
            return self._apply_operator(expr.operator, left_val, right_val, expr)
        
        raise ExecutionError("Invalid expression: no value, identifier, or operation", expr)
    
    def _apply_operator(self, op: str, left: Any, right: Any, node: ASTNode) -> Any:
        """
        Apply binary operator to operands.
        
        Args:
            op: Operator string (+, -, *, /, <, >, ==, etc.)
            left: Left operand
            right: Right operand
            node: AST node for error reporting
            
        Returns:
            Result of operation
            
        Raises:
            ExecutionError: If operator is unsupported or operands invalid
        """
        try:
            # Arithmetic operators
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right
            elif op == '%':
                return left % right
            
            # Comparison operators
            elif op == '<':
                return left < right
            elif op == '>':
                return left > right
            elif op == '<=':
                return left <= right
            elif op == '>=':
                return left >= right
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            
            # Logical operators
            elif op == 'and':
                return left and right
            elif op == 'or':
                return left or right
            
            else:
                raise ExecutionError(f"Unsupported operator: {op}", node)
                
        except Exception as e:
            raise ExecutionError(
                f"Error applying operator {op} to {type(left).__name__} and {type(right).__name__}: {e}",
                node
            )

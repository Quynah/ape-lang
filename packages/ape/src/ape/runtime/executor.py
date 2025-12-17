"""
Ape Runtime Executor

AST-based execution engine without using exec() or eval().
Deterministic, sandbox-safe execution of Ape control flow structures.
"""

import re
from typing import Any, List, Optional
from ape.parser.ast_nodes import (
    ASTNode, IfNode, WhileNode, ForNode, ExpressionNode,
    StepNode, TaskDefNode, ModuleNode, FunctionDefNode, ReturnNode,
    AssignmentNode, ListNode, TupleNode, IndexAccessNode
)
from ape.runtime.context import ExecutionContext, ExecutionError, MaxIterationsExceeded
from ape.runtime.trace import TraceCollector, TraceEvent, create_snapshot
from ape.errors import CapabilityError
from ape.std import logic, collections, strings, math
from ape.std import datetime as datetime_module
from ape.std import json as json_module
from ape.types import ApeList, ApeTuple


class ReturnValue(Exception):
    """Exception used to implement return statements in functions."""
    def __init__(self, value):
        self.value = value
        super().__init__()


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
        'std.datetime': datetime_module,
        'json': json_module,
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
            elif isinstance(node, FunctionDefNode):
                result = self.execute_function_def(node, context)
            elif isinstance(node, ReturnNode):
                result = self.execute_return(node, context)
            elif isinstance(node, AssignmentNode):
                result = self.execute_assignment(node, context)
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
            
            # Execute body in same context (variables must persist across iterations)
            result = self.execute_block(node.body, context)
        
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
    
    def execute_function_def(self, node: FunctionDefNode, context: ExecutionContext) -> None:
        """
        Register a function definition in the context.
        
        Args:
            node: FunctionDefNode to register
            context: Execution context
        """
        # Store function definition in context
        context.set(node.name, node)
        return None
    
    def execute_return(self, node: ReturnNode, context: ExecutionContext) -> Any:
        """
        Execute return statement.
        
        Args:
            node: ReturnNode to execute
            context: Execution context
            
        Returns:
            Never returns normally - raises ReturnValue exception
            
        Raises:
            ReturnValue: Contains the return value(s)
        """
        # Evaluate all return values
        values = [self.evaluate_expression(expr, context) for expr in node.values]
        
        # Single value return
        if len(values) == 1:
            raise ReturnValue(values[0])
        
        # Tuple return (multiple values)
        elif len(values) > 1:
            raise ReturnValue(ApeTuple(tuple(values)))
        
        # Empty return
        else:
            raise ReturnValue(None)
    
    def execute_assignment(self, node: AssignmentNode, context: ExecutionContext) -> None:
        """
        Execute assignment statement.
        
        Supports:
        - Single assignment: x = 5
        - Tuple destructuring: a, b, c = fn()
        
        Args:
            node: AssignmentNode to execute
            context: Execution context
            
        Raises:
            ExecutionError: If tuple destructuring arity mismatch
        """
        # Evaluate right-hand side
        value = self.evaluate_expression(node.value, context)
        
        # Single target
        if len(node.targets) == 1:
            if not self.dry_run and not context.dry_run:
                context.set(node.targets[0], value)
        
        # Tuple destructuring
        else:
            # Value must be tuple or ApeList with matching arity
            if isinstance(value, ApeTuple):
                if len(value) != len(node.targets):
                    raise ExecutionError(
                        f"Tuple destructuring arity mismatch: {len(node.targets)} targets, "
                        f"{len(value)} values",
                        node
                    )
                
                if not self.dry_run and not context.dry_run:
                    for i, target in enumerate(node.targets):
                        context.set(target, value[i])
            
            elif isinstance(value, ApeList):
                if len(value) != len(node.targets):
                    raise ExecutionError(
                        f"List destructuring arity mismatch: {len(node.targets)} targets, "
                        f"{len(value)} values",
                        node
                    )
                
                if not self.dry_run and not context.dry_run:
                    for i, target in enumerate(node.targets):
                        context.set(target, value[i])
            
            else:
                raise ExecutionError(
                    f"Cannot destructure non-tuple/non-list value of type {type(value).__name__}",
                    node
                )
        
        return None
    
    def execute_block(self, block: List[ASTNode], context: ExecutionContext) -> Any:
        """
        Execute a block of statements.
        
        Args:
            block: List of AST nodes
            context: Execution context
            
        Returns:
            Result of last statement (or None)
            
        Note:
            ReturnValue exceptions propagate up (not caught here)
        """
        result = None
        i = 0
        while i < len(block):
            statement = block[i]
            
            # Check if this is part of an if-elif-else chain
            if isinstance(statement, StepNode) and hasattr(statement, 'action'):
                action = statement.action.strip()
                
                # If we find an IF statement, look ahead for ELSE IF / ELSE
                if action.startswith("if ") and hasattr(statement, 'substeps'):
                    # Execute the if and collect elif/else blocks
                    if_executed = False
                    condition_text = action[3:].rstrip(':').strip()
                    
                    if self._eval_condition_simple(condition_text, context):
                        # Execute if body as a block (allows nested if statements)
                        result = self.execute_block(statement.substeps, context)
                        if_executed = True
                    
                    # Look ahead for else if / else
                    j = i + 1
                    while j < len(block) and not if_executed:
                        if j >= len(block):
                            break
                        next_statement = block[j]
                        if not isinstance(next_statement, StepNode) or not hasattr(next_statement, 'action'):
                            break
                        
                        next_action = next_statement.action.strip()
                        
                        # Check for else if
                        if next_action.startswith("else if "):
                            elif_condition = next_action[8:].rstrip(':').strip()
                            if self._eval_condition_simple(elif_condition, context):
                                result = self.execute_block(next_statement.substeps, context)
                                if_executed = True
                            j += 1
                        # Check for else (handle both "else:" and "else :")
                        elif next_action.rstrip(':').strip() == "else":
                            result = self.execute_block(next_statement.substeps, context)
                            if_executed = True
                            j += 1
                            break
                        else:
                            break
                    
                    # Skip past all the elif/else we just processed
                    i = j
                    continue
            
            # Regular statement execution
            result = self.execute(statement, context)
            i += 1
        
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
        
        # Regular step patterns below...
        
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
            
            # Check if it's a tuple return (contains comma outside of strings)
            if ',' in expr_text:
                # Parse as tuple - split by comma and evaluate each part
                parts = [part.strip() for part in expr_text.split(',')]
                
                # In dry-run mode, handle missing variables gracefully
                if self.dry_run or context.dry_run:
                    values = []
                    for part in parts:
                        try:
                            values.append(self._eval_atom(part, context))
                        except NameError:
                            values.append(None)
                    raise ReturnValue(ApeTuple(tuple(values)))
                
                # Normal execution - raise ReturnValue exception to exit task
                values = [self._eval_atom(part, context) for part in parts]
                raise ReturnValue(ApeTuple(tuple(values)))
            
            # Single value return
            # In dry-run mode, handle missing variables gracefully
            if self.dry_run or context.dry_run:
                try:
                    value = self._eval_atom(expr_text.strip(), context)
                    raise ReturnValue(value)
                except NameError:
                    # Variable doesn't exist (assignment was skipped in dry-run)
                    # Return None as placeholder
                    raise ReturnValue(None)
            
            value = self._eval_atom(expr_text.strip(), context)
            raise ReturnValue(value)
        
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
                
                # Create minimal assignment wrapper for parsing expressions
                # This allows parsing of any expression without needing conditional context
                wrapper = f"fn dummy():\n    x = {text}\n    return x"
                tokenizer = Tokenizer(wrapper)
                tokens = tokenizer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                
                # Extract expression from assignment
                expr_node = ast.functions[0].body[0].value
                
                # Evaluate using existing infrastructure
                return self.evaluate_expression(expr_node, context)
            except Exception as e:
                raise ExecutionError(f"Cannot evaluate expression '{text}': {e}")
        
        raise ExecutionError(f"Unsupported expression in step: {text}")
    
    def _eval_condition_simple(self, condition_text: str, context: ExecutionContext) -> bool:
        """
        Evaluate a simple condition expression for if statements in task steps.
        
        Supports basic comparisons: <, >, <=, >=, ==, !=, equals
        
        Args:
            condition_text: Condition expression text (e.g., "x < 10", "y equals true")
            context: Execution context
            
        Returns:
            Boolean result of condition
        """
        # Handle "equals" keyword (APE syntax)
        if " equals " in condition_text:
            parts = condition_text.split(" equals ")
            if len(parts) == 2:
                left = self._eval_atom(parts[0].strip(), context)
                right = self._eval_atom(parts[1].strip(), context)
                return left == right
        
        # Handle comparison operators
        for op in ['<=', '>=', '==', '!=', '<', '>']:
            if op in condition_text:
                parts = condition_text.split(op)
                if len(parts) == 2:
                    left = self._eval_atom(parts[0].strip(), context)
                    right = self._eval_atom(parts[1].strip(), context)
                    
                    if op == '<':
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
        
        # If no operator found, evaluate as boolean
        return bool(self._eval_atom(condition_text, context))
    
    def execute_module(self, node: ModuleNode, context: ExecutionContext) -> Any:
        """
        Execute a module node.
        
        Registers all functions, then executes tasks.
        
        Args:
            node: ModuleNode to execute
            context: Execution context
            
        Returns:
            Result of executing module tasks
        """
        # Register all function definitions
        if hasattr(node, 'functions'):
            for func in node.functions:
                self.execute(func, context)
        
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
            try:
                self.execute_block(node.steps, context)
                # If no return statement, return None
                return None
            except ReturnValue as ret:
                return ret.value
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
        - Function calls
        - Lists
        - Tuples
        - Index access
        
        Args:
            expr: Expression to evaluate
            context: Execution context
            
        Returns:
            Evaluated value
        """
        # List literal
        if expr.list_node:
            elements = [self.evaluate_expression(e, context) for e in expr.list_node.elements]
            return ApeList(elements)
        
        # Tuple literal
        if expr.tuple_node:
            elements = [self.evaluate_expression(e, context) for e in expr.tuple_node.elements]
            return ApeTuple(tuple(elements))
        
        # Index access
        if expr.index_access:
            target = self.evaluate_expression(expr.index_access.target, context)
            index = self.evaluate_expression(expr.index_access.index, context)
            
            # Validate index is integer
            if not isinstance(index, int):
                raise ExecutionError(
                    f"Index must be integer, got {type(index).__name__}",
                    expr
                )
            
            # Perform index access
            try:
                return target[index]
            except (IndexError, TypeError) as e:
                raise ExecutionError(str(e), expr)
        
        # Function call
        if expr.function_name:
            return self._call_function(expr.function_name, expr.arguments, context, expr)
        
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
    
    def _call_function(self, name: str, arg_exprs: List[ExpressionNode], 
                      context: ExecutionContext, node: ASTNode) -> Any:
        """
        Call a function (user-defined or stdlib).
        
        Args:
            name: Function name
            arg_exprs: Argument expressions
            context: Execution context
            node: AST node for error reporting
            
        Returns:
            Function result
            
        Raises:
            ExecutionError: If function not found or call fails
        """
        # Evaluate arguments
        args = [self.evaluate_expression(arg, context) for arg in arg_exprs]
        
        # Check for stdlib call
        if self._is_stdlib_call(name):
            return self._call_stdlib_function(name, args)
        
        # Check for built-in operations
        if name == 'len':
            if len(args) != 1:
                raise ExecutionError(f"len() takes exactly 1 argument ({len(args)} given)", node)
            obj = args[0]
            if hasattr(obj, '__len__'):
                return len(obj)
            raise ExecutionError(f"Object of type {type(obj).__name__} has no len()", node)
        
        elif name == 'map':
            if len(args) != 2:
                raise ExecutionError(f"map() takes exactly 2 arguments ({len(args)} given)", node)
            lst, fn = args
            if not isinstance(lst, ApeList):
                raise ExecutionError(f"map() first argument must be List, got {type(lst).__name__}", node)
            # fn should be a function - for now assume it's a FunctionDefNode stored in context
            if isinstance(fn, FunctionDefNode):
                result_items = []
                for item in lst:
                    result_items.append(self._call_user_function(fn, [item], context, node))
                return ApeList(result_items)
            raise ExecutionError("map() second argument must be a function", node)
        
        elif name == 'filter':
            if len(args) != 2:
                raise ExecutionError(f"filter() takes exactly 2 arguments ({len(args)} given)", node)
            lst, fn = args
            if not isinstance(lst, ApeList):
                raise ExecutionError(f"filter() first argument must be List, got {type(lst).__name__}", node)
            if isinstance(fn, FunctionDefNode):
                result_items = []
                for item in lst:
                    if self._call_user_function(fn, [item], context, node):
                        result_items.append(item)
                return ApeList(result_items)
            raise ExecutionError("filter() second argument must be a function", node)
        
        elif name == 'reduce':
            if len(args) != 3:
                raise ExecutionError(f"reduce() takes exactly 3 arguments ({len(args)} given)", node)
            lst, initial, fn = args
            if not isinstance(lst, ApeList):
                raise ExecutionError(f"reduce() first argument must be List, got {type(lst).__name__}", node)
            if isinstance(fn, FunctionDefNode):
                accumulator = initial
                for item in lst:
                    accumulator = self._call_user_function(fn, [accumulator, item], context, node)
                return accumulator
            raise ExecutionError("reduce() third argument must be a function", node)
        
        # User-defined function
        try:
            func_def = context.get(name)
        except NameError:
            func_def = None
        
        if func_def is None:
            raise ExecutionError(f"Undefined function: {name}", node)
        
        if not isinstance(func_def, FunctionDefNode):
            raise ExecutionError(f"{name} is not a function", node)
        
        return self._call_user_function(func_def, args, context, node)
    
    def _call_user_function(self, func_def: FunctionDefNode, args: List[Any],
                           context: ExecutionContext, node: ASTNode) -> Any:
        """
        Call a user-defined function.
        
        Args:
            func_def: Function definition node
            args: Evaluated arguments
            context: Execution context
            node: AST node for error reporting
            
        Returns:
            Function result
            
        Raises:
            ExecutionError: If arity mismatch or execution fails
        """
        # Check arity
        if len(args) != len(func_def.parameters):
            raise ExecutionError(
                f"Function {func_def.name}() takes {len(func_def.parameters)} "
                f"arguments ({len(args)} given)",
                node
            )
        
        # Create new scope for function
        func_context = context.create_child_scope()
        
        # Bind parameters
        for param, arg in zip(func_def.parameters, args):
            func_context.set(param, arg)
        
        # Execute function body
        try:
            self.execute_block(func_def.body, func_context)
            # If no return statement, return None
            return None
        except ReturnValue as ret:
            return ret.value
    
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
                # Special handling for list concatenation
                if isinstance(left, ApeList) and isinstance(right, ApeList):
                    return left + right
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
            
            # Membership test
            elif op == 'in':
                return left in right
            
            else:
                raise ExecutionError(f"Unsupported operator: {op}", node)
                
        except Exception as e:
            raise ExecutionError(
                f"Error applying operator {op} to {type(left).__name__} and {type(right).__name__}: {e}",
                node
            )

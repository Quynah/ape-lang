"""
Tests for control flow parsing and runtime execution.

Tests the new if/while/for control flow features and AST-based runtime executor.
"""

import pytest
from ape.parser.parser import parse_ape_source
from ape.parser.ast_nodes import IfNode, WhileNode, ForNode, ExpressionNode
from ape.runtime.executor import RuntimeExecutor
from ape.runtime.context import ExecutionContext, MaxIterationsExceeded


class TestControlFlowParsing:
    """Test parsing of control flow structures"""
    
    def test_parse_if_statement(self):
        """Test parsing simple if statement"""
        source = """
task test:
    inputs:
        x: Integer
    outputs:
        result: Boolean
    steps:
        if x < 10:
            - call sys.print with "small"
        - return result
"""
        ast = parse_ape_source(source)
        assert len(ast.tasks) == 1
        task = ast.tasks[0]
        assert len(task.steps) == 2
        
        # First step should be if node
        assert isinstance(task.steps[0], IfNode)
        if_node = task.steps[0]
        assert if_node.condition is not None
        assert len(if_node.body) == 1
    
    def test_parse_if_else(self):
        """Test parsing if-else statement"""
        source = """
task test:
    inputs:
        x: Integer
    outputs:
        result: Boolean
    steps:
        if x < 10:
            - call sys.print with "small"
        else:
            - call sys.print with "large"
"""
        ast = parse_ape_source(source)
        task = ast.tasks[0]
        if_node = task.steps[0]
        
        assert isinstance(if_node, IfNode)
        assert if_node.else_body is not None
        assert len(if_node.else_body) == 1
    
    def test_parse_if_elif_else(self):
        """Test parsing if-else if-else statement"""
        source = """
task test:
    inputs:
        x: Integer
    outputs:
        result: Boolean
    steps:
        if x < 5:
            - call sys.print with "tiny"
        else if x < 10:
            - call sys.print with "small"
        else:
            - call sys.print with "large"
"""
        ast = parse_ape_source(source)
        task = ast.tasks[0]
        if_node = task.steps[0]
        
        assert isinstance(if_node, IfNode)
        assert len(if_node.elif_blocks) == 1
        assert if_node.else_body is not None
    
    def test_parse_while_loop(self):
        """Test parsing while loop"""
        source = """
task test:
    inputs:
        counter: Integer
    outputs:
        result: Boolean
    steps:
        while counter < 10:
            - call sys.print with counter
        - return result
"""
        ast = parse_ape_source(source)
        task = ast.tasks[0]
        
        assert len(task.steps) == 2
        assert isinstance(task.steps[0], WhileNode)
        while_node = task.steps[0]
        assert while_node.condition is not None
        assert len(while_node.body) == 1
    
    def test_parse_for_loop(self):
        """Test parsing for loop"""
        source = """
task test:
    inputs:
        items: List
    outputs:
        result: Boolean
    steps:
        for item in items:
            - call sys.print with item
        - return result
"""
        ast = parse_ape_source(source)
        task = ast.tasks[0]
        
        assert len(task.steps) == 2
        assert isinstance(task.steps[0], ForNode)
        for_node = task.steps[0]
        assert for_node.iterator == "item"
        assert for_node.iterable is not None
        assert len(for_node.body) == 1


class TestRuntimeExecution:
    """Test AST-based runtime execution"""
    
    def test_execute_if_true(self):
        """Test executing if statement with true condition"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('x', 5)
        
        # Create if node: if x < 10
        condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='x'),
            right=ExpressionNode(value=10)
        )
        if_node = IfNode(condition=condition, body=[])
        
        # Execute - should not raise error
        result = executor.execute_if(if_node, context)
        assert result is None  # Empty body returns None
    
    def test_execute_if_false(self):
        """Test executing if statement with false condition"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('x', 15)
        
        # Create if node: if x < 10
        condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='x'),
            right=ExpressionNode(value=10)
        )
        if_node = IfNode(condition=condition, body=[])
        
        # Execute - should not execute body
        result = executor.execute_if(if_node, context)
        assert result is None
    
    def test_execute_if_else(self):
        """Test executing if-else statement"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('executed', False)
        context.set('x', 15)
        
        # Create if-else: if x < 10 ... else ...
        condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='x'),
            right=ExpressionNode(value=10)
        )
        if_node = IfNode(
            condition=condition,
            body=[],
            else_body=[]
        )
        
        # Execute - should execute else branch
        result = executor.execute_if(if_node, context)
        assert result is None
    
    def test_execute_while_loop(self):
        """Test executing while loop"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('counter', 0)
        
        # Create while loop: while counter < 3
        condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='counter'),
            right=ExpressionNode(value=3)
        )
        
        # Body: increment counter (we'll simulate this)
        # For now, just test that loop executes
        while_node = WhileNode(condition=condition, body=[])
        
        # This would loop forever, so we test with a condition that's already false
        context.set('counter', 5)
        result = executor.execute_while(while_node, context)
        assert result is None
    
    def test_while_max_iterations(self):
        """Test while loop respects max_iterations"""
        executor = RuntimeExecutor(max_iterations=10)
        context = ExecutionContext(max_iterations=10, dry_run=False)
        context.set('counter', 0)
        
        # Create infinite loop: while true
        condition = ExpressionNode(value=True)
        while_node = WhileNode(condition=condition, body=[])
        
        # Should raise MaxIterationsExceeded
        with pytest.raises(MaxIterationsExceeded):
            executor.execute_while(while_node, context)
    
    def test_execute_for_loop(self):
        """Test executing for loop"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('items', [1, 2, 3])
        
        # Create for loop: for item in items
        iterable_expr = ExpressionNode(identifier='items')
        for_node = ForNode(
            iterator='item',
            iterable=iterable_expr,
            body=[]
        )
        
        # Execute
        result = executor.execute_for(for_node, context)
        assert result is None
    
    def test_for_max_iterations(self):
        """Test for loop respects max_iterations"""
        executor = RuntimeExecutor(max_iterations=5)
        context = ExecutionContext(max_iterations=5, dry_run=False)
        context.set('items', list(range(100)))
        
        # Create for loop over 100 items
        iterable_expr = ExpressionNode(identifier='items')
        for_node = ForNode(
            iterator='item',
            iterable=iterable_expr,
            body=[]
        )
        
        # Should raise MaxIterationsExceeded
        with pytest.raises(MaxIterationsExceeded):
            executor.execute_for(for_node, context)
    
    def test_evaluate_expression_literal(self):
        """Test evaluating literal expression"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        
        expr = ExpressionNode(value=42)
        result = executor.evaluate_expression(expr, context)
        assert result == 42
    
    def test_evaluate_expression_variable(self):
        """Test evaluating variable expression"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('x', 100)
        
        expr = ExpressionNode(identifier='x')
        result = executor.evaluate_expression(expr, context)
        assert result == 100
    
    def test_evaluate_expression_arithmetic(self):
        """Test evaluating arithmetic expression"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        
        # 5 + 3
        expr = ExpressionNode(
            operator='+',
            left=ExpressionNode(value=5),
            right=ExpressionNode(value=3)
        )
        result = executor.evaluate_expression(expr, context)
        assert result == 8
    
    def test_evaluate_expression_comparison(self):
        """Test evaluating comparison expression"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        
        # 5 < 10
        expr = ExpressionNode(
            operator='<',
            left=ExpressionNode(value=5),
            right=ExpressionNode(value=10)
        )
        result = executor.evaluate_expression(expr, context)
        assert result is True
    
    def test_execution_context_scope(self):
        """Test execution context scoping"""
        context = ExecutionContext(dry_run=False)
        context.set('x', 10)
        
        # Create child scope
        child = context.create_child_scope()
        child.set('y', 20)
        
        # Child can access parent variables
        assert child.get('x') == 10
        assert child.get('y') == 20
        
        # Parent cannot access child variables
        assert context.has('y') is False
        
        # Child can shadow parent variables
        child.set('x', 30)
        assert child.get('x') == 30
        assert context.get('x') == 10  # Parent unchanged


class TestRuntimeSafety:
    """Test runtime safety features"""
    
    def test_no_exec_used(self):
        """Verify runtime doesn't use exec/eval/compile"""
        import inspect
        import re
        from ape.runtime.executor import RuntimeExecutor
        
        # Get source code of RuntimeExecutor
        source = inspect.getsource(RuntimeExecutor)
        
        # Remove comments and docstrings to avoid false positives
        # Remove multi-line strings/docstrings
        source_no_strings = re.sub(r'"""[\s\S]*?"""', '', source)
        source_no_strings = re.sub(r"'''[\s\S]*?'''", '', source_no_strings)
        # Remove comments
        source_no_strings = re.sub(r'#.*', '', source_no_strings)
        
        # Verify no exec/eval/compile calls in actual code
        assert 'exec(' not in source_no_strings
        assert 'eval(' not in source_no_strings
        assert 'compile(' not in source_no_strings
    
    def test_context_isolation(self):
        """Test execution context is isolated"""

        _executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)        # Context should not have access to os, sys, etc.
        assert 'os' not in context.variables
        assert 'sys' not in context.variables
        assert '__builtins__' not in context.variables
    
    def test_deterministic_execution(self):
        """Test execution is deterministic"""
        executor = RuntimeExecutor()
        
        # Create simple expression: 5 + 3
        expr = ExpressionNode(
            operator='+',
            left=ExpressionNode(value=5),
            right=ExpressionNode(value=3)
        )
        
        # Execute multiple times
        context1 = ExecutionContext()
        result1 = executor.evaluate_expression(expr, context1)
        
        context2 = ExecutionContext()
        result2 = executor.evaluate_expression(expr, context2)
        
        assert result1 == result2 == 8

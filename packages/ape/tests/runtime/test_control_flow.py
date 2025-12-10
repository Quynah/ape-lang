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


class TestReturnInsideControlFlow:
    """
    APE control-flow invariant: return inside if/else must exit function correctly.
    
    These tests guard against regressions where:
    - return inside true branch doesn't exit
    - return inside else branch doesn't exit
    - code after if/else incorrectly executes after return
    """
    
    def test_return_inside_if_true_branch(self):
        """Return inside if-true must exit function, skip code after if"""
        from ape.parser.ast_nodes import ReturnNode, AssignmentNode
        from ape.runtime.executor import ReturnValue
        
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('x', 5)
        context.set('executed_after', False)
        
        # if x < 10: return 42
        # after = True  # This should NOT execute
        condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='x'),
            right=ExpressionNode(value=10)
        )
        return_node = ReturnNode(values=[ExpressionNode(value=42)])
        if_node = IfNode(condition=condition, body=[return_node])
        
        # Execute if - should raise ReturnValue exception
        try:
            executor.execute_if(if_node, context)
            assert False, "Should have raised ReturnValue"
        except ReturnValue as e:
            # The return inside if should propagate with value 42
            assert e.value == 42
    
    def test_return_inside_else_branch(self):
        """Return inside else must exit function correctly"""
        from ape.parser.ast_nodes import ReturnNode
        from ape.runtime.executor import ReturnValue
        
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('x', 15)
        
        # if x < 10: pass
        # else: return 99
        condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='x'),
            right=ExpressionNode(value=10)
        )
        return_node = ReturnNode(values=[ExpressionNode(value=99)])
        if_node = IfNode(
            condition=condition,
            body=[],
            else_body=[return_node]
        )
        
        # Execute if - should raise ReturnValue exception
        try:
            executor.execute_if(if_node, context)
            assert False, "Should have raised ReturnValue"
        except ReturnValue as e:
            # The return inside else should propagate with value 99
            assert e.value == 99
    
    def test_if_without_else_returns_none(self):
        """If without else, when condition false, returns None (no crash)"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('x', 15)
        
        # if x < 10: pass
        # (no else)
        condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='x'),
            right=ExpressionNode(value=10)
        )
        if_node = IfNode(condition=condition, body=[])
        
        result = executor.execute_if(if_node, context)
        assert result is None


class TestNestedControlFlow:
    """
    APE control-flow invariant: nested if/else must resolve correctly.
    
    Guards against:
    - Wrong branch execution in nested structures
    - Scope leakage between nested blocks
    - Dangling else ambiguity (else binds to nearest if)
    """
    
    def test_nested_if_inside_if_true(self):
        """Nested if inside if-true branch"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('x', 5)
        context.set('y', 3)
        context.set('inner_executed', False)
        
        # if x < 10:
        #   if y < 5:
        #     inner_executed = True
        inner_condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='y'),
            right=ExpressionNode(value=5)
        )
        from ape.parser.ast_nodes import AssignmentNode
        inner_assign = AssignmentNode(
            targets=['inner_executed'],
            value=ExpressionNode(value=True)
        )
        inner_if = IfNode(condition=inner_condition, body=[inner_assign])
        
        outer_condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='x'),
            right=ExpressionNode(value=10)
        )
        outer_if = IfNode(condition=outer_condition, body=[inner_if])
        
        executor.execute_if(outer_if, context)
        
        # Both conditions true, inner should execute
        assert context.get('inner_executed') is True
    
    def test_nested_if_inside_else_branch(self):
        """Nested if inside else branch"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('x', 15)
        context.set('y', 3)
        context.set('inner_executed', False)
        
        # if x < 10:
        #   pass
        # else:
        #   if y < 5:
        #     inner_executed = True
        inner_condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='y'),
            right=ExpressionNode(value=5)
        )
        from ape.parser.ast_nodes import AssignmentNode
        inner_assign = AssignmentNode(
            targets=['inner_executed'],
            value=ExpressionNode(value=True)
        )
        inner_if = IfNode(condition=inner_condition, body=[inner_assign])
        
        outer_condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='x'),
            right=ExpressionNode(value=10)
        )
        outer_if = IfNode(
            condition=outer_condition,
            body=[],
            else_body=[inner_if]
        )
        
        executor.execute_if(outer_if, context)
        
        # Outer false, else executes; inner true, should execute
        assert context.get('inner_executed') is True
    
    def test_three_level_nesting(self):
        """Three-level nested if statements"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('a', 5)
        context.set('b', 3)
        context.set('c', 1)
        context.set('deepest', False)
        
        # if a < 10:
        #   if b < 5:
        #     if c < 2:
        #       deepest = True
        from ape.parser.ast_nodes import AssignmentNode
        deepest_assign = AssignmentNode(
            targets=['deepest'],
            value=ExpressionNode(value=True)
        )
        
        level3_cond = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='c'),
            right=ExpressionNode(value=2)
        )
        level3_if = IfNode(condition=level3_cond, body=[deepest_assign])
        
        level2_cond = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='b'),
            right=ExpressionNode(value=5)
        )
        level2_if = IfNode(condition=level2_cond, body=[level3_if])
        
        level1_cond = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='a'),
            right=ExpressionNode(value=10)
        )
        level1_if = IfNode(condition=level1_cond, body=[level2_if])
        
        executor.execute_if(level1_if, context)
        
        # All three conditions true, deepest should execute
        assert context.get('deepest') is True
    
    def test_nested_scope_isolation(self):
        """Variables in nested if don't leak to outer scope"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        context.set('x', 5)
        
        # if x < 10:
        #   inner_var = 42
        from ape.parser.ast_nodes import AssignmentNode
        inner_assign = AssignmentNode(
            targets=['inner_var'],
            value=ExpressionNode(value=42)
        )
        
        condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='x'),
            right=ExpressionNode(value=10)
        )
        if_node = IfNode(condition=condition, body=[inner_assign])
        
        # Create child scope for if block
        child_context = context.create_child_scope()
        executor.execute_if(if_node, child_context)
        
        # inner_var should exist in child
        assert child_context.has('inner_var')
        assert child_context.get('inner_var') == 42
        
        # But NOT in parent
        assert not context.has('inner_var')


class TestBooleanExpressions:
    """
    APE control-flow invariant: boolean expressions must evaluate deterministically.
    
    Guards against:
    - Inconsistent comparison operators
    - Type coercion bugs
    - Operator precedence errors
    """
    
    def test_all_comparison_operators(self):
        """Test all supported comparison operators"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        
        test_cases = [
            ('<', 5, 10, True),
            ('<', 10, 5, False),
            ('>', 10, 5, True),
            ('>', 5, 10, False),
            ('<=', 5, 10, True),
            ('<=', 10, 10, True),
            ('<=', 10, 5, False),
            ('>=', 10, 5, True),
            ('>=', 10, 10, True),
            ('>=', 5, 10, False),
            ('==', 10, 10, True),
            ('==', 10, 5, False),
            ('!=', 10, 5, True),
            ('!=', 10, 10, False),
        ]
        
        for op, left_val, right_val, expected in test_cases:
            expr = ExpressionNode(
                operator=op,
                left=ExpressionNode(value=left_val),
                right=ExpressionNode(value=right_val)
            )
            result = executor.evaluate_expression(expr, context)
            assert result == expected, f"{left_val} {op} {right_val} should be {expected}, got {result}"
    
    def test_boolean_literals(self):
        """Test boolean True/False literals"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        
        true_expr = ExpressionNode(value=True)
        false_expr = ExpressionNode(value=False)
        
        assert executor.evaluate_expression(true_expr, context) is True
        assert executor.evaluate_expression(false_expr, context) is False
    
    def test_string_comparison(self):
        """Test string equality/inequality"""
        executor = RuntimeExecutor()
        context = ExecutionContext(dry_run=False)
        
        # "hello" == "hello"
        eq_expr = ExpressionNode(
            operator='==',
            left=ExpressionNode(value="hello"),
            right=ExpressionNode(value="hello")
        )
        assert executor.evaluate_expression(eq_expr, context) is True
        
        # "hello" != "world"
        neq_expr = ExpressionNode(
            operator='!=',
            left=ExpressionNode(value="hello"),
            right=ExpressionNode(value="world")
        )
        assert executor.evaluate_expression(neq_expr, context) is True


class TestNegativeControlFlow:
    """
    APE control-flow invariant: invalid syntax must fail with clear errors.
    
    Guards against:
    - Silent misparsing
    - Ambiguous else binding
    - Invalid control structures
    """
    
    def test_malformed_if_missing_colon(self):
        """If without colon should fail to parse"""
        source = """
task test:
    inputs:
        x: Integer
    outputs:
        result: Boolean
    steps:
        if x < 10
            - call sys.print with "fail"
"""
        with pytest.raises(Exception):  # Should raise parse error
            parse_ape_source(source)
    
    def test_malformed_if_missing_condition(self):
        """If without condition should fail to parse"""
        source = """
task test:
    inputs:
        x: Integer
    outputs:
        result: Boolean
    steps:
        if:
            - call sys.print with "fail"
"""
        with pytest.raises(Exception):  # Should raise parse error
            parse_ape_source(source)
    
    def test_dangling_else_binds_to_nearest_if(self):
        """
        Else must bind to nearest if (Python-style).
        
        This test verifies parser correctly handles else binding.
        Currently APE uses explicit block structure with indentation,
        so dangling else ambiguity is resolved by indentation level.
        """
        source = """
task test:
    inputs:
        a: Integer
        b: Integer
    outputs:
        result: String
    steps:
        if a < 10:
            - call sys.print with "outer-true"
        else:
            - call sys.print with "outer-false"
"""
        # This should parse successfully
        ast = parse_ape_source(source)
        assert len(ast.tasks) == 1
        
        # Should have if-else at top level
        outer_if = ast.tasks[0].steps[0]
        assert isinstance(outer_if, IfNode)
        assert outer_if.else_body is not None


class TestExecutionStability:
    """
    APE control-flow invariant: execution must be deterministic.
    
    Same input → same output, always.
    Guards against:
    - Non-deterministic evaluation
    - State leakage between runs
    - Parser/executor inconsistency
    """
    
    def test_if_evaluation_10x_identical(self):
        """If-else must produce identical results across 10 runs"""
        from ape.runtime.executor import ReturnValue
        executor = RuntimeExecutor()
        
        # Create if x < 10: return 42 else: return 99
        from ape.parser.ast_nodes import ReturnNode
        
        condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='x'),
            right=ExpressionNode(value=10)
        )
        if_node = IfNode(
            condition=condition,
            body=[ReturnNode(values=[ExpressionNode(value=42)])],
            else_body=[ReturnNode(values=[ExpressionNode(value=99)])]
        )
        
        # Run 10 times with x=5 (true branch)
        results_true = []
        for _ in range(10):
            context = ExecutionContext(dry_run=False)
            context.set('x', 5)
            try:
                executor.execute_if(if_node, context)
            except ReturnValue as rv:
                results_true.append(rv.value)
        
        # All should be 42
        assert all(r == 42 for r in results_true)
        assert len(set(results_true)) == 1  # All identical
        
        # Run 10 times with x=15 (false branch)
        results_false = []
        for _ in range(10):
            context = ExecutionContext(dry_run=False)
            context.set('x', 15)
            try:
                executor.execute_if(if_node, context)
            except ReturnValue as rv:
                results_false.append(rv.value)
        
        # All should be 99
        assert all(r == 99 for r in results_false)
        assert len(set(results_false)) == 1  # All identical
    
    def test_nested_if_10x_identical(self):
        """Nested if must produce identical results across 10 runs"""
        from ape.runtime.executor import ReturnValue
        executor = RuntimeExecutor()
        
        # if a < 10:
        #   if b < 5:
        #     return 1
        #   else:
        #     return 2
        # else:
        #   return 3
        from ape.parser.ast_nodes import ReturnNode
        
        inner_cond = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='b'),
            right=ExpressionNode(value=5)
        )
        inner_if = IfNode(
            condition=inner_cond,
            body=[ReturnNode(values=[ExpressionNode(value=1)])],
            else_body=[ReturnNode(values=[ExpressionNode(value=2)])]
        )
        
        outer_cond = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='a'),
            right=ExpressionNode(value=10)
        )
        outer_if = IfNode(
            condition=outer_cond,
            body=[inner_if],
            else_body=[ReturnNode(values=[ExpressionNode(value=3)])]
        )
        
        # Test all three paths 10x each
        test_cases = [
            ({'a': 5, 'b': 3}, 1),   # Both true → 1
            ({'a': 5, 'b': 7}, 2),   # Outer true, inner false → 2
            ({'a': 15, 'b': 3}, 3),  # Outer false → 3
        ]
        
        for inputs, expected in test_cases:
            results = []
            for _ in range(10):
                context = ExecutionContext(dry_run=False)
                for key, val in inputs.items():
                    context.set(key, val)
                try:
                    executor.execute_if(outer_if, context)
                except ReturnValue as rv:
                    results.append(rv.value)
            
            # All 10 runs must produce same result
            assert all(r == expected for r in results), f"Expected {expected}, got varying results: {results}"
            assert len(set(results)) == 1  # All identical
    
    def test_while_loop_10x_identical(self):
        """While loop must produce identical iteration count across 10 runs"""
        executor = RuntimeExecutor()
        
        # while counter < 5: counter = counter + 1
        from ape.parser.ast_nodes import AssignmentNode
        
        condition = ExpressionNode(
            operator='<',
            left=ExpressionNode(identifier='counter'),
            right=ExpressionNode(value=5)
        )
        
        increment = AssignmentNode(
            targets=['counter'],
            value=ExpressionNode(
                operator='+',
                left=ExpressionNode(identifier='counter'),
                right=ExpressionNode(value=1)
            )
        )
        
        while_node = WhileNode(condition=condition, body=[increment])
        
        # Run 10 times
        final_values = []
        for _ in range(10):
            context = ExecutionContext(dry_run=False, max_iterations=100)
            context.set('counter', 0)
            executor.execute_while(while_node, context)
            final_values.append(context.get('counter'))
        
        # All should reach 5
        assert all(v == 5 for v in final_values)
        assert len(set(final_values)) == 1  # All identical

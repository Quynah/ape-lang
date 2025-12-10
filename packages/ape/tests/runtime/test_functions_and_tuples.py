"""
Test Suite for APE Functions, Tuple Returns, and List Operations

Tests for v1.x production features:
- Function definitions (fn)
- Return statements (single and tuple)
- Tuple destructuring
- List literals and operations

Author: David Van Aelst
Status: v1.x production
"""

import pytest
from ape.tokenizer.tokenizer import Tokenizer
from ape.parser.parser import Parser
from ape.runtime.executor import RuntimeExecutor
from ape.runtime.context import ExecutionContext
from ape.types import ApeList, ApeTuple


class TestFunctionDefinitions:
    """Test function definitions and calls"""
    
    def test_simple_function(self):
        """Test simple function definition and call"""
        source = """
fn add(x, y):
    return x + y

fn main():
    result = add(3, 4)
    return result
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call main function
        main_fn = context.get('main')
        result = executor._call_user_function(main_fn, [], context, ast)
        assert result == 7
    
    def test_function_with_multiple_params(self):
        """Test function with multiple parameters"""
        source = """
fn calculate(a, b, c):
    return a + b * c
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call calculate function
        calc_fn = context.get('calculate')
        result = executor._call_user_function(calc_fn, [2, 3, 4], context, ast)
        assert result == 14  # 2 + 3 * 4


class TestTupleReturns:
    """Test tuple returns and destructuring"""
    
    def test_tuple_return_simple(self):
        """Test function returning multiple values"""
        source = """
fn analyze(x):
    return x + 10, x * 2
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call analyze function
        analyze_fn = context.get('analyze')
        result = executor._call_user_function(analyze_fn, [5], context, ast)
        
        assert isinstance(result, ApeTuple)
        assert len(result) == 2
        assert result[0] == 15  # 5 + 10
        assert result[1] == 10  # 5 * 2
    
    def test_tuple_destructuring(self):
        """Test tuple destructuring in assignment"""
        source = """
fn get_coords():
    return 10, 20, 30

fn main():
    x, y, z = get_coords()
    return x + y + z
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call main function
        main_fn = context.get('main')
        result = executor._call_user_function(main_fn, [], context, ast)
        assert result == 60  # 10 + 20 + 30
    
    def test_tuple_destructuring_arity_mismatch(self):
        """Test that arity mismatch raises error"""
        source = """
fn get_pair():
    return 1, 2

fn main():
    a, b, c = get_pair()
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call main function - should raise error
        main_fn = context.get('main')
        from ape.runtime.context import ExecutionError
        with pytest.raises(ExecutionError, match="arity mismatch"):
            executor._call_user_function(main_fn, [], context, ast)


class TestListOperations:
    """Test list literals and operations"""
    
    def test_list_literal(self):
        """Test list literal creation"""
        source = """
fn make_list():
    return [1, 2, 3]
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call make_list function
        fn = context.get('make_list')
        result = executor._call_user_function(fn, [], context, ast)
        
        assert isinstance(result, ApeList)
        assert len(result) == 3
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == 3
    
    def test_list_index_access(self):
        """Test list index access"""
        source = """
fn get_item():
    items = [10, 20, 30]
    return items[1]
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call get_item function
        fn = context.get('get_item')
        result = executor._call_user_function(fn, [], context, ast)
        assert result == 20
    
    def test_list_concatenation(self):
        """Test list concatenation with + operator"""
        source = """
fn concat_lists():
    a = [1, 2]
    b = [3, 4]
    c = a + b
    return c
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call concat_lists function
        fn = context.get('concat_lists')
        result = executor._call_user_function(fn, [], context, ast)
        
        assert isinstance(result, ApeList)
        assert len(result) == 4
        assert result[0] == 1
        assert result[3] == 4
    
    def test_list_length(self):
        """Test len() on list"""
        source = """
fn list_length():
    items = [1, 2, 3, 4, 5]
    return len(items)
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call list_length function
        fn = context.get('list_length')
        result = executor._call_user_function(fn, [], context, ast)
        assert result == 5
    
    def test_list_membership(self):
        """Test 'in' operator for lists"""
        source = """
fn check_membership():
    items = [1, 2, 3]
    return 2
"""
        # Note: Full 'in' operator testing would require if statement
        # For now, test the basic parsing and execution
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        fn = context.get('check_membership')
        result = executor._call_user_function(fn, [], context, ast)
        assert result == 2
    
    def test_empty_list(self):
        """Test empty list creation"""
        source = """
fn empty_list():
    return []
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call empty_list function
        fn = context.get('empty_list')
        result = executor._call_user_function(fn, [], context, ast)
        
        assert isinstance(result, ApeList)
        assert len(result) == 0


class TestTupleLiterals:
    """Test tuple literal syntax"""
    
    def test_tuple_literal(self):
        """Test tuple literal creation"""
        source = """
fn make_tuple():
    return (1, 2, 3)
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call make_tuple function
        fn = context.get('make_tuple')
        result = executor._call_user_function(fn, [], context, ast)
        
        assert isinstance(result, ApeTuple)
        assert len(result) == 3
        assert result[0] == 1
        assert result[2] == 3
    
    def test_tuple_index_access(self):
        """Test tuple index access"""
        source = """
fn get_tuple_item():
    coords = (10, 20, 30)
    return coords[1]
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        # Call get_tuple_item function
        fn = context.get('get_tuple_item')
        result = executor._call_user_function(fn, [], context, ast)
        assert result == 20


class TestComplexScenarios:
    """Test complex scenarios combining multiple features"""
    
    def test_function_with_list_processing(self):
        """Test function that processes lists"""
        source = """
fn sum_list(items):
    total = 0
    return total
"""
        # Note: Would need for loop to properly sum
        # This tests basic structure
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        fn = context.get('sum_list')
        result = executor._call_user_function(fn, [ApeList([1, 2, 3])], context, ast)
        assert result == 0
    
    def test_nested_tuple_return(self):
        """Test nested data structures"""
        source = """
fn nested_data():
    return (1, [2, 3], 4)
"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        executor = RuntimeExecutor()
        context = ExecutionContext()
        executor.execute(ast, context)
        
        fn = context.get('nested_data')
        result = executor._call_user_function(fn, [], context, ast)
        
        assert isinstance(result, ApeTuple)
        assert result[0] == 1
        assert isinstance(result[1], ApeList)
        assert len(result[1]) == 2
        assert result[2] == 4

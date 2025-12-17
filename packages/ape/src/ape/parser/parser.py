"""
Ape Parser

Recursive descent parser for Ape grammar v0.3.
Transforms tokens into Abstract Syntax Tree (AST).
"""

from typing import List, Optional
from ape.tokenizer.tokenizer import Token, TokenType, Tokenizer
from ape.parser.ast_nodes import *


class ParseError(Exception):
    """Exception raised when parsing fails"""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.token = token
        if token:
            super().__init__(f"{message} at line {token.line}, column {token.column}")
        else:
            super().__init__(message)


class Parser:
    """
    Recursive descent parser for Ape language.
    Follows the strict Ape principle: reject any ambiguity.
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None
    
    def parse(self) -> ModuleNode:
        """Parse a complete Ape module"""
        return self._parse_module()
    
    # === Token Management ===
    
    def _advance(self) -> Token:
        """Move to next token and return previous"""
        prev = self.current_token
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
        return prev
    
    def _peek(self, offset: int = 0) -> Optional[Token]:
        """Look ahead at token without consuming"""
        idx = self.pos + offset
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx]
        return None
    
    def _expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error"""
        if self.current_token.type != token_type:
            raise ParseError(
                f"Expected {token_type.name}, got {self.current_token.type.name}",
                self.current_token
            )
        return self._advance()
    
    def _match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of given types"""
        return self.current_token.type in token_types
    
    def _skip_newlines(self):
        """Skip any NEWLINE tokens"""
        while self._match(TokenType.NEWLINE):
            self._advance()
    
    # === Module Level ===
    
    def _parse_module(self) -> ModuleNode:
        """
        Parse a complete module.
        
        Grammar:
            module_file := [module_decl] import* definition*
            module_decl := 'module' identifier NEWLINE
            import      := 'import' qualified_identifier NEWLINE
        """
        module = ModuleNode()
        
        self._skip_newlines()
        
        # Check for optional module declaration at the top
        if self._match(TokenType.MODULE):
            self._advance()  # consume 'module'
            module.name = self._expect(TokenType.IDENTIFIER).value
            module.has_module_declaration = True
            self._expect(TokenType.NEWLINE)
            self._skip_newlines()
        
        # Parse all imports (must come before other declarations)
        while self._match(TokenType.IMPORT):
            module.imports.append(self._parse_import())
            self._skip_newlines()
        
        # Parse remaining top-level definitions
        while not self._match(TokenType.EOF):
            if self._match(TokenType.FN):
                module.functions.append(self._parse_function())
            elif self._match(TokenType.ENTITY):
                module.entities.append(self._parse_entity())
            elif self._match(TokenType.ENUM):
                module.enums.append(self._parse_enum())
            elif self._match(TokenType.TASK):
                module.tasks.append(self._parse_task())
            elif self._match(TokenType.FLOW):
                module.flows.append(self._parse_flow())
            elif self._match(TokenType.POLICY):
                module.policies.append(self._parse_policy())
            elif self._match(TokenType.IMPORT):
                # Import after other declarations - error!
                raise ParseError(
                    "Import statements must appear at the top of the file, "
                    "before any entity, enum, task, flow, or policy declarations",
                    self.current_token
                )
            else:
                raise ParseError(
                    f"Unexpected token at module level: {self.current_token.type.name}",
                    self.current_token
                )
            
            self._skip_newlines()
        
        return module
    
    def _parse_import(self) -> ImportNode:
        """
        Parse import statement.
        
        Grammar:
            import := 'import' qualified_identifier NEWLINE
            qualified_identifier := identifier ('.' identifier)*
        
        Examples:
            import math
            import strings.upper
            import collections.list
        """
        token = self._expect(TokenType.IMPORT)
        node = ImportNode(line=token.line, column=token.column)
        
        # Parse qualified identifier (e.g., math or math.add)
        node.qualified_name = self._parse_qualified_identifier()
        
        self._expect(TokenType.NEWLINE)
        return node
    
    def _parse_qualified_identifier(self) -> QualifiedIdentifierNode:
        """
        Parse a qualified identifier (e.g., math, strings.upper, collections.list).
        
        Grammar:
            qualified_identifier := identifier ('.' identifier)*
        """
        token = self.current_token
        node = QualifiedIdentifierNode(line=token.line, column=token.column)
        
        # First part (required)
        node.parts.append(self._expect(TokenType.IDENTIFIER).value)
        
        # Additional parts (optional)
        while self._match(TokenType.DOT):
            self._advance()  # consume '.'
            node.parts.append(self._expect(TokenType.IDENTIFIER).value)
        
        return node
    
    # === Function Definition ===
    
    def _parse_function(self) -> 'FunctionDefNode':
        """
        Parse function definition.
        
        Grammar:
            fn <name>(<params>):
                <block>
        
        Example:
            fn analyze(x, y):
                return x + y, x * y
        """
        from ape.parser.ast_nodes import FunctionDefNode
        
        token = self._expect(TokenType.FN)
        node = FunctionDefNode(line=token.line, column=token.column)
        
        # Parse function name
        node.name = self._expect(TokenType.IDENTIFIER).value
        
        # Parse parameters
        self._expect(TokenType.LPAREN)
        
        if not self._match(TokenType.RPAREN):
            # Parse parameter list
            node.parameters.append(self._expect(TokenType.IDENTIFIER).value)
            
            while self._match(TokenType.COMMA):
                self._advance()  # consume comma
                node.parameters.append(self._expect(TokenType.IDENTIFIER).value)
        
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        
        # Parse body
        node.body = self._parse_function_body()
        
        return node
    
    def _parse_function_body(self) -> List[ASTNode]:
        """
        Parse function body which can contain:
        - Assignments
        - Control flow (if/while/for)
        - Return statements
        - Function calls
        """
        self._expect(TokenType.INDENT)
        
        statements = []
        while not self._match(TokenType.DEDENT):
            self._skip_newlines()
            if self._match(TokenType.DEDENT):
                break
            
            # Parse statement
            if self._match(TokenType.RETURN):
                statements.append(self._parse_return())
            elif self._match(TokenType.IF):
                statements.append(self._parse_if())
            elif self._match(TokenType.WHILE):
                statements.append(self._parse_while())
            elif self._match(TokenType.FOR):
                statements.append(self._parse_for())
            elif self._match(TokenType.IDENTIFIER):
                # Could be assignment or function call
                # Peek ahead to determine
                if self._peek(1) and self._peek(1).type in [TokenType.COMMA, TokenType.ASSIGN]:
                    statements.append(self._parse_assignment())
                elif self._peek(1) and self._peek(1).type == TokenType.LPAREN:
                    # Function call as statement
                    expr = self._parse_expression()
                    statements.append(expr)
                    self._expect(TokenType.NEWLINE)
                else:
                    statements.append(self._parse_assignment())
            else:
                raise ParseError(
                    f"Unexpected token in function body: {self.current_token.type.name}",
                    self.current_token
                )
        
        self._expect(TokenType.DEDENT)
        return statements
    
    def _parse_return(self) -> 'ReturnNode':
        """
        Parse return statement.
        
        Grammar:
            return <expression>
            return <expr1>, <expr2>, <expr3>
        
        Examples:
            return x
            return a, b, c
        """
        from ape.parser.ast_nodes import ReturnNode
        
        token = self._expect(TokenType.RETURN)
        node = ReturnNode(line=token.line, column=token.column)
        
        # Parse return values (comma-separated for tuple returns)
        if not self._match(TokenType.NEWLINE):
            node.values.append(self._parse_expression())
            
            while self._match(TokenType.COMMA):
                self._advance()  # consume comma
                node.values.append(self._parse_expression())
        
        self._expect(TokenType.NEWLINE)
        return node
    
    def _parse_arithmetic_expression(self) -> ExpressionNode:
        """
        Parse arithmetic expression with proper operator precedence.
        
        Grammar:
            arithmetic_expr := term (('+' | '-') term)*
            term := factor (('*' | '/') factor)*
            factor := primary | '(' arithmetic_expr ')'
        """
        return self._parse_additive_expression()
    
    def _parse_additive_expression(self) -> ExpressionNode:
        """Parse addition and subtraction (lowest precedence for arithmetic)"""
        left = self._parse_multiplicative_expression()
        
        while self._match(TokenType.PLUS) or self._match(TokenType.DASH):
            op_token = self._advance()
            right = self._parse_multiplicative_expression()
            
            left = ExpressionNode(
                operator='+' if op_token.type == TokenType.PLUS else '-',
                left=left,
                right=right,
                line=left.line,
                column=left.column
            )
        
        return left
    
    def _parse_multiplicative_expression(self) -> ExpressionNode:
        """Parse multiplication and division (higher precedence than addition)"""
        left = self._parse_primary_expression()
        
        while self._match(TokenType.STAR) or self._match(TokenType.SLASH) or self._match(TokenType.PERCENT):
            op_token = self._advance()
            right = self._parse_primary_expression()
            
            op_map = {
                TokenType.STAR: '*',
                TokenType.SLASH: '/',
                TokenType.PERCENT: '%'
            }
            
            left = ExpressionNode(
                operator=op_map[op_token.type],
                left=left,
                right=right,
                line=left.line,
                column=left.column
            )
        
        return left
    
    def _parse_assignment(self) -> 'AssignmentNode':
        """
        Parse assignment statement.
        
        Grammar:
            <identifier> = <expression>
            <id1>, <id2>, <id3> = <expression>
        
        Examples:
            x = 5
            a, b, c = analyze(input)
        """
        from ape.parser.ast_nodes import AssignmentNode
        
        token = self.current_token
        node = AssignmentNode(line=token.line, column=token.column)
        
        # Parse target(s)
        node.targets.append(self._expect(TokenType.IDENTIFIER).value)
        
        while self._match(TokenType.COMMA):
            self._advance()  # consume comma
            node.targets.append(self._expect(TokenType.IDENTIFIER).value)
        
        # Expect = sign
        self._expect(TokenType.ASSIGN)
        
        # Parse value expression (full expression, not just arithmetic)
        node.value = self._parse_expression()
        
        self._expect(TokenType.NEWLINE)
        return node
    
    # === Entity ===
    
    def _parse_entity(self) -> EntityDefNode:
        """Parse entity definition"""
        token = self._expect(TokenType.ENTITY)
        node = EntityDefNode(line=token.line, column=token.column)
        
        node.name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        
        while not self._match(TokenType.DEDENT):
            self._skip_newlines()
            if self._match(TokenType.DEDENT):
                break
            
            if self._match(TokenType.CONSTRAINTS):
                node.constraints = self._parse_constraints()
            else:
                # Parse field
                node.fields.append(self._parse_field())
                self._expect(TokenType.NEWLINE)
        
        self._expect(TokenType.DEDENT)
        return node
    
    def _parse_field(self) -> FieldDefNode:
        """Parse field definition (name: Type or name: Type = default)"""
        token = self.current_token
        node = FieldDefNode(line=token.line, column=token.column)
        
        node.name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.COLON)
        node.type_annotation = self._parse_type()
        
        return node
    
    def _parse_type(self) -> TypeAnnotationNode:
        """Parse type annotation"""
        token = self.current_token
        node = TypeAnnotationNode(line=token.line, column=token.column)
        
        type_name = self._expect(TokenType.IDENTIFIER).value
        node.type_name = type_name
        
        # Check for Optional or other generic types would go here
        # For now, simple types only
        
        return node
    
    # === Enum ===
    
    def _parse_enum(self) -> EnumDefNode:
        """Parse enum definition"""
        token = self._expect(TokenType.ENUM)
        node = EnumDefNode(line=token.line, column=token.column)
        
        node.name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        
        while not self._match(TokenType.DEDENT):
            self._skip_newlines()
            if self._match(TokenType.DEDENT):
                break
            
            self._expect(TokenType.DASH)
            value = self._expect(TokenType.IDENTIFIER).value
            node.values.append(value)
            self._expect(TokenType.NEWLINE)
        
        self._expect(TokenType.DEDENT)
        return node
    
    # === Task ===
    
    def _parse_task(self) -> TaskDefNode:
        """Parse task definition"""
        token = self._expect(TokenType.TASK)
        node = TaskDefNode(line=token.line, column=token.column)
        
        node.name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        
        while not self._match(TokenType.DEDENT):
            self._skip_newlines()
            if self._match(TokenType.DEDENT):
                break
            
            if self._match(TokenType.INPUTS):
                node.inputs = self._parse_io_section()
            elif self._match(TokenType.OUTPUTS):
                node.outputs = self._parse_io_section()
            elif self._match(TokenType.STEPS):
                node.steps = self._parse_steps()
            elif self._match(TokenType.CONSTRAINTS):
                node.constraints = self._parse_constraints()
            else:
                raise ParseError(
                    f"Unexpected token in task: {self.current_token.type.name} (value='{self.current_token.value}')",
                    self.current_token
                )
        
        self._expect(TokenType.DEDENT)
        return node
    
    def _parse_io_section(self) -> List[FieldDefNode]:
        """Parse inputs or outputs section"""
        self._advance()  # consume INPUTS/OUTPUTS
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        
        fields = []
        while not self._match(TokenType.DEDENT):
            self._skip_newlines()
            if self._match(TokenType.DEDENT):
                break
            
            fields.append(self._parse_field())
            self._expect(TokenType.NEWLINE)
        
        self._expect(TokenType.DEDENT)
        return fields
    
    def _parse_steps(self) -> List[StepNode]:
        """Parse steps section"""
        self._expect(TokenType.STEPS)
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        
        steps = []
        while not self._match(TokenType.DEDENT):
            self._skip_newlines()
            if self._match(TokenType.DEDENT):
                break
            
            steps.append(self._parse_step())
        
        self._expect(TokenType.DEDENT)
        return steps
    
    def _parse_step(self) -> StepNode:
        """
        Parse a single step or control flow statement.
        
        Can be:
        - A dash step (- call x with y)
        - An if statement
        - A while loop  
        - A for loop
        """
        # Check for control flow (no dash)
        if self._match(TokenType.IF):
            return self._parse_if()
        elif self._match(TokenType.WHILE):
            return self._parse_while()
        elif self._match(TokenType.FOR):
            return self._parse_for()
        
        # Regular step with dash
        token = self._expect(TokenType.DASH)
        node = StepNode(line=token.line, column=token.column)
        
        # Read step action (rest of line)
        action_parts = []
        while not self._match(TokenType.NEWLINE):
            action_parts.append(self.current_token.value)
            self._advance()
        
        node.action = ' '.join(action_parts)
        self._expect(TokenType.NEWLINE)
        
        # Check for substeps
        if self._match(TokenType.INDENT):
            self._advance()
            while not self._match(TokenType.DEDENT):
                self._skip_newlines()
                if self._match(TokenType.DEDENT):
                    break
                node.substeps.append(self._parse_step())
            self._expect(TokenType.DEDENT)
        
        return node
    
    def _parse_if(self) -> IfNode:
        """
        Parse if/else if/else statement.
        
        Grammar:
            if <condition>:
                <block>
            else if <condition>:
                <block>
            else:
                <block>
        """
        token = self._expect(TokenType.IF)
        node = IfNode(line=token.line, column=token.column)
        
        # Parse main condition
        node.condition = self._parse_expression()
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        
        # Parse body
        node.body = self._parse_block()
        
        # Parse else if blocks
        while self._match(TokenType.ELSE):
            # Peek ahead to see if this is "else if" or just "else"
            next_token = self._peek(1)
            if next_token and next_token.type == TokenType.IF:
                self._advance()  # consume 'else'
                self._advance()  # consume 'if'
                
                # Parse elif condition and body
                elif_condition = self._parse_expression()
                self._expect(TokenType.COLON)
                self._expect(TokenType.NEWLINE)
                elif_body = self._parse_block()
                
                node.elif_blocks.append((elif_condition, elif_body))
            else:
                # Just 'else' - break to parse else block below
                break
        
        # Parse else block (if present)
        if self._match(TokenType.ELSE):
            self._advance()  # consume 'else'
            self._expect(TokenType.COLON)
            self._expect(TokenType.NEWLINE)
            node.else_body = self._parse_block()
        
        return node
    
    def _parse_while(self) -> WhileNode:
        """
        Parse while loop.
        
        Grammar:
            while <condition>:
                <block>
        """
        token = self._expect(TokenType.WHILE)
        node = WhileNode(line=token.line, column=token.column)
        
        # Parse condition
        node.condition = self._parse_expression()
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        
        # Parse body
        node.body = self._parse_block()
        
        return node
    
    def _parse_for(self) -> ForNode:
        """
        Parse for loop.
        
        Grammar:
            for <identifier> in <iterable>:
                <block>
        """
        token = self._expect(TokenType.FOR)
        node = ForNode(line=token.line, column=token.column)
        
        # Parse iterator variable
        node.iterator = self._expect(TokenType.IDENTIFIER).value
        
        # Expect 'in'
        self._expect(TokenType.IN)
        
        # Parse iterable expression
        node.iterable = self._parse_expression()
        
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        
        # Parse body
        node.body = self._parse_block()
        
        return node
    
    def _parse_block(self) -> List[ASTNode]:
        """
        Parse an indented block of statements.
        
        Returns:
            List of AST nodes (steps or control flow)
        """
        self._expect(TokenType.INDENT)
        
        statements = []
        while not self._match(TokenType.DEDENT):
            self._skip_newlines()
            if self._match(TokenType.DEDENT):
                break
            
            statements.append(self._parse_step())
        
        self._expect(TokenType.DEDENT)
        return statements
    
    def _parse_expression(self) -> ExpressionNode:
        """
        Parse an expression with support for chained boolean logic.
        
        Supports:
        - Simple comparisons: x < 10
        - Boolean logic: x > 5 and y < 10
        - Multiple operators: a or b or c
        
        Returns:
            ExpressionNode
        """
        return self._parse_or_expression()
    
    def _parse_or_expression(self) -> ExpressionNode:
        """Parse OR expression (lowest precedence for boolean operators)"""
        left = self._parse_and_expression()
        
        while self.current_token.type == TokenType.IDENTIFIER and self.current_token.value == 'or':
            self._advance()  # consume 'or'
            right = self._parse_and_expression()
            # Create binary expression node
            left = ExpressionNode(
                operator='or',
                left=left,
                right=right,
                line=left.line,
                column=left.column
            )
        
        return left
    
    def _parse_and_expression(self) -> ExpressionNode:
        """Parse AND expression (higher precedence than OR)"""
        left = self._parse_comparison_expression()
        
        while self.current_token.type == TokenType.IDENTIFIER and self.current_token.value == 'and':
            self._advance()  # consume 'and'
            right = self._parse_comparison_expression()
            # Create binary expression node
            left = ExpressionNode(
                operator='and',
                left=left,
                right=right,
                line=left.line,
                column=left.column
            )
        
        return left
    
    def _parse_comparison_expression(self) -> ExpressionNode:
        """Parse comparison expression (e.g., x < 10, name == "test", item in list)"""
        token = self.current_token
        node = ExpressionNode(line=token.line, column=token.column)
        
        # Parse left side (identifier or primary)
        if self._match(TokenType.IDENTIFIER):
            identifier = self._advance().value
            
            # Check for 'in' operator
            if self._match(TokenType.IN):
                self._advance()  # consume 'in'
                node.operator = 'in'
                node.left = ExpressionNode(identifier=identifier, line=token.line, column=token.column)
                node.right = self._parse_primary_expression()
            # Check for comparison operator
            elif self._match_comparison_operator():
                op_token = self._advance()
                # Map token type to operator string
                op_map = {
                    TokenType.LT: '<',
                    TokenType.GT: '>',
                    TokenType.LE: '<=',
                    TokenType.GE: '>=',
                    TokenType.EQ: '==',
                    TokenType.NE: '!=',
                }
                node.operator = op_map.get(op_token.type, op_token.value)
                node.left = ExpressionNode(identifier=identifier, line=token.line, column=token.column)
                node.right = self._parse_primary_expression()
            else:
                node.identifier = identifier
        else:
            # Primary expression (literal)
            node = self._parse_primary_expression()
        
        return node
    
    def _match_comparison_operator(self) -> bool:
        """Check if current token is a comparison operator"""
        return self.current_token.type in [
            TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE,
            TokenType.EQ, TokenType.NE
        ]
    
    def _parse_primary_expression(self) -> ExpressionNode:
        """
        Parse a primary expression (literal, identifier, function call, list, tuple, map/record, or index access).
        
        Supports:
        - Literals: 42, 3.14, "hello", true
        - Identifiers: x, my_var
        - Function calls: analyze(x, y)
        - Lists: [1, 2, 3]
        - Tuples: (1, 2, 3)
        - Maps/Records: { "key": value } or { field: value }
        - Index access: list[0]
        """
        from ape.parser.ast_nodes import ListNode, TupleNode, IndexAccessNode, MapNode
        
        token = self.current_token
        node = ExpressionNode(line=token.line, column=token.column)
        
        # Map/Record literal
        if self._match(TokenType.LBRACE):
            map_node = self._parse_map()
            node.map_node = map_node
            
        # List literal
        elif self._match(TokenType.LBRACKET):
            list_node = self._parse_list()
            node.list_node = list_node
            
        # Tuple literal or grouped expression
        elif self._match(TokenType.LPAREN):
            self._advance()  # consume (
            
            # Check for empty tuple
            if self._match(TokenType.RPAREN):
                self._advance()
                node.tuple_node = TupleNode(elements=[], line=token.line, column=token.column)
            else:
                # Parse first element
                first_expr = self._parse_expression()
                
                # Check if tuple (comma present) or grouped expression
                if self._match(TokenType.COMMA):
                    # It's a tuple
                    elements = [first_expr]
                    
                    while self._match(TokenType.COMMA):
                        self._advance()  # consume comma
                        # Allow trailing comma
                        if self._match(TokenType.RPAREN):
                            break
                        elements.append(self._parse_expression())
                    
                    self._expect(TokenType.RPAREN)
                    node.tuple_node = TupleNode(elements=elements, line=token.line, column=token.column)
                else:
                    # Grouped expression - just return the inner expression
                    self._expect(TokenType.RPAREN)
                    return first_expr
        
        # Number literal
        elif self._match(TokenType.NUMBER):
            value_str = self._advance().value
            # Convert to int or float
            node.value = float(value_str) if '.' in value_str else int(value_str)
            
        # String literal
        elif self._match(TokenType.STRING):
            # Remove quotes from string
            value = self._advance().value
            node.value = value[1:-1]  # Strip quotes
            
        # Boolean literal
        elif self._match(TokenType.BOOLEAN):
            value = self._advance().value
            node.value = value.lower() == 'true'
            
        # Identifier or function call
        elif self._match(TokenType.IDENTIFIER):
            identifier = self._advance().value
            
            # Check for function call
            if self._match(TokenType.LPAREN):
                self._advance()  # consume (
                
                # Parse arguments
                args = []
                if not self._match(TokenType.RPAREN):
                    args.append(self._parse_expression())
                    
                    while self._match(TokenType.COMMA):
                        self._advance()  # consume comma
                        args.append(self._parse_expression())
                
                self._expect(TokenType.RPAREN)
                
                # Create function call expression
                node.function_name = identifier
                node.arguments = args
            else:
                # Just an identifier
                node.identifier = identifier
        
        else:
            raise ParseError(
                f"Expected expression, got {self.current_token.type.name}",
                self.current_token
            )
        
        # Check for index access (postfix)
        if self._match(TokenType.LBRACKET):
            self._advance()  # consume [
            index_expr = self._parse_expression()
            self._expect(TokenType.RBRACKET)
            
            # Wrap current node in index access
            index_node = IndexAccessNode(
                target=node,
                index=index_expr,
                line=token.line,
                column=token.column
            )
            
            # Create expression node wrapping the index access
            result = ExpressionNode(line=token.line, column=token.column)
            result.index_access = index_node
            return result
        
        return node
    
    def _parse_list(self) -> 'ListNode':
        """
        Parse list literal.
        
        Grammar:
            list := '[' [expression (',' expression)* [',']] ']'
        
        Examples:
            []
            [1, 2, 3]
            [1, 2, 3,]  # trailing comma allowed
        """
        from ape.parser.ast_nodes import ListNode
        
        token = self._expect(TokenType.LBRACKET)
        node = ListNode(line=token.line, column=token.column)
        
        # Empty list
        if self._match(TokenType.RBRACKET):
            self._advance()
            return node
        
        # Parse elements
        node.elements.append(self._parse_expression())
        
        while self._match(TokenType.COMMA):
            self._advance()  # consume comma
            
            # Allow trailing comma
            if self._match(TokenType.RBRACKET):
                break
            
            node.elements.append(self._parse_expression())
        
        self._expect(TokenType.RBRACKET)
        return node
    
    def _parse_map(self) -> 'MapNode':
        """
        Parse map/record literal.
        
        Grammar:
            map := '{' [key_value_pair (',' key_value_pair)* [',']] '}'
            key_value_pair := (STRING | IDENTIFIER) ':' expression
        
        Examples:
            {}
            { "name": "Alice", "age": 30 }
            { id: "abc", score: 100 }
            { "a": { "b": 3 } }  # nested
            {
                "multi": "line",
                "map": "supported"
            }
        """
        from ape.parser.ast_nodes import MapNode
        
        token = self._expect(TokenType.LBRACE)
        node = MapNode(line=token.line, column=token.column)
        
        # Skip newlines after opening brace for multi-line maps
        self._skip_newlines()
        
        # Empty map
        if self._match(TokenType.RBRACE):
            self._advance()
            return node
        
        # Parse key-value pairs
        while True:
            # Skip newlines before key
            self._skip_newlines()
            
            # Parse key (string or identifier)
            key_node = ExpressionNode(line=self.current_token.line, column=self.current_token.column)
            if self._match(TokenType.STRING):
                key_str = self._advance().value
                key_node.value = key_str[1:-1]  # Strip quotes
            elif self._match(TokenType.IDENTIFIER):
                # Identifier as key (e.g., { name: "Alice" })
                key_node.value = self._advance().value
            else:
                raise ParseError(
                    f"Expected STRING or IDENTIFIER for map key, got {self.current_token.type.name}",
                    self.current_token
                )
            
            self._expect(TokenType.COLON)
            
            # Parse value
            value_node = self._parse_expression()
            
            node.keys.append(key_node)
            node.values.append(value_node)
            
            # Skip newlines after value
            self._skip_newlines()
            
            # Check for comma or end
            if self._match(TokenType.COMMA):
                self._advance()
                # Skip newlines after comma
                self._skip_newlines()
                # Allow trailing comma
                if self._match(TokenType.RBRACE):
                    break
            elif self._match(TokenType.RBRACE):
                break
            else:
                raise ParseError(
                    f"Expected ',' or '}}' in map literal, got {self.current_token.type.name}",
                    self.current_token
                )
        
        self._expect(TokenType.RBRACE)
        return node
    
    def _match_expression_operator(self) -> bool:
        """Check if current token is a binary operator"""
        return self.current_token.type in [
            TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE,
            TokenType.EQ, TokenType.NE, TokenType.PLUS, TokenType.DASH,
            TokenType.STAR, TokenType.SLASH, TokenType.PERCENT
        ] or (self.current_token.type == TokenType.IDENTIFIER and 
              self.current_token.value in ['and', 'or'])
    
    def _parse_constraints(self) -> List[ConstraintNode]:
        """Parse constraints section"""
        self._expect(TokenType.CONSTRAINTS)
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        
        constraints = []
        while not self._match(TokenType.DEDENT):
            self._skip_newlines()
            if self._match(TokenType.DEDENT):
                break
            
            # Expect a dash for any constraint
            token = self._expect(TokenType.DASH)
            
            # Check for deviation (after the dash)
            if self.current_token.type == TokenType.ALLOW:
                # Parse deviation block
                deviation_node = self._parse_deviation()
                constraints.append(deviation_node)
                continue
            
            # Regular constraint
            node = ConstraintNode(line=token.line, column=token.column)
            
            # Read constraint expression (rest of line)
            expr_parts = []
            while not self._match(TokenType.NEWLINE):
                expr_parts.append(self.current_token.value)
                self._advance()
            
            node.expression = ' '.join(expr_parts)
            self._expect(TokenType.NEWLINE)
            constraints.append(node)
        
        self._expect(TokenType.DEDENT)
        return constraints
    
    def _parse_deviation(self) -> 'DeviationNode':
        """Parse allow deviation block - DASH is already consumed"""
        from .ast_nodes import DeviationNode
        
        # DASH already consumed by caller, expect: allow deviation:
        # Format: "allow deviation:" then NEWLINE INDENT
        self._expect(TokenType.ALLOW)
        self._expect(TokenType.DEVIATION)
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        
        scope = ""
        mode = ""
        bounds = []
        rationale = None
        
        while not self._match(TokenType.DEDENT):
            self._skip_newlines()
            if self._match(TokenType.DEDENT):
                break
            
            # Parse scope:
            if self.current_token.type == TokenType.SCOPE:
                self._advance()  # consume SCOPE
                self._expect(TokenType.COLON)
                # scope value can be IDENTIFIER or keyword like STEPS
                if self.current_token.type == TokenType.IDENTIFIER:
                    scope = self.current_token.value
                    self._advance()
                elif self.current_token.type == TokenType.STEPS:
                    scope = "steps"
                    self._advance()
                elif self.current_token.type == TokenType.FLOW:
                    scope = "flow"
                    self._advance()
                else:
                    scope = self.current_token.value
                    self._advance()
                self._expect(TokenType.NEWLINE)
            
            # Parse mode:
            elif self.current_token.type == TokenType.MODE:
                self._advance()  # consume MODE
                self._expect(TokenType.COLON)
                mode = self._expect(TokenType.IDENTIFIER).value
                self._expect(TokenType.NEWLINE)
            
            # Parse bounds:
            elif self.current_token.type == TokenType.BOUNDS:
                self._advance()  # consume BOUNDS
                self._expect(TokenType.COLON)
                self._expect(TokenType.NEWLINE)
                self._expect(TokenType.INDENT)
                
                while not self._match(TokenType.DEDENT):
                    self._skip_newlines()
                    if self._match(TokenType.DEDENT):
                        break
                    
                    # Each bound is a "- text" line
                    self._expect(TokenType.DASH)
                    bound_parts = []
                    while not self._match(TokenType.NEWLINE):
                        bound_parts.append(self.current_token.value)
                        self._advance()
                    
                    bound_text = ' '.join(bound_parts)
                    bounds.append(bound_text)
                    self._expect(TokenType.NEWLINE)
                
                self._expect(TokenType.DEDENT)
            
            # Parse rationale:
            elif self.current_token.type == TokenType.RATIONALE:
                self._advance()  # consume RATIONALE
                self._expect(TokenType.COLON)
                # Rationale can be a STRING or plain text
                if self.current_token.type == TokenType.STRING:
                    rationale = self.current_token.value
                    self._advance()
                else:
                    # Read rest of line as rationale
                    rationale_parts = []
                    while not self._match(TokenType.NEWLINE):
                        rationale_parts.append(self.current_token.value)
                        self._advance()
                    rationale = ' '.join(rationale_parts)
                self._expect(TokenType.NEWLINE)
            
            else:
                # Unknown field, skip line
                while not self._match(TokenType.NEWLINE):
                    self._advance()
                self._expect(TokenType.NEWLINE)
        
        self._expect(TokenType.DEDENT)
        
        return DeviationNode(
            scope=scope,
            mode=mode,
            bounds=bounds,
            rationale=rationale
        )
    
    def _skip_until_dedent(self):
        """Skip tokens until DEDENT"""
        depth = 0
        while not (self._match(TokenType.DEDENT) and depth == 0):
            if self._match(TokenType.INDENT):
                depth += 1
            elif self._match(TokenType.DEDENT):
                depth -= 1
            self._advance()
    
    # === Flow ===
    
    def _parse_flow(self) -> FlowDefNode:
        """Parse flow definition"""
        token = self._expect(TokenType.FLOW)
        node = FlowDefNode(line=token.line, column=token.column)
        
        node.name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        
        while not self._match(TokenType.DEDENT):
            self._skip_newlines()
            if self._match(TokenType.DEDENT):
                break
            
            if self._match(TokenType.STEPS):
                node.steps = self._parse_steps()
            elif self._match(TokenType.CONSTRAINTS):
                node.constraints = self._parse_constraints()
            else:
                raise ParseError(
                    f"Unexpected token in flow: {self.current_token.type.name}",
                    self.current_token
                )
        
        self._expect(TokenType.DEDENT)
        return node
    
    # === Policy ===
    
    def _parse_policy(self) -> PolicyDefNode:
        """Parse policy definition"""
        token = self._expect(TokenType.POLICY)
        node = PolicyDefNode(line=token.line, column=token.column)
        
        node.name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        
        if self._match(TokenType.RULES):
            self._advance()
            self._expect(TokenType.COLON)
            self._expect(TokenType.NEWLINE)
            self._expect(TokenType.INDENT)
            
            while not self._match(TokenType.DEDENT):
                self._skip_newlines()
                if self._match(TokenType.DEDENT):
                    break
                
                self._expect(TokenType.DASH)
                
                # Read rule (rest of line)
                rule_parts = []
                while not self._match(TokenType.NEWLINE):
                    rule_parts.append(self.current_token.value)
                    self._advance()
                
                node.rules.append(' '.join(rule_parts))
                self._expect(TokenType.NEWLINE)
            
            self._expect(TokenType.DEDENT)
        
        self._expect(TokenType.DEDENT)
        return node


def parse_ape_source(source: str, filename: str = "<unknown>") -> ModuleNode:
    """
    Convenience function to tokenize and parse Ape source code.
    
    Args:
        source: Ape source code as string
        filename: Source filename for error reporting
    
    Returns:
        Parsed AST ModuleNode
    """
    tokenizer = Tokenizer(source, filename)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    return parser.parse()

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
            if self._match(TokenType.ENTITY):
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
                    f"Unexpected token in task: {self.current_token.type.name}",
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
        Parse an expression (condition, arithmetic, etc.).
        
        For now, this is a simplified parser that reads tokens until :
        In a full implementation, this would be a proper expression parser
        with operator precedence, etc.
        
        Returns:
            ExpressionNode
        """
        token = self.current_token
        node = ExpressionNode(line=token.line, column=token.column)
        
        # Simple expression parsing: read until we hit a colon
        # This is a placeholder - a real implementation would parse
        # operators, precedence, etc.
        
        # For now, just handle simple cases:
        # - identifiers (variables)
        # - literals (numbers, strings, booleans)
        # - simple binary operations (x < 10, x == 5, etc.)
        
        if self._match(TokenType.IDENTIFIER):
            identifier = self._advance().value
            
            # Check for binary operator
            if self._match_expression_operator():
                op_token = self._advance()
                # Map token type to operator string
                op_map = {
                    TokenType.LT: '<',
                    TokenType.GT: '>',
                    TokenType.LE: '<=',
                    TokenType.GE: '>=',
                    TokenType.EQ: '==',
                    TokenType.NE: '!=',
                    TokenType.PLUS: '+',
                    TokenType.DASH: '-',
                    TokenType.STAR: '*',
                    TokenType.SLASH: '/',
                    TokenType.PERCENT: '%',
                }
                node.operator = op_map.get(op_token.type, op_token.value)
                node.left = ExpressionNode(identifier=identifier, line=token.line, column=token.column)
                node.right = self._parse_primary_expression()
            else:
                node.identifier = identifier
        else:
            # Primary expression (literal or parenthesized expression)
            node = self._parse_primary_expression()
        
        return node
    
    def _parse_primary_expression(self) -> ExpressionNode:
        """Parse a primary expression (literal, identifier, or grouped expression)"""
        token = self.current_token
        node = ExpressionNode(line=token.line, column=token.column)
        
        if self._match(TokenType.NUMBER):
            value_str = self._advance().value
            # Convert to int or float
            node.value = float(value_str) if '.' in value_str else int(value_str)
        elif self._match(TokenType.STRING):
            # Remove quotes from string
            value = self._advance().value
            node.value = value[1:-1]  # Strip quotes
        elif self._match(TokenType.BOOLEAN):
            value = self._advance().value
            node.value = value.lower() == 'true'
        elif self._match(TokenType.IDENTIFIER):
            node.identifier = self._advance().value
        else:
            raise ParseError(
                f"Expected expression, got {self.current_token.type.name}",
                self.current_token
            )
        
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

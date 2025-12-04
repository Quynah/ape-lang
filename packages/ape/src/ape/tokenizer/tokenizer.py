"""
Ape Tokenizer

Lexical analysis for Ape language with indentation-aware tokenization.
Follows strict Ape principle: all tokens are explicit and unambiguous.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """All valid token types in Ape language"""
    # Keywords
    MODULE = auto()
    ENTITY = auto()
    TASK = auto()
    FLOW = auto()
    POLICY = auto()
    ENUM = auto()
    CONSTRAINTS = auto()
    ALLOW = auto()
    DEVIATION = auto()
    SCOPE = auto()
    MODE = auto()
    BOUNDS = auto()
    RATIONALE = auto()
    INPUTS = auto()
    OUTPUTS = auto()
    STEPS = auto()
    RULES = auto()
    IMPORT = auto()
    FROM = auto()
    
    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    
    # Operators and delimiters
    COLON = auto()
    COMMA = auto()
    DOT = auto()
    DASH = auto()
    PIPE = auto()
    ARROW = auto()
    
    # Structure
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    EOF = auto()
    
    # Comments
    COMMENT = auto()


@dataclass
class Token:
    """
    Represents a single token in Ape source code.
    
    Attributes:
        type: The token type
        value: The literal value from source
        line: Line number (1-indexed)
        column: Column number (1-indexed)
    """
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class Tokenizer:
    """
    Tokenizer for Ape language with Python-style indentation handling.
    """
    
    KEYWORDS = {
        'module': TokenType.MODULE,
        'entity': TokenType.ENTITY,
        'task': TokenType.TASK,
        'flow': TokenType.FLOW,
        'policy': TokenType.POLICY,
        'enum': TokenType.ENUM,
        'constraints': TokenType.CONSTRAINTS,
        'allow': TokenType.ALLOW,
        'deviation': TokenType.DEVIATION,
        'scope': TokenType.SCOPE,
        'mode': TokenType.MODE,
        'bounds': TokenType.BOUNDS,
        'rationale': TokenType.RATIONALE,
        'inputs': TokenType.INPUTS,
        'outputs': TokenType.OUTPUTS,
        'steps': TokenType.STEPS,
        'rules': TokenType.RULES,
        'import': TokenType.IMPORT,
        'from': TokenType.FROM,
        'true': TokenType.BOOLEAN,
        'false': TokenType.BOOLEAN,
        'True': TokenType.BOOLEAN,
        'False': TokenType.BOOLEAN,
    }
    
    # Token patterns (order matters!)
    TOKEN_PATTERNS = [
        # Comments
        (r'#[^\n]*', TokenType.COMMENT),
        
        # Multi-character operators
        (r'->', TokenType.ARROW),
        
        # String literals (single or double quoted)
        (r'"(?:[^"\\]|\\.)*"', TokenType.STRING),
        (r"'(?:[^'\\]|\\.)*'", TokenType.STRING),
        
        # Numbers
        (r'\d+\.\d+', TokenType.NUMBER),
        (r'\d+', TokenType.NUMBER),
        
        # Identifiers and keywords
        (r'[a-zA-Z_][a-zA-Z0-9_?]*', TokenType.IDENTIFIER),
        
        # Single-character delimiters
        (r':', TokenType.COLON),
        (r',', TokenType.COMMA),
        (r'\.', TokenType.DOT),
        (r'-', TokenType.DASH),
        (r'\|', TokenType.PIPE),
    ]
    
    def __init__(self, source: str, filename: str = "<unknown>"):
        self.source = source
        self.filename = filename
        self.lines = source.split('\n')
        self.tokens: List[Token] = []
        self.indent_stack: List[int] = [0]
        
    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire source code.
        Returns a list of tokens including INDENT/DEDENT tokens.
        """
        self.tokens = []
        
        for line_num, line in enumerate(self.lines, start=1):
            self._process_line(line, line_num)
        
        # Add final dedents to return to base level
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, '', len(self.lines), 0))
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', len(self.lines) + 1, 0))
        
        return self.tokens
    
    def _process_line(self, line: str, line_num: int):
        """Process a single line of source code"""
        # Skip empty lines
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            return
        
        # Calculate indentation
        indent_level = len(line) - len(stripped)
        
        # Handle indentation changes
        self._handle_indentation(indent_level, line_num)
        
        # Tokenize the line content
        self._tokenize_line(stripped, line_num, indent_level)
        
        # Add newline token
        self.tokens.append(Token(TokenType.NEWLINE, '\n', line_num, len(line)))
    
    def _handle_indentation(self, indent_level: int, line_num: int):
        """Handle INDENT and DEDENT tokens based on indentation level"""
        current_indent = self.indent_stack[-1]
        
        if indent_level > current_indent:
            # Indent
            self.indent_stack.append(indent_level)
            self.tokens.append(Token(TokenType.INDENT, '', line_num, 0))
        elif indent_level < current_indent:
            # Dedent (possibly multiple levels)
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, '', line_num, 0))
            
            # Check for indentation error
            if self.indent_stack[-1] != indent_level:
                raise SyntaxError(
                    f"Indentation error at line {line_num}: "
                    f"unexpected indentation level {indent_level}"
                )
    
    def _tokenize_line(self, line: str, line_num: int, base_column: int):
        """Tokenize the content of a single line"""
        pos = 0
        
        while pos < len(line):
            # Skip whitespace
            if line[pos].isspace():
                pos += 1
                continue
            
            # Try to match a token
            matched = False
            for pattern, token_type in self.TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(line, pos)
                
                if match:
                    value = match.group(0)
                    
                    # Skip comments
                    if token_type == TokenType.COMMENT:
                        return
                    
                    # Check if identifier is actually a keyword
                    if token_type == TokenType.IDENTIFIER:
                        token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)
                    
                    self.tokens.append(Token(
                        type=token_type,
                        value=value,
                        line=line_num,
                        column=base_column + pos + 1
                    ))
                    
                    pos = match.end()
                    matched = True
                    break
            
            if not matched:
                raise SyntaxError(
                    f"Unexpected character '{line[pos]}' at line {line_num}, "
                    f"column {base_column + pos + 1}"
                )

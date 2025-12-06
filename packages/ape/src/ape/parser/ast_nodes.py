"""
Ape Abstract Syntax Tree (AST) Node Definitions

AST is an intermediate structure between tokens and IR.
These nodes directly represent the parsed grammar structure.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    line: int = 0
    column: int = 0


@dataclass
class IdentifierNode(ASTNode):
    """Identifier reference"""
    name: str = ""


@dataclass
class QualifiedIdentifierNode(ASTNode):
    """Qualified identifier for module paths (e.g., math.add, strings.upper)"""
    parts: List[str] = field(default_factory=list)
    
    def __str__(self):
        return ".".join(self.parts)
    
    @property
    def is_simple(self) -> bool:
        """Check if this is a simple (non-qualified) identifier"""
        return len(self.parts) == 1
    
    @property
    def module_name(self) -> str:
        """Get the module name (first part)"""
        return self.parts[0] if self.parts else ""
    
    @property
    def symbol_name(self) -> Optional[str]:
        """Get the symbol name (last part if qualified, None if simple)"""
        return self.parts[-1] if len(self.parts) > 1 else None


@dataclass
class TypeAnnotationNode(ASTNode):
    """Type annotation (e.g., String, Integer, Optional[User])"""
    type_name: str = ""
    is_optional: bool = False
    type_params: List[str] = field(default_factory=list)


@dataclass
class FieldDefNode(ASTNode):
    """Field definition in entity or task"""
    name: str = ""
    type_annotation: Optional[TypeAnnotationNode] = None
    default_value: Optional[Any] = None


@dataclass
class ConstraintNode(ASTNode):
    """Constraint expression"""
    expression: str = ""


@dataclass
class DeviationBoundsNode(ASTNode):
    """Deviation bounds definition"""
    bounds: List[str] = field(default_factory=list)


@dataclass
class DeviationNode(ASTNode):
    """Controlled deviation block (RFC-0001)"""
    scope: str = ""  # steps|strategy|flow
    mode: str = ""   # creative|semantic_choice|fuzzy_goal
    bounds: List[str] = field(default_factory=list)
    rationale: Optional[str] = None


@dataclass
class StepNode(ASTNode):
    """Task or flow step"""
    action: str = ""
    description: Optional[str] = None
    substeps: List['StepNode'] = field(default_factory=list)


@dataclass
class ExpressionNode(ASTNode):
    """
    Expression node for conditions and computations.
    Can be a literal, identifier, or operation.
    """
    value: Any = None  # For literals
    identifier: Optional[str] = None  # For variable references
    operator: Optional[str] = None  # For operations: +, -, <, >, ==, etc.
    left: Optional['ExpressionNode'] = None
    right: Optional['ExpressionNode'] = None


@dataclass
class IfNode(ASTNode):
    """
    If/else if/else control flow node.
    
    Grammar:
        if <condition>:
            <block>
        else if <condition>:
            <block>
        else:
            <block>
    """
    condition: ExpressionNode = None
    body: List[ASTNode] = field(default_factory=list)
    elif_blocks: List[tuple[ExpressionNode, List[ASTNode]]] = field(default_factory=list)
    else_body: Optional[List[ASTNode]] = None


@dataclass
class WhileNode(ASTNode):
    """
    While loop control flow node.
    
    Grammar:
        while <condition>:
            <block>
    """
    condition: ExpressionNode = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class ForNode(ASTNode):
    """
    For loop control flow node.
    
    Grammar:
        for <identifier> in <iterable>:
            <block>
    """
    iterator: str = ""  # Variable name
    iterable: ExpressionNode = None  # Expression that evaluates to iterable
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class EntityDefNode(ASTNode):
    """Entity definition"""
    name: str = ""
    fields: List[FieldDefNode] = field(default_factory=list)
    constraints: List[ConstraintNode] = field(default_factory=list)


@dataclass
class EnumDefNode(ASTNode):
    """Enum definition"""
    name: str = ""
    values: List[str] = field(default_factory=list)


@dataclass
class TaskDefNode(ASTNode):
    """Task definition"""
    name: str = ""
    inputs: List[FieldDefNode] = field(default_factory=list)
    outputs: List[FieldDefNode] = field(default_factory=list)
    steps: List[StepNode] = field(default_factory=list)
    constraints: List[ConstraintNode] = field(default_factory=list)
    deviation: Optional[DeviationNode] = None


@dataclass
class FlowDefNode(ASTNode):
    """Flow definition"""
    name: str = ""
    steps: List[StepNode] = field(default_factory=list)
    constraints: List[ConstraintNode] = field(default_factory=list)
    deviation: Optional[DeviationNode] = None


@dataclass
class PolicyDefNode(ASTNode):
    """Policy definition"""
    name: str = ""
    rules: List[str] = field(default_factory=list)
    scope: str = "global"


@dataclass
class ImportNode(ASTNode):
    """Import statement - supports both 'import math' and 'import math.add'"""
    qualified_name: Optional[QualifiedIdentifierNode] = None
    
    @property
    def is_specific_symbol(self) -> bool:
        """Check if importing a specific symbol (e.g., math.add) vs whole module (e.g., math)"""
        return self.qualified_name is not None and not self.qualified_name.is_simple
    
    @property
    def module_name(self) -> str:
        """Get the module name being imported"""
        return self.qualified_name.module_name if self.qualified_name else ""
    
    @property
    def symbol_name(self) -> Optional[str]:
        """Get the specific symbol name if importing specific symbol"""
        return self.qualified_name.symbol_name if self.qualified_name else None


@dataclass
class ModuleNode(ASTNode):
    """Module (file) root node"""
    name: str = ""  # Empty string means no module declaration (legacy/main program)
    has_module_declaration: bool = False  # True if file starts with 'module <name>'
    imports: List[ImportNode] = field(default_factory=list)
    entities: List[EntityDefNode] = field(default_factory=list)
    enums: List[EnumDefNode] = field(default_factory=list)
    tasks: List[TaskDefNode] = field(default_factory=list)
    flows: List[FlowDefNode] = field(default_factory=list)
    policies: List[PolicyDefNode] = field(default_factory=list)


@dataclass
class ProjectNode(ASTNode):
    """Project root node (collection of modules)"""
    name: str = ""
    modules: List[ModuleNode] = field(default_factory=list)


# ============================================================================
# Exception Handling Nodes (v1.0.0 scaffold)
# ============================================================================

@dataclass
class TryNode(ASTNode):
    """
    Try-catch-finally exception handling construct.
    
    Example:
        try:
            risky_operation()
        catch Error as e:
            handle_error(e)
        finally:
            cleanup()
    
    Author: David Van Aelst
    Status: v1.0.0 scaffold - implementation pending
    """
    try_block: List[ASTNode] = field(default_factory=list)
    catch_clauses: List['CatchNode'] = field(default_factory=list)
    finally_block: Optional[List[ASTNode]] = None


@dataclass
class CatchNode(ASTNode):
    """
    Catch clause within a try block.
    
    Example:
        catch TypeError as e:
            print("Type error: " + e.message)
    
    Author: David Van Aelst
    Status: v1.0.0 scaffold - implementation pending
    """
    error_type: Optional[str] = None  # None means catch all
    variable_name: Optional[str] = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class RaiseNode(ASTNode):
    """
    Raise an error/exception.
    
    Example:
        raise Error("Something went wrong")
    
    Author: David Van Aelst
    Status: v1.0.0 scaffold - implementation pending
    """
    error_type: str = "Error"
    message: Optional[ASTNode] = None  # Expression node

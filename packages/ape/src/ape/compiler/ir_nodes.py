"""
Ape Intermediate Representation (IR) Node Definitions

This module defines the IR node structures used throughout the Ape compiler.
All nodes follow the strict Ape principle: "What is not declared, does not exist."
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any
from enum import Enum


class NodeKind(Enum):
    """All valid IR node types in Ape"""
    PROJECT = "Project"
    MODULE = "Module"
    ENTITY = "Entity"
    TASK = "Task"
    FLOW = "Flow"
    POLICY = "Policy"
    ENUM = "Enum"
    DEVIATION = "Deviation"
    CONSTRAINT = "Constraint"
    STEP = "Step"
    FIELD = "Field"


class DeviationMode(Enum):
    """Modes for controlled deviation"""
    CREATIVE = "creative"
    SEMANTIC_CHOICE = "semantic_choice"
    FUZZY_GOAL = "fuzzy_goal"


@dataclass
class Location:
    """Source location for error reporting"""
    file: str
    line: int
    column: Optional[int] = None
    
    def __str__(self):
        if self.column:
            return f"{self.file}:{self.line}:{self.column}"
        return f"{self.file}:{self.line}"


@dataclass
class FieldNode:
    """Entity field definition"""
    name: str
    type: str
    optional: bool = False
    default: Optional[Any] = None
    location: Optional[Location] = None


@dataclass
class StepNode:
    """Task or Flow step"""
    action: str
    description: Optional[str] = None
    substeps: List['StepNode'] = field(default_factory=list)
    location: Optional[Location] = None


@dataclass
class ConstraintNode:
    """Constraint definition"""
    expression: str
    location: Optional[Location] = None


@dataclass
class DeviationNode:
    """Controlled deviation block (RFC-0001)"""
    kind: str = "Deviation"
    scope: str = ""  # steps|strategy|flow
    mode: DeviationMode = DeviationMode.CREATIVE
    bounds: List[str] = field(default_factory=list)
    rationale: Optional[str] = None
    location: Optional[Location] = None
    
    def __post_init__(self):
        if isinstance(self.mode, str):
            self.mode = DeviationMode(self.mode)


@dataclass
class EntityNode:
    """Entity definition (data structure)"""
    kind: str = "Entity"
    name: str = ""
    fields: List[FieldNode] = field(default_factory=list)
    constraints: List[ConstraintNode] = field(default_factory=list)
    location: Optional[Location] = None


@dataclass
class EnumNode:
    """Enum definition"""
    kind: str = "Enum"
    name: str = ""
    values: List[str] = field(default_factory=list)
    location: Optional[Location] = None


@dataclass
class TaskNode:
    """Task definition (executable unit)"""
    kind: str = "Task"
    name: str = ""
    inputs: List[FieldNode] = field(default_factory=list)
    outputs: List[FieldNode] = field(default_factory=list)
    steps: List[StepNode] = field(default_factory=list)
    constraints: List[ConstraintNode] = field(default_factory=list)
    deviation: Optional[DeviationNode] = None
    location: Optional[Location] = None


@dataclass
class FlowNode:
    """Flow definition (orchestration)"""
    kind: str = "Flow"
    name: str = ""
    steps: List[StepNode] = field(default_factory=list)
    constraints: List[ConstraintNode] = field(default_factory=list)
    deviation: Optional[DeviationNode] = None
    location: Optional[Location] = None


@dataclass
class PolicyNode:
    """Policy definition (global rules)"""
    kind: str = "Policy"
    name: str = ""
    rules: List[str] = field(default_factory=list)
    scope: str = "global"  # global|module|task
    location: Optional[Location] = None


@dataclass
class ModuleNode:
    """Module definition (compilation unit)"""
    kind: str = "Module"
    name: str = ""
    entities: List[EntityNode] = field(default_factory=list)
    enums: List[EnumNode] = field(default_factory=list)
    tasks: List[TaskNode] = field(default_factory=list)
    flows: List[FlowNode] = field(default_factory=list)
    policies: List[PolicyNode] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    location: Optional[Location] = None


@dataclass
class ProjectNode:
    """Root project node"""
    kind: str = "Project"
    name: str = ""
    modules: List[ModuleNode] = field(default_factory=list)
    global_policies: List[PolicyNode] = field(default_factory=list)
    location: Optional[Location] = None

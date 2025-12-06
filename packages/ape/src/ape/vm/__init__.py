"""
APE Virtual Machine Package (v1.0.0 Scaffold)

Stack-based virtual machine for executing APE bytecode.

Author: David Van Aelst
Status: Scaffold - implementation pending
"""

from .vm import VirtualMachine
from .instructions import StackFrame, ExecutionContext

__all__ = ['VirtualMachine', 'StackFrame', 'ExecutionContext']

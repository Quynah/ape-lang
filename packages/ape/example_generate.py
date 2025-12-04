"""
Example: Save generated Python code to file

Demonstrates how to use the Ape pipeline and save generated code.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ape.parser import parse_ape_source, IRBuilder
from ape.compiler.ir_nodes import ProjectNode
from ape.codegen.python_codegen import PythonCodeGenerator


# Example Ape source
ape_source = """entity User:
    id: Integer
    username: String
    email: String
    created_at: String

enum UserRole:
    - admin
    - moderator
    - user
    - guest

task CreateUser:
    inputs:
        username: String
        email: String
        role: UserRole
    outputs:
        user: User
    steps:
        - validate username is not empty
        - validate email format
        - check username is unique
        - create User instance with generated id
        - set username and email and created_at
        - assign role to user
        - persist user to database
        - return user
    constraints:
        - username must be unique
        - email must be valid format

task AuthenticateUser:
    inputs:
        username: String
        password: String
    outputs:
        authenticated: Boolean
    steps:
        - find user by username
        - verify password hash
        - return authentication result

flow UserRegistrationFlow:
    steps:
        - receive registration request
        - validate input data
        - call CreateUser task
        - send welcome email to user
        - log registration event
        - return success response

policy SecurityPolicy:
    rules:
        - all passwords must be hashed
        - user data must be encrypted at rest
        - failed login attempts must be logged
"""

# Parse and generate
ast = parse_ape_source(ape_source, "user_system.ape")
builder = IRBuilder()
ir_module = builder.build_module(ast, "user_system.ape")
project = ProjectNode(name="UserSystem", modules=[ir_module])

# Generate Python code
codegen = PythonCodeGenerator(project)
files = codegen.generate()

# Create output directory
os.makedirs("generated", exist_ok=True)

# Save files
for file in files:
    filepath = file.path
    print(f"Writing {filepath}...")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(file.content)
    
    print(f"✅ Saved {filepath} ({len(file.content)} bytes)")

print("\n🎉 Code generation complete!")
print(f"Generated {len(files)} file(s) in ./generated/")

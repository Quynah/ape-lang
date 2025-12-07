# Test Suite: Tutorial Execution Validation
# Verifies all tutorial scenarios execute successfully

from pathlib import Path
import re
import json
import pytest
from ape import run

# Get tutorials directory
TUTORIALS_DIR = Path(__file__).parent.parent.parent / "tutorials"

def iter_tutorial_files():
    """Find all .ape files in tutorials directory."""
    for ape_file in TUTORIALS_DIR.rglob("*.ape"):
        yield ape_file

def extract_expected(source: str):
    """Parse EXPECT comment from APE source."""
    match = re.search(r'#\s*EXPECT:\s*(.+)', source)
    if match:
        expected_str = match.group(1).strip()
        try:
            # Try JSON parsing first
            return json.loads(expected_str)
        except json.JSONDecodeError:
            # If not valid JSON, return as string (strip quotes if present)
            return expected_str.strip('"').strip("'")
    return None

# Collect all tutorial files
TUTORIAL_FILES = list(iter_tutorial_files())

# Define context/inputs for each tutorial
# Primary contexts test the happy path (matches EXPECT comments)
SCENARIO_CONTEXTS = {
    "scenario_ai_input_governance": {
        "is_safe_intent": True,
        "is_mutation_request": False,
        "is_eu_user": False
    },
    "scenario_ape_anthropic": {
        "is_harmful_intent": False,
        "is_policy_compliant": True,
        "is_sensitive_domain": False
    },
    "scenario_ape_langchain": {
        "is_read_only": True,
        "is_execute_step": False,
        "is_vector_search": False,
        "is_tool_call": False
    },
    "scenario_ape_openai": {
        "is_classify": True,
        "is_execute_code": False,
        "is_chat": False
    },
    "scenario_dry_run_auditing": {
        "v1": 10,
        "v2": 25,
        "v3": 30,
        "v4": 0
    },
    "scenario_explainable_decisions": {
        "score": 55
    },
    "scenario_multilanguage_team": {
        "score": 75,
        "threshold": 50,
        "is_flagged": False,
        "manual_override": False
    },
    "scenario_risk_classification": {
        "is_admin": True,
        "is_active": False,
        "credit_score": 450,
        "account_age_days": 100
    },
}

# Additional test cases for multiple execution paths
ADDITIONAL_TEST_CASES = [
    # AI Input Governance: Block unsafe intent
    {
        "scenario": "scenario_ai_input_governance",
        "name": "block_unsafe_intent",
        "context": {"is_safe_intent": False, "is_mutation_request": False, "is_eu_user": False},
        "expected": "blocked"
    },
    # AI Input Governance: Block EU mutation (GDPR)
    {
        "scenario": "scenario_ai_input_governance",
        "name": "block_eu_mutation",
        "context": {"is_safe_intent": True, "is_mutation_request": True, "is_eu_user": True},
        "expected": "blocked"
    },
    # Anthropic: Block harmful intent
    {
        "scenario": "scenario_ape_anthropic",
        "name": "block_harmful",
        "context": {"is_harmful_intent": True, "is_policy_compliant": True, "is_sensitive_domain": False},
        "expected": "unsafe"
    },
    # Anthropic: Review sensitive domain
    {
        "scenario": "scenario_ape_anthropic",
        "name": "review_sensitive",
        "context": {"is_harmful_intent": False, "is_policy_compliant": True, "is_sensitive_domain": True},
        "expected": "review"
    },
    # LangChain: Block tool call in vector search
    {
        "scenario": "scenario_ape_langchain",
        "name": "block_vector_tool",
        "context": {"is_read_only": True, "is_execute_step": False, "is_vector_search": True, "is_tool_call": True},
        "expected": "blocked"
    },
    # LangChain: Block tool call without execution
    {
        "scenario": "scenario_ape_langchain",
        "name": "block_tool_no_exec",
        "context": {"is_read_only": True, "is_execute_step": False, "is_vector_search": False, "is_tool_call": True},
        "expected": "blocked"
    },
    # OpenAI: Block code execution
    {
        "scenario": "scenario_ape_openai",
        "name": "block_code_execution",
        "context": {"is_classify": False, "is_execute_code": True, "is_chat": False},
        "expected": "blocked"
    },
    # OpenAI: Block chat with code execution
    {
        "scenario": "scenario_ape_openai",
        "name": "block_chat_with_code",
        "context": {"is_classify": False, "is_execute_code": True, "is_chat": True},
        "expected": "blocked"
    },
    # Dry-Run: High-risk bonus triggered
    {
        "scenario": "scenario_dry_run_auditing",
        "name": "high_risk_bonus",
        "context": {"v1": 20, "v2": 20, "v3": 20, "v4": 10},
        "expected": 70
    },
    # Dry-Run: Low values (no bonus)
    {
        "scenario": "scenario_dry_run_auditing",
        "name": "low_values",
        "context": {"v1": 10, "v2": 10, "v3": 10, "v4": 5},
        "expected": 0
    },
    # Explainable: Low rating
    {
        "scenario": "scenario_explainable_decisions",
        "name": "low_rating",
        "context": {"score": 20},
        "expected": "low"
    },
    # Explainable: High rating
    {
        "scenario": "scenario_explainable_decisions",
        "name": "high_rating",
        "context": {"score": 70},
        "expected": "high"
    },
    # Explainable: Critical rating
    {
        "scenario": "scenario_explainable_decisions",
        "name": "critical_rating",
        "context": {"score": 85},
        "expected": "critical"
    },
    # Multilanguage: Reject low score
    {
        "scenario": "scenario_multilanguage_team",
        "name": "reject_low_score",
        "context": {"score": 30, "threshold": 50, "is_flagged": False, "manual_override": False},
        "expected": "rejected"
    },
    # Multilanguage: Manual override approval
    {
        "scenario": "scenario_multilanguage_team",
        "name": "manual_override",
        "context": {"score": 30, "threshold": 50, "is_flagged": True, "manual_override": True},
        "expected": "approved"
    },
    # Risk Classification: Low risk
    {
        "scenario": "scenario_risk_classification",
        "name": "low_risk",
        "context": {"is_admin": False, "is_active": True, "credit_score": 700, "account_age_days": 100},
        "expected": "low"
    },
    # Risk Classification: Medium risk
    {
        "scenario": "scenario_risk_classification",
        "name": "medium_risk",
        "context": {"is_admin": False, "is_active": True, "credit_score": 450, "account_age_days": 15},
        "expected": "medium"
    },
]

@pytest.mark.parametrize("tutorial_path", TUTORIAL_FILES, ids=lambda p: p.stem)
def test_tutorial_executes_without_error(tutorial_path):
    """Verify tutorial executes successfully."""
    source = tutorial_path.read_text(encoding='utf-8')
    
    # Get context based on parent directory (scenario name)
    scenario_name = tutorial_path.parent.name
    context = SCENARIO_CONTEXTS.get(scenario_name, {})
    
    # Execute the tutorial
    _result = run(source, context=context)

    # Basic validation: execution completed without errors
    # Note: result can be None for tutorials without explicit returns

@pytest.mark.parametrize("tutorial_path", TUTORIAL_FILES, ids=lambda p: p.stem)
def test_tutorial_matches_expected(tutorial_path):
    """Verify tutorial result matches EXPECT comment."""
    source = tutorial_path.read_text(encoding='utf-8')
    
    # Extract expected value
    expected = extract_expected(source)
    
    if expected is None:
        pytest.skip(f"No EXPECT comment in {tutorial_path.name}")
    
    # Get context based on parent directory (scenario name)
    scenario_name = tutorial_path.parent.name
    context = SCENARIO_CONTEXTS.get(scenario_name, {})
    
    # Execute the tutorial
    result = run(source, context=context)
    
    # Validate result matches expected
    assert result == expected, (
        f"Tutorial {tutorial_path.name} failed validation:\n"
        f"Expected: {expected}\n"
        f"Got: {result}"
    )

@pytest.mark.parametrize("test_case", ADDITIONAL_TEST_CASES, ids=lambda tc: f"{tc['scenario']}_{tc['name']}")
def test_tutorial_additional_paths(test_case):
    """Verify tutorials handle multiple execution paths correctly."""
    scenario = test_case["scenario"]
    context = test_case["context"]
    expected = test_case["expected"]
    
    # Find the tutorial file for this scenario
    scenario_dir = TUTORIALS_DIR / scenario
    ape_files = list(scenario_dir.glob("*.ape"))
    
    # For multilanguage, use tutorial_en.ape
    if scenario == "scenario_multilanguage_team":
        tutorial_path = scenario_dir / "tutorial_en.ape"
    else:
        assert len(ape_files) > 0, f"No tutorial found for {scenario}"
        tutorial_path = ape_files[0]
    
    # Read and execute
    source = tutorial_path.read_text(encoding='utf-8')
    result = run(source, context=context)
    
    # Validate result
    assert result == expected, (
        f"Test case {test_case['name']} failed:\n"
        f"Context: {context}\n"
        f"Expected: {expected}\n"
        f"Got: {result}"
    )
    
    # Execute the tutorial
    result = run(source, context=context)
    
    # Validate result matches expected
    assert result == expected, (
        f"Tutorial {tutorial_path.name} failed validation:\n"
        f"Expected: {expected}\n"
        f"Got: {result}"
    )

def test_all_tutorials_have_expect_comments():
    """Verify all tutorials include EXPECT comments for self-verification."""
    missing = []
    
    for tutorial_path in TUTORIAL_FILES:
        source = tutorial_path.read_text(encoding='utf-8')
        expected = extract_expected(source)
        
        if expected is None:
            missing.append(tutorial_path.name)
    
    assert len(missing) == 0, (
        "The following tutorials are missing EXPECT comments:\n"
        + "\n".join(f"  - {name}" for name in missing)
    )

def test_tutorial_count():
    """Verify we have the expected number of tutorial scenarios."""
    # Expected scenarios:
    # 1. risk_classification
    # 2. ai_input_governance
    # 3. explainable_decisions
    # 4. dry_run_auditing
    # 5. multilanguage_team (EN + NL = 2 files)
    # 6. ape_openai
    # 7. ape_anthropic
    # 8. ape_langchain
    # Total: 9 .ape files (scenario 5 has 2)
    
    assert len(TUTORIAL_FILES) >= 9, (
        f"Expected at least 9 tutorial files, found {len(TUTORIAL_FILES)}\n"
        f"Files found: {[p.name for p in TUTORIAL_FILES]}"
    )

def test_each_scenario_has_readme():
    """Verify each tutorial scenario includes a README.md."""
    missing_readme = []
    
    for tutorial_path in TUTORIAL_FILES:
        readme_path = tutorial_path.parent / "README.md"
        if not readme_path.exists():
            missing_readme.append(tutorial_path.parent.name)
    
    assert len(missing_readme) == 0, (
        "The following scenarios are missing README.md:\n"
        + "\n".join(f"  - {name}" for name in missing_readme)
    )

@pytest.mark.parametrize("scenario", [
    "scenario_risk_classification",
    "scenario_ai_input_governance",
    "scenario_explainable_decisions",
    "scenario_dry_run_auditing",
    "scenario_multilanguage_team",
    "scenario_ape_openai",
    "scenario_ape_anthropic",
    "scenario_ape_langchain"
])
def test_required_scenarios_exist(scenario):
    """Verify all 8 required scenarios are present."""
    scenario_dir = TUTORIALS_DIR / scenario
    assert scenario_dir.exists(), f"Missing required scenario: {scenario}"
    
    # Verify at least one .ape file exists
    ape_files = list(scenario_dir.glob("*.ape"))
    assert len(ape_files) > 0, f"Scenario {scenario} has no .ape files"
    
    # Verify README exists
    readme_path = scenario_dir / "README.md"
    assert readme_path.exists(), f"Scenario {scenario} missing README.md"

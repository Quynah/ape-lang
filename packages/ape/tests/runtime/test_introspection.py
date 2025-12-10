"""
Tests for Runtime Introspection Layer

Tests for ExplanationEngine, ReplayEngine, and Runtime Profiles.
"""

import pytest
from ape.runtime.trace import TraceCollector, TraceEvent
from ape.runtime.explain import ExplanationEngine, ExplanationStep
from ape.runtime.replay import ReplayEngine, ReplayError
from ape.runtime.profile import (
    ProfileError,
    get_profile,
    list_profiles,
    create_context_from_profile,
    create_executor_config_from_profile,
    get_profile_description,
    validate_profile,
    register_profile,
)
from ape.runtime.executor import RuntimeExecutor


class TestExplanationEngine:
    """Tests for ExplanationEngine"""
    
    def test_explanation_engine_initialization(self):
        """Test that ExplanationEngine can be initialized"""
        engine = ExplanationEngine()
        assert engine is not None
    
    def test_explain_empty_trace(self):
        """Test explanation of empty trace"""
        engine = ExplanationEngine()
        trace = TraceCollector()
        
        explanations = engine.from_trace(trace)
        
        assert len(explanations) == 0
    
    def test_explain_if_node_true(self):
        """Test explanation of IF node with true condition"""
        engine = ExplanationEngine()
        trace = TraceCollector()
        
        # Create IF enter/exit events
        enter = TraceEvent(
            node_type="IF",
            phase="enter",
            context_snapshot={"x": 5},
            metadata={"condition_result": True, "branch_taken": "then"}
        )
        exit_event = TraceEvent(
            node_type="IF",
            phase="exit",
            context_snapshot={"x": 5, "y": 10},
            result=None
        )
        
        trace.record(enter)
        trace.record(exit_event)
        
        explanations = engine.from_trace(trace)
        
        assert len(explanations) == 1
        assert explanations[0].node_type == "IF"
        assert "true" in explanations[0].summary.lower()
        assert "then" in explanations[0].summary.lower()
    
    def test_explain_if_node_false(self):
        """Test explanation of IF node with false condition"""
        engine = ExplanationEngine()
        trace = TraceCollector()
        
        enter = TraceEvent(
            node_type="IF",
            phase="enter",
            context_snapshot={"x": 5},
            metadata={"condition_result": False, "branch_taken": "else"}
        )
        exit_event = TraceEvent(
            node_type="IF",
            phase="exit",
            context_snapshot={"x": 5},
            result=None
        )
        
        trace.record(enter)
        trace.record(exit_event)
        
        explanations = engine.from_trace(trace)
        
        assert len(explanations) == 1
        assert "false" in explanations[0].summary.lower()
        assert "else" in explanations[0].summary.lower()
    
    def test_explain_while_node(self):
        """Test explanation of WHILE node"""
        engine = ExplanationEngine()
        trace = TraceCollector()
        
        enter = TraceEvent(
            node_type="WHILE",
            phase="enter",
            context_snapshot={"i": 0},
            metadata={"iterations": 3, "final_condition_result": False}
        )
        exit_event = TraceEvent(
            node_type="WHILE",
            phase="exit",
            context_snapshot={"i": 3},
            result=None
        )
        
        trace.record(enter)
        trace.record(exit_event)
        
        explanations = engine.from_trace(trace)
        
        assert len(explanations) == 1
        assert explanations[0].node_type == "WHILE"
        assert "3" in explanations[0].summary
        assert "iterations" in explanations[0].summary.lower()
    
    def test_explain_for_node(self):
        """Test explanation of FOR node"""
        engine = ExplanationEngine()
        trace = TraceCollector()
        
        enter = TraceEvent(
            node_type="FOR",
            phase="enter",
            context_snapshot={},
            metadata={"collection_size": 5, "loop_var": "item", "iterations": 2}
        )
        exit_event = TraceEvent(
            node_type="FOR",
            phase="exit",
            context_snapshot={"item": "value"},
            result=None
        )
        
        trace.record(enter)
        trace.record(exit_event)
        
        explanations = engine.from_trace(trace)
        
        assert len(explanations) == 1
        assert explanations[0].node_type == "FOR"
        assert "5" in explanations[0].summary
        assert "collection" in explanations[0].summary.lower()
    
    def test_explain_expression_with_dry_run(self):
        """Test explanation of EXPRESSION in dry-run mode"""
        engine = ExplanationEngine()
        trace = TraceCollector()
        
        enter = TraceEvent(
            node_type="EXPRESSION",
            phase="enter",
            context_snapshot={"x": 5},
            metadata={"variable": "y", "dry_run": True}
        )
        exit_event = TraceEvent(
            node_type="EXPRESSION",
            phase="exit",
            context_snapshot={"x": 5},
            result=10
        )
        
        trace.record(enter)
        trace.record(exit_event)
        
        explanations = engine.from_trace(trace)
        
        assert len(explanations) == 1
        assert "would be set" in explanations[0].summary.lower()
        assert "y" in explanations[0].summary
        assert explanations[0].details["dry_run"] is True
    
    def test_explanation_step_structure(self):
        """Test ExplanationStep data structure"""
        step = ExplanationStep(
            index=0,
            node_type="IF",
            summary="Test summary",
            details={"key": "value"}
        )
        
        assert step.index == 0
        assert step.node_type == "IF"
        assert step.summary == "Test summary"
        assert step.details["key"] == "value"
    
    def test_explain_multiple_events(self):
        """Test explanation of multiple consecutive events"""
        engine = ExplanationEngine()
        trace = TraceCollector()
        
        # First IF
        trace.record(TraceEvent("IF", "enter", {"x": 1}, metadata={"condition_result": True, "branch_taken": "then"}))
        trace.record(TraceEvent("IF", "exit", {"x": 1, "y": 2}, None))
        
        # Second WHILE
        trace.record(TraceEvent("WHILE", "enter", {"y": 2}, metadata={"iterations": 1, "final_condition_result": False}))
        trace.record(TraceEvent("WHILE", "exit", {"y": 3}, None))
        
        explanations = engine.from_trace(trace)
        
        assert len(explanations) == 2
        assert explanations[0].node_type == "IF"
        assert explanations[1].node_type == "WHILE"


class TestReplayEngine:
    """Tests for ReplayEngine"""
    
    def test_replay_engine_initialization(self):
        """Test that ReplayEngine can be initialized"""
        engine = ReplayEngine()
        assert engine is not None
    
    def test_replay_empty_trace(self):
        """Test replay of empty trace"""
        engine = ReplayEngine()
        trace = TraceCollector()
        
        replayed = engine.replay(trace)
        
        assert len(replayed) == 0
    
    def test_replay_valid_paired_events(self):
        """Test replay of valid enter/exit pairs"""
        engine = ReplayEngine()
        trace = TraceCollector()
        
        trace.record(TraceEvent("IF", "enter", {"x": 1}, metadata={}))
        trace.record(TraceEvent("IF", "exit", {"x": 1}, None))
        
        replayed = engine.replay(trace)
        
        assert len(replayed) == 2
        assert replayed.events()[0].node_type == "IF"
        assert replayed.events()[0].phase == "enter"
        assert replayed.events()[1].phase == "exit"
    
    def test_replay_nested_events(self):
        """Test replay of nested enter/exit events"""
        engine = ReplayEngine()
        trace = TraceCollector()
        
        # Outer IF
        trace.record(TraceEvent("IF", "enter", {"x": 1}, metadata={}))
        # Nested WHILE
        trace.record(TraceEvent("WHILE", "enter", {"x": 1}, metadata={}))
        trace.record(TraceEvent("WHILE", "exit", {"x": 2}, None))
        # Close outer IF
        trace.record(TraceEvent("IF", "exit", {"x": 2}, None))
        
        replayed = engine.replay(trace)
        
        assert len(replayed) == 4
    
    def test_replay_fails_on_mismatch(self):
        """Test replay fails when enter/exit don't match"""
        engine = ReplayEngine()
        trace = TraceCollector()
        
        # IF enter, but WHILE exit
        trace.record(TraceEvent("IF", "enter", {"x": 1}, metadata={}))
        trace.record(TraceEvent("WHILE", "exit", {"x": 1}, None))
        
        with pytest.raises(ReplayError) as exc_info:
            engine.replay(trace)
        
        assert "mismatch" in str(exc_info.value).lower()
    
    def test_replay_fails_on_unclosed_events(self):
        """Test replay fails when events aren't closed"""
        engine = ReplayEngine()
        trace = TraceCollector()
        
        # Only enter, no exit
        trace.record(TraceEvent("IF", "enter", {"x": 1}, metadata={}))
        
        with pytest.raises(ReplayError) as exc_info:
            engine.replay(trace)
        
        assert "unclosed" in str(exc_info.value).lower()
    
    def test_replay_fails_on_exit_without_enter(self):
        """Test replay fails on exit without enter"""
        engine = ReplayEngine()
        trace = TraceCollector()
        
        # Exit without enter
        trace.record(TraceEvent("IF", "exit", {"x": 1}, None))
        
        with pytest.raises(ReplayError):
            engine.replay(trace)
    
    def test_validate_determinism_identical_traces(self):
        """Test determinism validation with identical traces"""
        engine = ReplayEngine()
        
        trace1 = TraceCollector()
        trace1.record(TraceEvent("IF", "enter", {"x": 1}, metadata={}))
        trace1.record(TraceEvent("IF", "exit", {"x": 1}, None))
        
        trace2 = TraceCollector()
        trace2.record(TraceEvent("IF", "enter", {"x": 1}, metadata={}))
        trace2.record(TraceEvent("IF", "exit", {"x": 1}, None))
        
        result = engine.validate_determinism(trace1, trace2)
        
        assert result is True
    
    def test_validate_determinism_different_length(self):
        """Test determinism validation fails on different lengths"""
        engine = ReplayEngine()
        
        trace1 = TraceCollector()
        trace1.record(TraceEvent("IF", "enter", {"x": 1}, metadata={}))
        
        trace2 = TraceCollector()
        trace2.record(TraceEvent("IF", "enter", {"x": 1}, metadata={}))
        trace2.record(TraceEvent("IF", "exit", {"x": 1}, None))
        
        with pytest.raises(ReplayError) as exc_info:
            engine.validate_determinism(trace1, trace2)
        
        assert "length mismatch" in str(exc_info.value).lower()
    
    def test_validate_determinism_different_node_types(self):
        """Test determinism validation fails on different node types"""
        engine = ReplayEngine()
        
        trace1 = TraceCollector()
        trace1.record(TraceEvent("IF", "enter", {"x": 1}, metadata={}))
        
        trace2 = TraceCollector()
        trace2.record(TraceEvent("WHILE", "enter", {"x": 1}, metadata={}))
        
        with pytest.raises(ReplayError) as exc_info:
            engine.validate_determinism(trace1, trace2)
        
        assert "node_type mismatch" in str(exc_info.value).lower()


class TestRuntimeProfiles:
    """Tests for Runtime Profiles"""
    
    def test_list_profiles(self):
        """Test listing available profiles"""
        profiles = list_profiles()
        
        assert "analysis" in profiles
        assert "execution" in profiles
        assert "audit" in profiles
        assert "debug" in profiles
        assert "test" in profiles
    
    def test_get_profile_analysis(self):
        """Test getting analysis profile"""
        profile = get_profile("analysis")
        
        assert profile["dry_run"] is True
        assert profile["tracing"] is True
        assert profile["capabilities"] == []
    
    def test_get_profile_execution(self):
        """Test getting execution profile"""
        profile = get_profile("execution")
        
        assert profile["dry_run"] is False
        assert profile["tracing"] is False
        assert profile["capabilities"] == ["*"]
    
    def test_get_profile_audit(self):
        """Test getting audit profile"""
        profile = get_profile("audit")
        
        assert profile["dry_run"] is True
        assert profile["tracing"] is True
        assert profile["capabilities"] == ["*"]
    
    def test_get_profile_invalid(self):
        """Test getting invalid profile raises error"""
        with pytest.raises(ProfileError) as exc_info:
            get_profile("nonexistent")
        
        assert "unknown profile" in str(exc_info.value).lower()
    
    def test_get_profile_description(self):
        """Test getting profile description"""
        desc = get_profile_description("analysis")
        
        assert isinstance(desc, str)
        assert len(desc) > 0
    
    def test_create_context_from_profile_analysis(self):
        """Test creating context from analysis profile"""
        context = create_context_from_profile("analysis")
        
        assert context.dry_run is True
        assert not context.has_capability("io.read")
    
    def test_create_context_from_profile_execution(self):
        """Test creating context from execution profile"""
        context = create_context_from_profile("execution")
        
        assert context.dry_run is False
        assert context.has_capability("io.read")
        assert context.has_capability("io.write")
    
    def test_create_executor_config_from_profile(self):
        """Test creating executor config from profile"""
        config = create_executor_config_from_profile("debug")
        
        assert config["max_iterations"] == 1_000
        assert config["dry_run"] is False
        assert "trace" in config
        assert isinstance(config["trace"], TraceCollector)
    
    def test_validate_profile_valid(self):
        """Test validating valid profile"""
        profile = {
            "description": "Test profile",
            "dry_run": True,
            "tracing": True,
            "capabilities": ["io.read"],
            "max_iterations": 5000
        }
        
        validate_profile(profile)  # Should not raise
    
    def test_validate_profile_missing_key(self):
        """Test validating profile with missing key"""
        profile = {
            "description": "Test profile",
            "dry_run": True,
            # Missing other keys
        }
        
        with pytest.raises(ProfileError):
            validate_profile(profile)
    
    def test_validate_profile_invalid_type(self):
        """Test validating profile with invalid type"""
        profile = {
            "description": "Test profile",
            "dry_run": "not a boolean",  # Invalid type
            "tracing": True,
            "capabilities": [],
            "max_iterations": 1000
        }
        
        with pytest.raises(ProfileError):
            validate_profile(profile)
    
    def test_register_custom_profile(self):
        """Test registering custom profile"""
        custom = {
            "description": "Custom test profile",
            "dry_run": False,
            "tracing": True,
            "capabilities": ["custom.capability"],
            "max_iterations": 500
        }
        
        register_profile("custom_test", custom)
        
        assert "custom_test" in list_profiles()
        retrieved = get_profile("custom_test")
        assert retrieved["max_iterations"] == 500
    
    def test_register_profile_duplicate_name(self):
        """Test registering profile with duplicate name fails"""
        with pytest.raises(ProfileError):
            register_profile("analysis", {})  # analysis already exists


class TestIntegration:
    """Integration tests combining multiple introspection features"""
    
    def test_trace_explain_replay_workflow(self):
        """Test complete workflow: trace -> explain -> replay"""
        # Create trace
        trace = TraceCollector()
        trace.record(TraceEvent("IF", "enter", {"x": 5}, metadata={"condition_result": True, "branch_taken": "then"}))
        trace.record(TraceEvent("IF", "exit", {"x": 5, "y": 10}, None))
        
        # Explain
        explainer = ExplanationEngine()
        explanations = explainer.from_trace(trace)
        assert len(explanations) == 1
        assert "true" in explanations[0].summary.lower()
        
        # Replay
        replayer = ReplayEngine()
        replayed = replayer.replay(trace)
        assert len(replayed) == 2
    
    def test_profile_executor_integration(self):
        """Test profile integration with executor"""
        config = create_executor_config_from_profile("analysis")
        
        # Create executor with profile config
        executor = RuntimeExecutor(**config)
        
        assert executor.dry_run is True
        assert executor.trace is not None
        assert isinstance(executor.trace, TraceCollector)

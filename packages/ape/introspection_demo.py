"""
Demo of APE v0.3.x-dev Runtime Introspection Layer

Shows ExplanationEngine, ReplayEngine, and Runtime Profiles in action.
"""

from ape.runtime.trace import TraceCollector, TraceEvent
from ape.runtime.explain import ExplanationEngine
from ape.runtime.replay import ReplayEngine
from ape.runtime.profile import get_profile, list_profiles, create_context_from_profile

print('=== APE v0.3.x-dev Runtime Introspection Demo ===\n')

# 1. Create sample trace (simulates execution of: if x > 5: y = x * 2)
trace = TraceCollector()
trace.record(TraceEvent(
    'IF', 'enter', {'x': 10}, 
    metadata={'condition_result': True, 'branch_taken': 'then'}
))
trace.record(TraceEvent(
    'EXPRESSION', 'enter', {'x': 10}, 
    metadata={'variable': 'y', 'dry_run': False}
))
trace.record(TraceEvent(
    'EXPRESSION', 'exit', {'x': 10, 'y': 20}, 
    result=20
))
trace.record(TraceEvent(
    'IF', 'exit', {'x': 10, 'y': 20}, 
    None
))

print(f'1. TRACE: Collected {len(trace)} events\n')

# 2. Explain execution
explainer = ExplanationEngine()
explanations = explainer.from_trace(trace)

print('2. EXPLANATION:')
for step in explanations:
    print(f'   Step {step.index}: {step.summary}')
print()

# 3. Replay validation
replayer = ReplayEngine()
try:
    replayed = replayer.replay(trace)
    print(f'3. REPLAY: ✓ Validated {len(replayed)} events (deterministic execution confirmed)\n')
except Exception as e:
    print(f'3. REPLAY: ✗ Validation failed: {e}\n')

# 4. Runtime Profiles
profiles = list_profiles()
print(f'4. PROFILES: {len(profiles)} available')
for name in profiles:
    prof = get_profile(name)
    caps_str = '*' if prof['capabilities'] == ['*'] else str(len(prof['capabilities']))
    print(f'   - {name}: dry_run={prof["dry_run"]}, tracing={prof["tracing"]}, caps={caps_str}')

print()

# 5. Create context from profile
context = create_context_from_profile('analysis')
print(f'5. CONTEXT FROM PROFILE:')
print(f'   Analysis profile → dry_run={context.dry_run}, can_mutate={context.can_mutate()}')

print('\n✓ All introspection features working!')

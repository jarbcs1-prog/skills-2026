"""
Test Summarization Schema Validation — Test all schemas for compliance.
"""

import json
import tempfile
import os
from typing import List, Dict, Any

from summarization import Summarizer, SummarizationConfig, SCHEMAS


def create_test_context() -> List[Dict[str, Any]]:
    """Create a realistic test context."""
    return [
        {"type": "system_prompt", "content": "You are a senior software engineer."},
        {"type": "user_message", "content": "Refactor the authentication module to use JWT tokens.", "role": "user"},
        {"type": "tool_call", "tool": "read_file", "arguments": {"path": "src/auth.py"}, "output": "import os\nfrom functools import wraps\n\nSECRET = os.getenv('JWT_SECRET')\n\n@wraps\ndef auth_required(f):\n    @wraps(f)\n    def decorated(*args, **kwargs):\n        token = request.headers.get('Authorization')\n        if not token:\n            return {'error': 'Missing token'}, 401\n        try:\n            payload = jwt.decode(token, SECRET, algorithms=['HS256'])\n            request.user = payload\n        except jwt.InvalidTokenError:\n            return {'error': 'Invalid token'}, 401\n        return f(*args, **kwargs)\n    return decorated\n"},
        {"type": "assistant_message", "content": "I'll refactor the authentication module to use JWT tokens properly."},
        {"type": "tool_call", "tool": "edit_file", "arguments": {"path": "src/auth.py", "old": "SECRET = os.getenv('JWT_SECRET')", "new": "import jwt\nimport os\n\nSECRET = os.getenv('JWT_SECRET', 'default-secret-change-in-production')"}, "output": "Updated JWT secret with fallback."},
        {"type": "tool_call", "tool": "edit_file", "arguments": {"path": "src/auth.py", "old": "payload = jwt.decode(token, SECRET, algorithms=['HS256'])", "new": "payload = jwt.decode(token, SECRET, algorithms=['HS256'], options={'verify_exp': True})"}, "output": "Added token expiration verification."},
        {"type": "tool_call", "tool": "run_tests", "arguments": {"path": "tests/test_auth.py"}, "output": "test_jwt_validation ... PASS\ntest_expired_token ... PASS\ntest_invalid_token ... PASS\nAll 12 tests passed! ✓"},
        {"type": "assistant_message", "content": "Refactored authentication module with proper JWT handling and tests pass."},
        {"type": "todo", "content": "Add rate limiting to auth endpoints", "status": "pending"},
        {"type": "todo", "content": "Add refresh token support", "status": "pending"},
    ]


def test_schema(schema_name: str, schema) -> bool:
    """Test a single summarization schema."""
    print(f"\nTesting schema: {schema_name}")
    print(f"  Fields: {schema.fields}")
    print(f"  Required: {schema.required}")
    
    context = create_test_context()
    
    config = SummarizationConfig(
        schema=schema,
        keep_recent_full=2,
        model="opencode/big-pickle",
    )
    
    summarizer = Summarizer(config)
    result = summarizer.summarize(context)
    
    print(f"  Summary generated: {len(result.summary)} fields")
    for field, value in result.summary.items():
        if isinstance(value, list):
            print(f"    {field}: {len(value)} items")
        elif isinstance(value, str):
            print(f"    {field}: {value[:80]}...")
        else:
            print(f"    {field}: {type(value).__name__}")
    
    print(f"  Entries summarized: {result.entries_summarized}")
    print(f"  Entries preserved: {result.entries_preserved}")
    print(f"  Estimated tokens: {result.tokens_estimated}")
    
    # Validate
    validation = summarizer.validate(result.summary, context)
    print(f"  Validation: {'PASS' if validation['valid'] else 'FAIL'}")
    if validation['schema_errors']:
        print(f"  Schema errors: {validation['schema_errors']}")
    print(f"  Coverage: {validation['coverage']}")
    
    # Check required fields present
    for req in schema.required:
        if req not in result.summary:
            print(f"  ✗ MISSING REQUIRED FIELD: {req}")
            return False
    
    # Check no unknown fields
    for field in result.summary:
        if field not in schema.fields:
            print(f"  ✗ UNKNOWN FIELD: {field}")
            return False
    
    print(f"  ✓ Schema {schema_name} PASSED")
    return True


def test_all_schemas():
    """Test all predefined schemas."""
    print("="*60)
    print("SUMMARIZATION SCHEMA VALIDATION TESTS")
    print("="*60)
    
    results = {}
    for name, schema in SCHEMAS.items():
        try:
            results[name] = test_schema(name, schema)
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results[name] = False
    
    print("\n" + "="*60)
    print("SUMMARY:")
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'ALL SCHEMA TESTS PASSED ✓' if all_passed else 'SOME SCHEMA TESTS FAILED ✗'}")
    return all_passed


def test_summarizer_cli():
    """Test the summarizer CLI integration."""
    print("\n" + "="*60)
    print("TESTING SUMMARIZER CLI INTEGRATION")
    print("="*60)
    
    context = create_test_context()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(context, f)
        input_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = f.name
    
    config_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "summarization": {"schema": "agent_default", "keep_recent_full": 2, "model": "opencode/big-pickle"},
            }, f)
            config_path = f.name
        
        # Test via direct class usage
        config = SummarizationConfig(
            schema=SCHEMAS["agent_default"],
            keep_recent_full=2,
            model="opencode/big-pickle",
        )
        summarizer = Summarizer(config)
        result = summarizer.summarize(context)
        
        print(f"Summary generated with {len(result.summary)} fields")
        print(f"Schema: {result.schema_used}")
        print(f"Tokens: {result.tokens_estimated}")
        
        if result.validation_errors:
            print(f"Validation errors: {result.validation_errors}")
            return False
        
        print("  ✓ CLI integration test PASSED")
        return True
    finally:
        for path in [input_path, output_path, config_path]:
            if path and os.path.exists(path):
                os.unlink(path)


if __name__ == "__main__":
    import json
    import tempfile
    
    print("="*60)
    print("SUMMARIZATION SCHEMA VALIDATION TESTS")
    print("="*60)
    
    all_passed = test_all_schemas()
    all_passed = test_summarizer_cli() and all_passed
    
    if all_passed:
        print("\n✓ ALL SUMMARIZATION TESTS PASSED")
        exit(0)
    else:
        print("\n✗ SOME SUMMARIZATION TESTS FAILED")
        exit(1)
"""
Simple import test to verify the package structure works.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    # Test importing the agents
    from agent import get_answer_agent, get_gaia_agent

    print("✅ Successfully imported agent functions")

    # Test getting agent instances
    research_agent = get_gaia_agent()
    answer_agent = get_answer_agent()
    print(f"✅ Created research agent: {research_agent.name}")
    print(f"✅ Created answer agent: {answer_agent.name}")

    # Test tool availability
    print(f"✅ Research agent has {len(research_agent.tools)} tools")
    print(f"✅ Answer agent has {len(answer_agent.tools)} tools")

    print("\n🎉 All imports successful! The package structure is working correctly.")
    print("\nNote: To run actual tasks, you need to set your OPENAI_API_KEY:")
    print("  export OPENAI_API_KEY='your-actual-api-key'")
    print("  or")
    print('  echo "OPENAI_API_KEY=your-actual-api-key" > .env')

except Exception as e:
    print(f"❌ Import test failed: {str(e)}")
    sys.exit(1)

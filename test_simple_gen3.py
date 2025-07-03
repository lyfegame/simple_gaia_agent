#!/usr/bin/env python3
"""
Simple test suite for Generation 3 improvements.
Just validates that tools can be imported and have correct structure.
"""

import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_generation3_improvements():
    """Test that Generation 3 improvements are available."""

    logger.info("🧪 Testing Generation 3 Improvements")
    logger.info("=" * 50)

    # Test 1: Tool imports
    logger.info("\n1. Testing tool imports...")
    try:
        from tools import (
            analyze_image_with_ocr,
            mathematical_reasoning,
            analyze_youtube_video,
            validate_reasoning,
            analyze_graph_traversal,
            GAIA_TOOLS,
            ANSWER_TOOLS
        )
        logger.info(f"✅ All new tools imported successfully")
        logger.info(f"📊 Total GAIA tools: {len(GAIA_TOOLS)}")
        logger.info(f"📊 Answer tools: {len(ANSWER_TOOLS)}")
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

    # Test 2: Agent improvements
    logger.info("\n2. Testing agent improvements...")
    try:
        from agent import gaia_agent, answer_agent

        # Check that new tools are in agent toolset
        tool_names = [tool.name if hasattr(tool, 'name') else str(type(tool).__name__) for tool in gaia_agent.tools]

        expected_tools = [
            'analyze_image_with_ocr',
            'mathematical_reasoning',
            'analyze_youtube_video',
            'validate_reasoning',
            'analyze_graph_traversal'
        ]

        found_tools = []
        for expected in expected_tools:
            if any(expected in tool_name for tool_name in tool_names):
                found_tools.append(expected)
                logger.info(f"✅ Found tool: {expected}")
            else:
                logger.warning(f"⚠️ Tool not found in agent: {expected}")

        logger.info(f"📊 Found {len(found_tools)}/{len(expected_tools)} new tools in agent")

    except ImportError as e:
        logger.error(f"❌ Agent import failed: {e}")
        return False

    # Test 3: Dependencies check
    logger.info("\n3. Testing dependencies...")

    dependencies = {
        "opencv-python": "cv2",
        "numpy": "numpy",
        "yt-dlp": "yt_dlp",
        "pytesseract": "pytesseract"
    }

    available_deps = []
    missing_deps = []

    for dep_name, import_name in dependencies.items():
        try:
            __import__(import_name)
            available_deps.append(dep_name)
            logger.info(f"✅ {dep_name} available")
        except ImportError:
            missing_deps.append(dep_name)
            logger.warning(f"⚠️ {dep_name} missing")

    logger.info(f"📊 Dependencies: {len(available_deps)}/{len(dependencies)} available")

    # Test 4: Enhanced instructions check
    logger.info("\n4. Testing enhanced instructions...")

    instructions = gaia_agent.instructions
    enhancement_keywords = [
        "analyze_image_with_ocr",
        "mathematical_reasoning",
        "validate_reasoning",
        "REASONING VALIDATION PROTOCOL",
        "visual analysis tasks",
        "statistical/mathematical tasks"
    ]

    found_enhancements = []
    for keyword in enhancement_keywords:
        if keyword in instructions:
            found_enhancements.append(keyword)
            logger.info(f"✅ Found instruction enhancement: {keyword}")
        else:
            logger.warning(f"⚠️ Missing instruction enhancement: {keyword}")

    logger.info(f"📊 Instructions: {len(found_enhancements)}/{len(enhancement_keywords)} enhancements found")

    # Test 5: Documentation check
    logger.info("\n5. Testing documentation...")
    try:
        with open('changes_log/3.md', 'r') as f:
            doc_content = f.read()
            if "Generation 3 Improvements" in doc_content and "Multimodal" in doc_content:
                logger.info("✅ Generation 3 documentation found")
                doc_available = True
            else:
                logger.warning("⚠️ Documentation incomplete")
                doc_available = False
    except FileNotFoundError:
        logger.warning("⚠️ Generation 3 documentation not found")
        doc_available = False

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 GENERATION 3 READINESS SUMMARY")
    logger.info("=" * 50)

    total_score = 0
    max_score = 5

    # Tool imports (critical)
    if len(found_tools) >= len(expected_tools):
        logger.info("✅ Tools: All new tools successfully integrated")
        total_score += 1
    else:
        logger.warning("⚠️ Tools: Some tools missing from agent")

    # Dependencies (important but not critical)
    if len(available_deps) >= 3:
        logger.info("✅ Dependencies: Most required dependencies available")
        total_score += 1
    elif len(available_deps) >= 2:
        logger.info("⚠️ Dependencies: Some dependencies missing but core functionality available")
        total_score += 0.5
    else:
        logger.warning("❌ Dependencies: Critical dependencies missing")

    # Instructions (critical)
    if len(found_enhancements) >= 4:
        logger.info("✅ Instructions: Enhanced agent instructions integrated")
        total_score += 1
    else:
        logger.warning("⚠️ Instructions: Some instruction enhancements missing")

    # Agent integration (critical)
    if len(found_tools) > 0:
        logger.info("✅ Integration: New tools available in agent")
        total_score += 1
    else:
        logger.warning("❌ Integration: Tools not properly integrated")

    # Documentation (nice to have)
    if doc_available:
        logger.info("✅ Documentation: Complete documentation available")
        total_score += 1
    else:
        logger.info("⚠️ Documentation: Missing or incomplete")

    percentage = (total_score / max_score) * 100
    logger.info(f"\n🎯 Overall Readiness: {total_score}/{max_score} ({percentage:.1f}%)")

    if percentage >= 80:
        logger.info("🎉 Generation 3 improvements successfully implemented!")
        logger.info("🚀 Ready for enhanced GAIA benchmark performance")
        return True
    elif percentage >= 60:
        logger.info("✅ Generation 3 improvements mostly ready")
        logger.info("⚠️ Some optional features may not work without missing dependencies")
        return True
    else:
        logger.warning("🚨 Generation 3 improvements incomplete")
        logger.warning("❌ Major issues need to be resolved")
        return False

if __name__ == "__main__":
    success = test_generation3_improvements()
    sys.exit(0 if success else 1)
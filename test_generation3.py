#!/usr/bin/env python3
"""
Test suite for Generation 3 improvements.
Validates that new tools can be imported and basic functionality works.
"""

import sys
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tool_imports():
    """Test that all new tools can be imported successfully."""
    try:
        from tools import (
            analyze_image_with_ocr,
            mathematical_reasoning,
            analyze_youtube_video,
            validate_reasoning,
            analyze_graph_traversal,
            GAIA_TOOLS
        )
        logger.info("✅ All new tools imported successfully")
        logger.info(f"Total GAIA tools available: {len(GAIA_TOOLS)}")
        return True
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

async def test_mathematical_reasoning():
    """Test mathematical reasoning tool with sample data."""
    try:
        from tools import mathematical_reasoning

        # Test basic statistics
        test_data = "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
        result = await mathematical_reasoning.on_invoke_tool(
            ctx=None,
            input={"data": test_data, "operation": "statistics"}
        )

        if "Mean: 5.500000" in result and "Count: 10" in result:
            logger.info("✅ Mathematical reasoning tool working correctly")
            return True
        else:
            logger.error("❌ Mathematical reasoning tool not producing expected results")
            logger.error(f"Result: {result[:200]}...")
            return False
    except Exception as e:
        logger.error(f"❌ Mathematical reasoning test failed: {e}")
        return False

async def test_validate_reasoning():
    """Test reasoning validation tool."""
    try:
        from tools import validate_reasoning

        claim = "The average of 1, 2, 3, 4, 5 is 3"
        evidence = "Calculated using the formula: (1+2+3+4+5)/5 = 15/5 = 3"
        context = "mathematical calculation task"

        result = await validate_reasoning.on_invoke_tool(
            ctx=None,
            input={"claim": claim, "evidence": evidence, "task_context": context}
        )

        if "Confidence Level:" in result and "STEP 1:" in result:
            logger.info("✅ Reasoning validation tool working correctly")
            return True
        else:
            logger.error("❌ Reasoning validation tool not producing expected format")
            logger.error(f"Result: {result[:200]}...")
            return False
    except Exception as e:
        logger.error(f"❌ Reasoning validation test failed: {e}")
        return False

async def test_graph_traversal():
    """Test graph traversal tool with simple graph."""
    try:
        from tools import analyze_graph_traversal

        # Simple graph: A-B, B-C, C-D
        graph_data = "A-B, B-C, C-D"
        result = await analyze_graph_traversal.on_invoke_tool(
            ctx=None,
            input={"graph_data": graph_data, "analysis_type": "connectivity"}
        )

        if "Graph is connected" in result and "Nodes:" in result:
            logger.info("✅ Graph traversal tool working correctly")
            return True
        else:
            logger.error("❌ Graph traversal tool not producing expected results")
            logger.error(f"Result: {result[:200]}...")
            return False
    except Exception as e:
        logger.error(f"❌ Graph traversal test failed: {e}")
        return False

def test_image_analysis_dependencies():
    """Test if image analysis dependencies are available."""
    missing_deps = []

    try:
        import cv2
        logger.info("✅ OpenCV available")
    except ImportError:
        missing_deps.append("opencv-python")

    try:
        import pytesseract
        logger.info("✅ PyTesseract available")
    except ImportError:
        missing_deps.append("pytesseract")

    try:
        import numpy as np
        logger.info("✅ NumPy available")
    except ImportError:
        missing_deps.append("numpy")

    if missing_deps:
        logger.warning(f"⚠️  Missing dependencies for image analysis: {missing_deps}")
        logger.warning("Image analysis will not work until these are installed")
        return False
    else:
        logger.info("✅ All image analysis dependencies available")
        return True

def test_video_analysis_dependencies():
    """Test if video analysis dependencies are available."""
    try:
        import yt_dlp
        logger.info("✅ yt-dlp available for video analysis")
        return True
    except ImportError:
        logger.warning("⚠️  yt-dlp not available - video analysis will not work")
        return False

async def run_all_tests():
    """Run all tests and report results."""
    logger.info("🧪 Starting Generation 3 Tool Tests")
    logger.info("=" * 50)

    tests = [
        ("Tool Imports", test_tool_imports),
        ("Mathematical Reasoning", test_mathematical_reasoning),
        ("Reasoning Validation", test_validate_reasoning),
        ("Graph Traversal", test_graph_traversal),
        ("Image Analysis Dependencies", test_image_analysis_dependencies),
        ("Video Analysis Dependencies", test_video_analysis_dependencies),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        logger.info("🎉 All tests passed! Generation 3 tools are ready.")
    elif passed >= total * 0.75:
        logger.info("⚠️  Most tests passed. Some optional dependencies missing.")
    else:
        logger.warning("🚨 Multiple test failures. Check dependencies and tool implementations.")

    return passed, total

if __name__ == "__main__":
    asyncio.run(run_all_tests())
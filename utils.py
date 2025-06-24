import logging
import sys
from agents import (
    HandoffOutputItem,
    ItemHelpers,
    MessageOutputItem,
    ToolCallItem,
    ToolCallOutputItem,
)
from openai.types.responses import ResponseFunctionToolCall

logger = logging.getLogger(__name__)


class AppOnlyFilter(logging.Filter):
    """Filter to only show logs from our application modules."""

    def filter(self, record):
        app_modules = ["__main__", "utils", "agent", "tools", "agents"]
        return any(record.name.startswith(module) for module in app_modules)


def configure_logging():
    """Configure logging for the application."""
    # Standard logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Add filter to suppress third-party logs
    for handler in logging.root.handlers:
        handler.addFilter(AppOnlyFilter())


def log_agent_output(result):
    """Log agent output in a clean, readable format."""

    # Log each new item with simplified information
    for new_item in result.new_items:
        agent_name = new_item.agent.name
        if isinstance(new_item, MessageOutputItem):
            logger.info(f"{agent_name}: {ItemHelpers.text_message_output(new_item)}")
        elif isinstance(new_item, HandoffOutputItem):
            logger.info(
                f"Handed off from {new_item.source_agent.name} to {new_item.target_agent.name}"
            )
        elif isinstance(new_item, ToolCallItem):
            if isinstance(
                new_item.raw_item,
                (ResponseFunctionToolCall,),
            ):
                logger.info(
                    f"{agent_name}: Tool call: {new_item.raw_item.name}({new_item.raw_item.arguments})"
                )
            else:
                logger.info(f"{agent_name}: Tool call: {new_item.raw_item}")
        elif isinstance(new_item, ToolCallOutputItem):
            logger.info(f"{agent_name}: Tool call output: {new_item.output}")
        else:
            logger.info(f"{agent_name}: Skipping item: {new_item.__class__.__name__}")

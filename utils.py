import logging
import sys

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
        agent_name = new_item.agent.name if hasattr(new_item, "agent") else "Unknown"
        item_type = new_item.__class__.__name__

        # Handle different types of items with clean, concise logging
        if "Message" in item_type:
            # Extract just the text content from message
            if hasattr(new_item, "raw_item") and hasattr(new_item.raw_item, "content"):
                # Get the actual message text
                content = new_item.raw_item.content
                if isinstance(content, list) and len(content) > 0:
                    message_text = (
                        content[0].text
                        if hasattr(content[0], "text")
                        else str(content[0])
                    )
                else:
                    message_text = str(content)
            else:
                message_text = getattr(new_item, "content", str(new_item))

            # Clean up agent name for display
            display_name = agent_name.replace("_", " ").title()
            logger.info(f"💬 {display_name}: {message_text}")

        elif "Handoff" in item_type:
            # Clean handoff logging
            source = getattr(new_item, "source_agent", {})
            target = getattr(new_item, "target_agent", {})
            source_name = getattr(source, "name", "Unknown").replace("_", " ").title()
            target_name = getattr(target, "name", "Unknown").replace("_", " ").title()
            logger.info(f"🔄 Handoff: {source_name} → {target_name}")

        elif "ToolCall" in item_type and "Output" not in item_type:
            # Tool call logging
            tool_name = getattr(
                new_item, "tool_name", getattr(new_item, "name", "Unknown Tool")
            )
            display_name = agent_name.replace("_", " ").title()
            logger.info(f"🔧 {display_name}: Using tool '{tool_name}'")

        elif "ToolCall" in item_type and "Output" in item_type:
            # Tool output logging (shortened)
            output = getattr(new_item, "output", str(new_item))
            output_preview = (
                str(output)[:150] + "..." if len(str(output)) > 150 else str(output)
            )
            display_name = agent_name.replace("_", " ").title()
            logger.info(f"📄 {display_name}: Tool result: {output_preview}")

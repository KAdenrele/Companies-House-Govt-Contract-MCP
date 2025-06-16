import logging
import sys
import asyncio
import server.tools.mygemini as mygemini

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)

# Get a logger for this specific module
logger = logging.getLogger(__name__)


async def main():
    """Main asynchronous function to run the chatbot."""
    logger.info("Chatbot initialized. Type 'exit' to quit.")
    logger.info(f"MCP Server script path: {mygemini.MCP_SERVER_SCRIPT_PATH}")

    # Initialize the chat session from the mygemini module
    chat_session = mygemini.model.start_chat()

    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            logger.info("Input stream closed. Shutting down.")
            break

        if user_input.lower() == "exit":
            logger.info("Exit command received. Shutting down.")
            break

        try:
            # Use the asynchronous version for sending messages in an async context
            gemini_response = await asyncio.to_thread(chat_session.send_message, user_input)
            
            # Pass the chat_session and response to the handler in the other module
            await mygemini.handle_gemini_response_async(chat_session, gemini_response)

        except Exception as e:
            # Use logging.error to report exceptions. This captures the full traceback.
            # The 'exc_info=True' argument is crucial as it automatically adds exception info.
            logger.error(f"An error occurred during chat interaction: {e}", exc_info=True)
            logger.warning("Please ensure your Gemini API key is correct and the network is stable.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        logger.info("KeyboardInterrupt received. Exiting.")

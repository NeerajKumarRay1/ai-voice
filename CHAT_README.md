# Enhanced Chat Module

## Overview

The Enhanced Chat Module provides a robust interface for interacting with OpenAI's GPT-4o model. It includes several improvements over the basic implementation:

- **Conversation History Management**: Maintains and persists conversation context between sessions
- **Exponential Backoff for Rate Limiting**: Automatically retries requests with increasing delays when rate limits are hit
- **Configuration Management**: Loads settings from a config file with sensible defaults
- **Improved Error Handling**: Comprehensive error handling with detailed logging
- **Session Management**: Supports multiple conversation sessions with unique identifiers

## Features

### Conversation History

- Maintains conversation context between messages
- Automatically manages context window size by trimming older messages
- Persists conversations to disk for resuming later
- Supports clearing history while preserving system prompts

### Rate Limiting

- Implements exponential backoff for rate limit errors
- Configurable retry parameters (max retries, initial backoff, multiplier)
- Detailed logging of retry attempts

### Configuration

- Loads settings from `config.json` if available
- Provides sensible defaults for all parameters
- Supports environment variables for API keys

### Error Handling

- Comprehensive error handling for API errors, rate limits, and unexpected exceptions
- Structured logging with file and line information
- User-friendly error messages

## Usage

### Direct Function Call

```python
from chat_enhanced import get_bot_response

# Make sure OPENAI_API_KEY is set in environment variables
response = get_bot_response("What types of insurance do you offer?")
print(response)
```

### With Conversation History

```python
from chat_enhanced import get_bot_response, ConversationManager

# Create a conversation manager with a session ID
conversation = ConversationManager("user123")

# First message
response1 = get_bot_response("What types of insurance do you offer?", 
                           session_id="user123", 
                           conversation=conversation)

# Follow-up question (will maintain context)
response2 = get_bot_response("Which one is cheapest?", 
                           session_id="user123", 
                           conversation=conversation)
```

### Class-Based Interface

```python
from chat_enhanced import ChatEngine

config = {
    'openai_model': 'gpt-4o',
    'temperature': 0.7,
    'assistant_name': 'Insurance Assistant',
    'session_id': 'user123'
}

chat = ChatEngine(config)

# First message
response1 = chat.process("How do I file a claim?")

# Follow-up (maintains context)
response2 = chat.process("What documents do I need?")

# Clear conversation history
chat.clear_conversation()

# Clean up when done
chat.cleanup()
```

## Configuration

Create a `config.json` file in the project root with the following structure:

```json
{
  "openai": {
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 500,
    "system_prompt": "You are an insurance support assistant..."
  },
  "rate_limiting": {
    "max_retries": 5,
    "initial_backoff": 1,
    "backoff_multiplier": 2,
    "max_backoff": 60
  },
  "conversation": {
    "max_history": 10,
    "save_history": true
  }
}
```

## Testing

Use the included test script to try out the enhanced chat module:

```bash
python test_chat_enhanced.py --api-key YOUR_API_KEY
```

Options:
- `--api-key`: Your OpenAI API key (if not set in environment)
- `--class-mode`: Use ChatEngine class instead of direct function
- `--session`: Session ID for conversation history (default: random UUID)
- `--no-history`: Disable conversation history saving

## Future Enhancements

- Complete the RAG integration with FAISS
- Add streaming responses
- Implement token counting for better context management
- Add support for function calling
- Add support for multiple LLM providers
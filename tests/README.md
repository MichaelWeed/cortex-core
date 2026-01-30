# Cortex Core Tests

This directory contains the test infrastructure for the Cortex Core tool catalog.

## Usage

The test runner checks for the existence of tool implementations and optionally uses a local Ollama instance to validate prompt-to-argument generation.

### Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- (Optional) [Ollama](https://ollama.ai) running locally for AI validation

### Running Tests

Run all test suites:
```bash
python3 runner.py
```

Run a specific suite:
```bash
python3 runner.py --suite file_operations
```

### Suites

Test cases are defined in `suites.json`. Each suite groups related tools:
- **file_operations**: File I/O, editing
- **system**: Shell, Calculator, Python REPL
- **web**: Search, Browser, HTTP
- **integration**: AWS, Slack, Memory
- **advanced**: Batching, MCP, Threading

### Configuration

The runner automatically detects available models in your local Ollama instance (preferring Llama 3, Mistral, etc.). If no model is found, it runs in deterministic mode, verifying only the tool definitions and paths.




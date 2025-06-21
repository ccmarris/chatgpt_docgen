# GenAI DocGen

## Overview

**GenAI DocGen** is a Python tool that automates sending multiple prompts to 
an API driven GenAI system, for example, OpenAI's ChatGPT, and generate a 
Microsoft Word document (or other formats) containing the responses. This is 
useful for batch content generation, documentation, research, or summarization 
tasks.

## Features

- Send a customizable list of prompts to a Gen AI system 
- Configure model parameters such as `temperature`, `top_p`, `frequency_penalty`, and `presence_penalty`
- Save all prompt-response pairs in a formatted Word document (`.docx`), Markdown (`.md`), plain text (`.txt`), or print to stdout
- Command-line interface for easy automation and integration
- Progress bar for prompt processing
- Graceful handling of interruptions (partial results are saved)
- Flexible prompt source: use a file, structured data, or modify the built-in
  list (`prompts.py`)
- Supports loading API key and defaults from an ini file or environment
  variables
- Optionally output only responses (no prompts)
- Optionally include a document title
- (Reserved) Option to generate a table of contents
- **Prompt/response caching:** Avoids duplicate API calls and allows cache
  cleaning (older than 28 days)
- **Cache management:** Easily clean cache entries older than a set number of
  days
- **Token usage reporting:** See how many tokens each call used (OpenAI and
  Anthropic)
- **Extensible:** Add new providers or output formats with minimal changes

## Requirements

- Python 3.8+
- [openai](https://pypi.org/project/openai/)
- [anthropic](https://pypi.org/project/anthropic/)
- [python-docx](https://python-docx.readthedocs.io/en/latest/)
- [python-dotenv](https://pypi.org/project/python-dotenv/) (optional, for API
  key management)
- [tqdm](https://pypi.org/project/tqdm/) (for progress bar)
- [rich](https://pypi.org/project/rich/) (for colored output)
- [platformdirs](https://pypi.org/project/platformdirs/) (for cache location
  management)

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

1. **Set your API key(s)**  
   Export your API key as an environment variable or use a `.env` file:
   ```bash
   export OPENAI_API_KEY=sk-...
   export ANTHROPIC_API_KEY=your-anthropic-key
   ```

   Alternatively, use an ini file to store your API key and other defaults
   using the template `ai.ini` example.

     ```ini
   [CHATGPT]
   api_key = "<your_api_key_here>"
   model = "gpt-3.5-turbo"
   # Default parameters for the OpenAI API
   # temperature=1.0
   # top_p=1.0
   # frequency_penalty=0.0
   # presence_penalty=0.0

   [CLAUDE]
   api_key = "<your_api_key_here>"
   model = "claude-3-5-haiku-latest"
   # Default parameters
   # temperature=1.0
   # top_p=0.7
```

2. **Edit your prompts**  
   - Modify `src/prompts.py` to set the list of prompts you want to send, **or**
   - Use the `--prompt-file` option to load prompts from a file (one per line),
     **or**
   - Use structured data and Jinja2 templates for dynamic prompt generation.

3. **Run the tool**  
   ```bash
   python src/main.py --output my_report.docx --output-format docx --temperature 0.7 --top_p 0.9
   ```

   **Command-line options:**
   - `--provider`: Select LLM provider (`openai`, `anthropic`, etc.)
   - `--output`, `-o`: Output filename (default: `output.docx`)
   - `--output-format`, `-f`: Output format: `docx` (default), `txt`, `md`, or
     `stdout`
   - `--prompt-file`, `-p`: Path to a file containing prompts (one per line)
   - `--temperature`: Sampling temperature (default: 1.0)
   - `--top_p`: Nucleus sampling parameter (default: 1.0)
   - `--frequency_penalty`: Frequency penalty (default: 0.0, OpenAI only)
   - `--presence_penalty`: Presence penalty (default: 0.0, OpenAI only)
   - `--max_tokens`: Maximum tokens in the response (provider-specific)
   - `--sleep`, `-s`: Sleep time in seconds between requests (default: 1)
   - `--ini`, `-i`: Path to the ini file with API key and model settings
     (default: `ai.ini`)
   - `--debug`, `-d`: Enable debug logging
   - `--generate-title`: Include a document title in the output (default:
     enabled)
   - `--title`: Specify a custom document title
   - `--generate-as-prompts`: Output only responses (no prompts)
   - `--generate-toc`: (Reserved) Generate a table of contents

## Example

```bash
python src/main.py --provider anthropic --output summary.md \
--output-format md --prompt-file prompts.txt --temperature 0.7 \
--max_tokens 1024 --generate-title --title "AI Generated Report"
```

## Cache Management

- **Prompt/response caching** is enabled by default to avoid duplicate API
  calls.
- To clean the cache and remove entries older than 28 days, run:

  ```bash
  python -c "from response_cache import RESPONSECACHE; \
  RESPONSECACHE('prompt_cache_anthropic.json').clean(days=28)"
  ```

  *(Adjust the cache filename if you use a custom one or a different
  provider.)*

## Project Structure

```
genai_docgen/
├── src/
│   ├── main.py
│   ├── prompts.py
│   ├── genai_client.py
│   ├── response_cache.py
│   └── docgen.py
├── requirements.txt
├── README.md
```

## Default Model Parameters

The following are the default values (matching the ChatGPT and Claude web
interfaces):

- `temperature`: **1.0**
- `top_p`: **1.0**
- `frequency_penalty`: **0.0** (OpenAI only)
- `presence_penalty`: **0.0** (OpenAI only)

## License

BSD 2-Clause License

## Author

Chris Marrison

## Acknowledgements

Special thanks to **Steve Makousky** for assistance with testing and as a
sounding board for ideas.

---

*Feel free to contribute or open issues for feature requests!*


# ChatGPT DocGen

## Overview

**ChatGPT DocGen** is a Python tool that automates sending multiple prompts to OpenAI's ChatGPT and generates a Microsoft Word document (or other formats) containing the responses. This is useful for batch content generation, documentation, research, or summarization tasks.

## Features

- Send a customizable list of prompts to ChatGPT (via the OpenAI API)
- Configure model parameters such as `temperature`, `top_p`, `frequency_penalty`, and `presence_penalty`
- Save all prompt-response pairs in a formatted Word document (`.docx`), Markdown (`.md`), plain text (`.txt`), or print to stdout
- Command-line interface for easy automation and integration
- Progress bar for prompt processing
- Graceful handling of interruptions (partial results are saved)
- Flexible prompt source: use a file or modify the built-in list (`prompts.py`)

## Requirements

- Python 3.8+
- [openai](https://pypi.org/project/openai/)
- [python-docx](https://python-docx.readthedocs.io/en/latest/)
- [python-dotenv](https://pypi.org/project/python-dotenv/) (optional, for API key management)
- [tqdm](https://pypi.org/project/tqdm/) (for progress bar)
- [rich](https://pypi.org/project/rich/) (for colored output)

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

1. **Set your OpenAI API key**  
   Export your API key as an environment variable or use a `.env` file:
   ```bash
   export OPENAI_API_KEY=sk-...
   ```

   Alternatively use an inifile to store your API key and other defaults using
   the template `ai.ini` example.

2. **Edit your prompts**  
   - Modify `src/prompts.py` to set the list of prompts you want to send, **or**
   - Use the `--prompt-file` option to load prompts from a file (one per line).

3. **Run the tool**  
   ```bash
   python src/main.py --output my_report.docx --output-format docx --temperature 0.7 --top_p 0.9
   ```

   **Command-line options:**
   - `--output`, `-o`: Output filename (default: `output.docx`)
   - `--output-format`, `-f`: Output format: `docx` (default), `txt`, `md`, or `stdout`
   - `--prompt-file`, `-p`: Path to a file containing prompts (one per line)
   - `--temperature`: Sampling temperature (default: 1.0)
   - `--top_p`: Nucleus sampling parameter (default: 1.0)
   - `--frequency_penalty`: Frequency penalty (default: 0.0)
   - `--presence_penalty`: Presence penalty (default: 0.0)
   - `--sleep`, `-s`: Sleep time in seconds between requests (default: 1)
   - `--ini`, `-i`: Path to the ini file with API key and model settings (default: `ai.ini`)
   - `--debug`, `-d`: Enable debug logging

## Example

```bash
python src/main.py --output summary.md --output-format md --prompt-file prompts.txt --temperature 0.7
```

## Project Structure

```
chatgpt_wordgen/
├── src/
│   ├── main.py
│   ├── prompts.py
│   ├── chatgpt_client.py
│   └── docgen.py
├── requirements.txt
├── README.md
```

## Default Model Parameters

The following are the default values (matching the ChatGPT web interface):

- `temperature`: **1.0**
- `top_p`: **1.0**
- `frequency_penalty`: **0.0**
- `presence_penalty`: **0.0**

## License

BSD 2-Clause License

## Author

Chris Marrison

## Acknowledgements

Special thanks to **Steve Makousky** for assistance with testing.

---

*Feel free to contribute or open issues for feature requests!*


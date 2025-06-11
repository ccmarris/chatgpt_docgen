# ChatGPT WordGen

## Overview

**ChatGPT WordGen** is a Python tool that automates sending multiple prompts to OpenAI's ChatGPT and generates a Microsoft Word document containing the responses. This is useful for batch content generation, documentation, research, or summarization tasks.

## Features

- Send a customizable list of prompts to ChatGPT (via the OpenAI API)
- Configure model parameters such as temperature, top_p, frequency_penalty, and presence_penalty
- Save all prompt-response pairs in a formatted Word document (`.docx`)
- Command-line interface for easy automation and integration

## Requirements

- Python 3.8+
- [openai](https://pypi.org/project/openai/)
- [python-docx](https://python-docx.readthedocs.io/en/latest/)
- [python-dotenv](https://pypi.org/project/python-dotenv/) (optional, for API key management)

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

2. **Edit your prompts**  
   Modify `src/prompts.py` to set the list of prompts you want to send.

3. **Run the tool**  
   ```bash
   python src/main.py --output my_report.docx --temperature 0.7 --top_p 0.9
   ```

   **Command-line options:**
   - `--output`: Output Word document filename (default: `output.docx`)
   - `--temperature`: Sampling temperature (default: 1.0)
   - `--top_p`: Nucleus sampling parameter (default: 1.0)
   - `--frequency_penalty`: Frequency penalty (default: 0.0)
   - `--presence_penalty`: Presence penalty (default: 0.0)

## Example

```bash
python src/main.py --output summary.docx --temperature 0.7
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

## License

BSD 2-Clause License

## Author

Chris Marrison:wq

---

*Feel free to contribute or open issues for feature requests!*


import docx

def save_responses_to_docx(prompt_response_pairs, filename="output.docx"):
    doc = docx.Document()
    for prompt, response in prompt_response_pairs:
        doc.add_heading(prompt, level=2)
        doc.add_paragraph(response)
    doc.save(filename)
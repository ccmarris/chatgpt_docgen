#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script to generate responses from ChatGPT for a set of prompts and save them to a Word document.
"""

import logging
import argparse
import chatgpt_client
import time
from prompts import PROMPTS
from docgen import save_responses_to_docx
from rich import print

_logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ini", 
                        type=str, 
                        default="ai.ini", 
                        help="Path to the ini file with API key and model settings",
                        required= False)
    parser.add_argument(
        "--sleep",
        type=int,
        default=10,
        help="Sleep time in seconds between requests to avoid hitting rate limits (default: 2 seconds)"
    )
    # Add arguments for custom weightings
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top_p", type=float, default=1.0)
    parser.add_argument("--frequency_penalty", type=float, default=0.0)
    parser.add_argument("--presence_penalty", type=float, default=0.0)
    parser.add_argument(
        "--output",
        type=str,
        default="output.docx",
        help="Output Word document filename (default: output.docx)",
    )
    args = parser.parse_args()
    return args


def main():
    # Example: custom weightings
    success = True
    temperature = 0.7
    top_p = 0.9
    frequency_penalty = 0.2
    presence_penalty = 0.1
    args = parse_args()
    if args.temperature is not None:
        temperature = args.temperature
    if args.top_p is not None:
        top_p = args.top_p
    if args.frequency_penalty is not None:
        frequency_penalty = args.frequency_penalty
    if args.presence_penalty is not None:
        presence_penalty = args.presence_penalty
    _logger.info(
        f"Using parameters: temperature={temperature}, top_p={top_p}, frequency_penalty={frequency_penalty}, presence_penalty={presence_penalty}"
    )

    # Initialize ChatGPT client
    client = chatgpt_client.ChatGPTClient(inifile=args.ini)

    # Generate responses for each prompt
    prompt_response_pairs = []
    for prompt in PROMPTS:
        _logger.info(f"Sending prompt: {prompt}")
        response = client.get_response(
            prompt,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        if response == 'Success':
            #_logger.debug(f"Response: {client.last_response}")
            prompt_response_pairs.append((prompt, client.last_response))
            time.sleep(args.sleep)  # Sleep to avoid hitting rate limits
        else:
            _logger.error(f"Error generating response for prompt: {prompt}")
            _logger.error(f"Exiting due to error: {response}")
            print(f"[red]Error generating response for prompt: {prompt}[/red]")
            print(f"[red]Exiting due to error:[/red] {response}")
            success = False
            break

    if success: # Save responses to a Word document
        _logger.info(f"Saving responses to {args.output}")
        save_responses_to_docx(prompt_response_pairs, filename=args.output)
    
    return

if __name__ == "__main__":
    main()
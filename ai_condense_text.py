import aiohttp
import asyncio
import re
import logging
import os
from typing import List
from dotenv import load_dotenv
import aiofiles

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get OpenRouter API key from .env
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("Please set the OPENROUTER_API_KEY in your .env file")

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def split_into_chunks(text: str, max_chunk_size: int = 4000) -> List[str]:
    chunks = []
    current_chunk = ""
    for sentence in re.split(r'(?<=[.!?])\s+', text):
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

async def summarize_chunk(chunk: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://your-site.com",  # Replace with your actual site
        "X-Title": "AI Text Condenser"
    }
    
    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an AI assistant specializing in condensing technical documentation. Your task is to create a highly condensed summary of the given text, focusing exclusively on actionable information, key concepts, and technical details. Follow these guidelines:\n\n1. Prioritize steps, procedures, and technical specifications.\n2. Omit all general descriptions, introductions, and non-essential context.\n3. Exclude changelogs, privacy information, and security details unless they directly impact usage.\n4. Use extremely concise language, avoiding full sentences where possible.\n5. Employ technical abbreviations and shorthand freely.\n6. Retain precise technical terms, commands, and code snippets.\n7. Structure output in a way that's easily parseable by other AI systems, not necessarily human-readable.\n8. If the input contains multiple topics, separate them clearly but minimally.\n\nYour goal is to produce the most information-dense, action-oriented summary possible."},
            {"role": "user", "content": chunk}
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENROUTER_API_URL, json=data, headers=headers) as response:
                response.raise_for_status()
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()
    except aiohttp.ClientError as e:
        logging.error(f"An error occurred while calling the OpenRouter API: {e}")
        return chunk  # Return the original chunk if summarization fails

async def condense_text(input_file: str, output_file: str) -> None:
    try:
        async with aiofiles.open(input_file, 'r', encoding='utf-8') as infile:
            content = await infile.read()
        
        # Extract code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        
        # Remove code blocks from content
        content = re.sub(r'```[\s\S]*?```', '', content)
        
        # Split content into chunks
        chunks = split_into_chunks(content)
        
        # Summarize chunks concurrently
        tasks = [summarize_chunk(chunk) for chunk in chunks]
        summarized_chunks = await asyncio.gather(*tasks)
        
        # Write summarized content
        async with aiofiles.open(output_file, 'w', encoding='utf-8') as outfile:
            await outfile.write("\n\n".join(summarized_chunks))
            
            # Write code blocks (limit to 5 for brevity)
            await outfile.write("\n\n" + "\n\n".join(code_blocks[:5]))
        
        logging.info(f"Text condensed successfully. Output written to {output_file}")
    except Exception as e:
        logging.error(f"An error occurred during text condensation: {e}")

# Remove the main function as it's not needed in this context
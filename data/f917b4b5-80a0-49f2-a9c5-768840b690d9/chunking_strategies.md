# Chunking Strategies for LLM Applications

## Introduction
Chunking is the process of breaking down large documents into smaller, semantically coherent segments before generating vector embeddings.

## Strategies
- **Fixed-size Chunking**: Divides text by a fixed character or token count with sliding overlap windows.
- **Recursive Character Splitting**: Respects structural boundaries such as paragraphs (`\n\n`), newlines (`\n`), sentences, and spaces.
- **Document-Structure Aware**: Segments markdown documents based on header hierarchies (`#`, `##`, `###`).
- **Semantic Chunking**: Computes embedding distances between sentences and splits where semantic similarity drops significantly.

## Recommended Parameters
- Tokenizer: `cl100k_base` (tiktoken)
- Default Chunk Size: 500 tokens
- Chunk Overlap: 50 tokens (10% overlap to preserve cross-boundary context)

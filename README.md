# Codebase-Genius
Multi-Agent Repository Analyzer
This program is a multi-agent system implemented in Jaclang using Meaning-Typed Programming (MTP) and integrated with a Large Language Model (LLM). Its primary purpose is to analyze a GitHub repository and automatically generate a structured summary of its contents, structure, and purpose.

Agents:
1. Repo Mapper Agent – Clones the repo, applies ignore rules, and extracts the README outline and repository structure.
2. Code Parser Agent – Collects raw code from non-ignored files.
3. Doc Genie Agent – Generates a descriptive summary explaining the repository’s purpose, components, and functionality.
4. Supervisor Agent – Orchestrates all agents and aggregates their outputs, producing the final analysis including ignored files, README outline, structure, and summary.

MTP & LLM Integration:
The system leverages MTP’s language-level abstractions to integrate LLMs seamlessly. Core functions are declared using by llm() (e.g., cleanup_fn, readme_outline_fn, repo_structure_fn), allowing the compiler to automatically generate prompts from function signatures and rich docstrings. This eliminates manual prompt engineering, enabling the agents to behave intelligently and autonomously, interpreting repository contents, extracting structure, and producing human-readable documentation.
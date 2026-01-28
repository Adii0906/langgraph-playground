# AI Solver CLI

An intelligent command-line tool that solves programming errors and problems using LangGraph and AI.

## Overview
AI Solver is an agentic workflow built with **LangGraph** that analyzes programming errors and provides expert solutions. It leverages the Groq API (Qwen model) to power intelligent reasoning.

## Key Features
- **Error Analysis**: Input any programming error or problem
- **Agentic Workflow**: Multi-node graph (user input → solver → tools → output)
- **Tool Integration**: Documentation search tools for enhanced solutions
- **Enhanced UI**: Colored output with typing animations and thinking spinner
- **Tool Calling**: Supports dynamic tool invocation based on solver decisions

## Architecture
- **State Management**: TypedDict-based state with message history
- **Graph Flow**: START → user_input → solver ⇄ tools → output → END
- **LLM**: ChatGroq with tool binding for intelligent reasoning
- **Nodes**: User input processor, LLM solver, tool executor, output formatter

## Usage
```bash
python main.py
# Paste your error/problem when prompted
```

The system will analyze your problem and provide solutions with a formatted conversation log.

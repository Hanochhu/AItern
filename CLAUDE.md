# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

- **Install dependencies**: `pip install -r requirements.txt`
- **Run tests**: `pytest tests/`
- **Run a single test**: `pytest tests/test_example.py::test_function_to_implement`
- **Start AI exploration**: `aitern . explore`
- **List exploration history**: `aitern . list`
- **Apply exploration result**: `aitern . apply <exploration_id>`

## Code Architecture

- **Core modules**: Located in `src/core/`, handling the main logic of the tool.
- **AI agents**: Implemented in `src/agents/`, responsible for generating and modifying code.
- **Utilities**: Found in `src/utils/`, providing helper functions.
- **Configuration**: Managed in `src/config/`, including AI model settings and exploration parameters.
- **Tests**: Stored in `tests/`, following pytest conventions.

## Workflow

1. **Test-driven**: Write tests first, then use `aitern . explore` to generate implementations.
2. **Branch-based**: Each exploration creates a new git branch.
3. **Iterative**: AI modifies code until tests pass or max iterations are reached.
4. **Merge-ready**: Successful explorations can be applied to the main branch.

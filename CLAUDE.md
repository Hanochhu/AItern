# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Install dependencies**: `pip install -r requirements.txt`
- **Run tests**: `pytest tests/`
- **Run a single test**: `pytest tests/test_example.py::test_function_to_implement`
- **Start AItern exploration**: `aitern . explore`
- **List exploration history**: `aitern . list`
- **Apply exploration results**: `aitern . apply <exploration_id>`

## Architecture

- **Core modules**: `src/core/` contains the main logic for AItern's TDD workflow.
- **AI agents**: `src/agents/` implements different AI-driven exploration strategies.
- **Configuration**: `src/config/` handles project and AI model settings.
- **Tests**: `tests/` contains test cases for TDD.
- **Explorations**: `.aitern/explorations/` stores AI-generated code exploration records.

## Workflow

1. Write tests in `tests/`.
2. Run `aitern . explore` to start AI-driven code exploration.
3. AI generates/modifies code in a new branch until tests pass.
4. Apply successful explorations with `aitern . apply`.
# Project Guide

This project follows a strict set of rules for development. Rules for the overall architecture and file structure, testing guidelines, and the integrators/units sections below, must be followed at all times.

## Purpose and Usage

Please refer to README.md at the project root for details about the purpose of this project, how it is organized and configured, and for usage examples.

## Commands

Set up to run as a module:

```bash
uv pip install -e .
```

Run tests:

```bash
uv run python -m pytest
```

## System Architecture

This project follows a strict "hexagonal" architecture. Other names for this architectural style include "functional core, imperative shell" and "ports and adapters."

The codebase is organized into a set of subpackages. Each subpackage is an independent unit, often with a clear/independent API, complete with types, usage guidelines, and documentation. Circular dependencies between subpackages are strictly forbidden!

Each subpackage keeps an internally strict separation between functions and data.

The data (data structures, dataclasses, Pydantic models, and types) are kept in a data folder.

The functions (often "pure" functions, wherever possible) are kept in the functions folder.

We maintain a strict 1:1 correspondence between:
1. functions and files: one function per file (in the functions folder).
2. data and files: one data structure per file (in the data folder).
3. files and tests: one file, one test suite.

At the same level as the functions and data folders, there may also exist:

- Traditional classes, if they are not "pure" and/or are not easily expressed as functions (this is VERY rare).
- Protocols (see `src/electric_text/providers/model_provider.py`).
- Subpackages, which themselves have the same data and functions structure as the subpackage they are in.


### Dependencies

Run the following command to visualize the dependency graph:

```bash
uv run pydeps src/electric_text --max-module-depth=2 --rankdir RL --rmprefix electric_text.
```

There should be no blue boxes in the above graph (blue boxes and two-way arrows indicate circular dependencies).

The following dependencies are allowed:

#### `__main__.py` depends on:
- `cli` (calls the `main` function, returns an exit code).

#### `cli` depends on:
- `shorthand`
- `prompting` (in: `SystemInput`, out: `None` (prints content)).

#### `prompting` depends on:
- `tools`
- `formatting` (for output formatting functions)
- `clients` (in: `ClientRequest`, out: `ClientResponse`)

#### `clients` depends on:
- `providers` (in: `ProviderRequest`, out: `StreamHistory`)

#### `providers` depends on nothing.

#### `tools` depends on nothing.

#### `shorthand` depends on nothing.

#### `formatting` depends on nothing.

## Testing

Testing is critical in this project and often informs how subsystems are designed.

Well-designed components produce tests that are easy to read, write, and run.

We use our tests as a way of evaluating the quality of our design.

We follow a strict and focused test-first approach, always discussing WHAT behavior to test before determining HOW to test it.

We almost never use test classes; usually functions are simple and sufficiently "unit-like" that a flat list of pytest tests in a file will suffice.

Tests are written before implementation with declarative assertion documentation:
- BAD test docstring: "Tests that env is loaded in non-containerized environment"
- GOOD test docstring: "Loads env in non-containerized environment"

Additional general testing rules:

- Fixtures are ALWAYS centralized and shared in tests/fixtures.py. No exceptions!
- Tests focus on input/output pairs for our functional codebase.
- Single pytest assertion per test where possible.
- Never write code until tests have been written.
- Never `patch` code! Integration tests *fully* run *all* user code.

## "Integrators" and "Units"

All subpackages contain functions that are one of two types:
1. **Units**: Simple components with pure functions (input -> output)
2. **Integrators**: Components with dependencies on other functions, and/or effectful behavior

Integration tests may contain multiple assertions since integrators often call several units and compose their results into some data structure, which is returned.

We avoid combinatorial explosion (2^n paths for n branches) through careful design that makes invalid states unrepresentable and maintains a clear separation between integrators and units.

Notes on units:
- Simple data types in and out.
- Pure functions, no imports, no dependencies, no side effects.
- Tested simply: all possible return values are covered in unit-like assertions.

Notes on integrators:
- Calls other units and/or integrators.
- Sole purpose is to assemble complex return types and data structures via delegated unit/integrator calls.
- Never makes semantically meaningful decisions: always delegates to other integrators/units.
- Can use if/else but ONLY to conditionally (i.e. early) return its return type.
- Simple integration tests: one test function/suite-of-functions for each `return` inside integrator body.
- Size of test suite is proportional to variety of return conditions.
- Never mocks or stubs user code, always runs code that it depends on.

## Workflows

"Simple things should be simple, complex things should be possible." — Alan Kay

Code changes in this project should typically start at the end-user's request, and cascade "all the way down" to the lower levels of, for example, a provider API call, making architectural and code changes as necessary along that path through the layers of abstraction. The reasoning behind this order of operations follows from the ultimate aim of this software: ease of use and power of expression. If we decide to add a feature or extend certain behavior of the system, we should first focus on how that specific behavior is *expressed* by the user of the software. How do _they_ see the world, how do they express the outcome they desire, and how then can our system most naturally model their intent? Always start with the user!

### "Follow the Data"

We model the world in the following sequence, getting less general/abstract and more granular/detailed as we go:

```
User request → SystemInput → ClientRequest/ClientResponse → ProviderRequest → StreamHistory
```

## Style

We follow a strictly functional programming style:
1. Prefer functions and composition over classes and inheritance.
2. Functions are almost always pure and have no side effects.
3. Functions follow SRP and are small/focused.
4. Functions always have clear input and output types.
5. Functions never mutate their arguments.

There are a few other general rules for how we write code:
1. Always use `dedent` for multi-line strings.

## Progress

Some code predates these rules and is not yet in compliance. Before making changes to existing functionality, please review the code and determine if it is in compliance with the rules. If it is not in compliance, please highlight the code in question and ask for guidance as to whether it should be changed before proceeding.
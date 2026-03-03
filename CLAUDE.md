# CLAUDE.md — DisCoPy Codebase Guide

## Project Overview

**DisCoPy** is a Python toolkit for computing with [string diagrams](https://en.wikipedia.org/wiki/String_diagram). It implements monoidal categories and their hierarchy for compositional semantics, quantum computing, and formal grammar. Version: `1.0.0`.

- **Docs:** https://discopy.readthedocs.io
- **Paper (category theory):** https://doi.org/10.4204/EPTCS.333.13
- **Paper (quantum):** https://arxiv.org/abs/2205.05190

---

## Repository Layout

```
discopy/            # Main source package
  cat.py            # Foundation: free dagger category (Ob, Arrow, Box, Functor)
  monoidal.py       # Planar string diagrams (Ty, Diagram, Box, Functor)
  braided.py        # Braided monoidal categories (swap boxes)
  balanced.py       # Balanced (braided + twists)
  symmetric.py      # Symmetric monoidal categories
  cartesian.py      # Cartesian (copy/discard)
  traced.py         # Traced monoidal categories
  closed.py         # Closed monoidal (exponential types)
  rigid.py          # Rigid categories (cups, caps, adjoints)
  pivotal.py        # Pivotal categories (dimension function)
  ribbon.py         # Ribbon categories (framed links)
  compact.py        # Compact closed categories
  frobenius.py      # Frobenius algebras and spiders
  hypergraph.py     # Hypergraph diagram rewriting
  python.py         # Evaluation: Python function semantics
  matrix.py         # Evaluation: matrix/linear algebra
  tensor.py         # Evaluation: tensor networks (NumPy/PyTorch/TF/JAX)
  drawing/          # Visualization (NetworkX/Matplotlib and HTML5)
  grammar/          # Formal grammars (thue, cfg, categorial, pregroup, dependency)
  quantum/          # Quantum computing (circuits, ZX calculus, tket, PennyLane)
  utils.py          # Shared utilities
  config.py         # Configuration (backends, thresholds)
  messages.py       # Error messages and warnings

test/               # Test suite (mirrors source layout)
  syntax/           # Tests for categorical structure modules
  semantics/        # Tests for evaluation modules (python, tensor, matrix)
  drawing/          # Tests for visualization
  grammar/          # Tests for grammar modules
  quantum/          # Tests for quantum modules
  requirements.txt  # Test-only dependencies

docs/               # Sphinx documentation source
notebooks/          # Jupyter notebook examples
setup.py            # Package setup (reads version from discopy/__init__.py)
setup.cfg           # pytest and pycodestyle configuration
requirements.txt    # Runtime dependencies
```

---

## Module Dependency Hierarchy

Dependencies flow **downward** (bottom modules are more foundational). Forgetful functors go upward.

```
cat  (foundation)
 └─ monoidal  (planar diagrams)
     ├─ braided
     │   ├─ balanced
     │   ├─ symmetric
     │   │   └─ cartesian
     │   └─ closed
     │       └─ rigid
     │           ├─ pivotal
     │           ├─ ribbon
     │           ├─ compact
     │           └─ frobenius
     └─ hypergraph  (rewriting)
```

`drawing`, `python`, `matrix`, `tensor`, `grammar`, and `quantum` are consumers that depend on the categorical core but are not depended upon by it.

---

## Development Workflow

### Installation

```bash
git clone https://github.com/discopy/discopy.git
cd discopy
pip install .
```

### Running Tests

```bash
pip install ".[test]" .
coverage run -m pytest --doctest-modules --pycodestyle
coverage report -m discopy/*.py discopy/*/*.py
```

The full test command used in CI:

```bash
coverage run --source=discopy -m pytest discopy test --doctest-modules
coverage report --fail-under=100 --show-missing
```

### Building Documentation

```bash
pip install ".[docs]" .
sphinx-build docs docs/_build/html
```

---

## CI/CD

GitHub Actions (`.github/workflows/build_test.yml`) runs on every push and pull request:

1. **Lint job** — runs `pycodestyle discopy` on Python 3.9 and 3.10
2. **Build & Test job** (requires lint to pass) — installs the package, runs pytest with doctests, enforces **100% code coverage**

Both jobs run against Python **3.9** and **3.10**.

---

## Code Conventions

### File Header

Every source file starts with:

```python
# -*- coding: utf-8 -*-
```

And uses:

```python
from __future__ import annotations
```

### Naming

| Kind | Convention | Example |
|------|-----------|---------|
| Classes | `PascalCase` | `Diagram`, `Functor`, `AxiomError` |
| Functions / methods | `snake_case` | `is_composable`, `from_tree`, `to_tree` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_BACKEND`, `NUMPY_THRESHOLD` |
| Single-char vars | Allowed (exempted) | `x`, `y`, `f`, `g` |
| Lambda assignments | Allowed (exempted) | `E731` waived |

### Pycodestyle Exemptions (setup.cfg)

```
E731  # lambda assignments (do not assign a lambda expression)
E741  # ambiguous variable names (l, O, I)
E743  # ambiguous function names
W503  # line break before binary operator
```

### Docstring Style

Modules and classes use **reStructuredText** with Sphinx `autosummary` tables. Docstrings contain embedded **doctests** that are executed as part of the test suite. Keep doctest examples concise and illustrative.

Example module docstring pattern:

```python
"""
The free (dagger) category ...

Summary
-------

.. autosummary::
    :template: class.rst
    :nosignatures:
    :toctree:

    Ob
    Arrow
    Box

Axioms
------

>>> x, y = Ob('x'), Ob('y')
>>> f = Box('f', x, y)
>>> assert f[::-1][::-1] == f
"""
```

### Design Patterns

**`@factory` decorator** — Used to enable flexible class instantiation where inner objects can be passed as raw values and automatically wrapped:

```python
@factory
class Ty(cat.Ob):
    ob_factory = cat.Ob
```

**Inheritance mixins** — Classes often inherit from both a categorical structure class and a `Diagram` base:

```python
class Box(monoidal.Box, Diagram): ...
```

**Abstract base classes** — Use `ABC` and `@abstractmethod` for interfaces:

```python
from abc import ABC, abstractmethod

class Composable(ABC):
    @abstractmethod
    def then(self, *others): ...
```

**Type assertions** — Use helper functions rather than bare `assert` for domain/codomain validation:

```python
assert_isinstance(other, Arrow)
assert_iscomposable(self, other)
```

**Operators** — Composition uses `>>` (left-to-right) and `<<` (right-to-left); monoidal tensor uses `@`:

```python
arrow = f >> g >> h          # sequential composition
diagram = f @ g              # monoidal tensor
```

**Dagger** — Accessed via `[::-1]` slice syntax:

```python
f_dagger = f[::-1]
```

### Testing Requirements

- **100% code coverage** is mandatory — every line of `discopy/` must be exercised.
- Tests live in `test/<subdirectory>/` and mirror source layout.
- Doctests embedded in source files are executed as part of the test suite (`--doctest-modules`).
- `test/drawing/legacy.py` is excluded from the default test run (`--ignore`).
- `python_files = test/*/*.py` — only files in subdirectories are collected automatically.

---

## Key Abstractions

### `cat.py` — The Foundation

- **`Ob`** — Objects in a category
- **`Arrow`** — Morphisms (lists of `Box`es) between `Ob`s
- **`Box`** — Atomic morphism with a name, domain, and codomain
- **`Id`** — Identity arrow on an object
- **`Functor`** — Structure-preserving map between categories
- **`Sum`** — Formal linear combination of arrows (for enriched categories)
- **`Bubble`** — Unary operator applied to an arrow

### `monoidal.py` — String Diagrams

- **`Ty`** — Monoidal type (sequence of `Ob`, monoid under `@`)
- **`Diagram`** — String diagram: list of `Layer`s
- **`Layer`** — A box with left/right context wires
- **`Box`** — Monoidal box (extends `cat.Box`)
- **`Functor`** — Monoidal functor (extends `cat.Functor`)

### `rigid.py` — Adjoints

- **`Ty`** — Rigid type with `.l` (left adjoint) and `.r` (right adjoint)
- **`Cup`** / **`Cap`** — Counit / unit of the adjunction
- Snake equation: `Cap >> (Id @ Cup) == Id` (up to interchanger)

### `tensor.py` — Tensor Evaluation

- Evaluates diagrams as tensor networks
- Backend-agnostic: works with NumPy, PyTorch, TensorFlow, JAX
- Backend controlled via `discopy.config`

### `quantum/` — Quantum Computing

- `circuit.py` — Quantum circuits as monoidal diagrams
- `gates.py` — Standard quantum gates (H, CX, Rz, etc.)
- `zx.py` — ZX calculus (interfaces with PyZX)
- `tk.py` — tket integration for circuit compilation
- `pennylane.py` — PennyLane integration for auto-differentiation

### `grammar/` — Formal Grammars

- `pregroup.py` — Pregroup grammar (used in DisCoCat / QNLP)
- `cfg.py` — Context-free grammar
- `categorial.py` — Categorial grammar
- `dependency.py` — Dependency grammar
- `thue.py` — Thue rewriting systems

---

## Common Gotchas

1. **Doctests are tests** — All doctests in `discopy/*.py` run in CI. Broken doctests break the build.
2. **Coverage must be 100%** — Adding new code without tests will fail CI.
3. **Pycodestyle is enforced** — The lint job runs before tests; style errors block the build.
4. **`test/drawing/legacy.py` is ignored** — It is explicitly excluded from the default pytest run.
5. **Single-character variable names are intentional** — They reflect mathematical notation (objects `x, y, z`, morphisms `f, g, h`).
6. **`[::-1]` is the dagger** — This is an intentional overloading of Python's slice syntax, not a bug.
7. **`@` is monoidal tensor** — Not matrix multiplication; this is the monoidal product `⊗`.
8. **`>>` is sequential composition** — `f >> g` means "apply `f` then `g`" (left-to-right diagrammatic order).

---

## Dependencies

### Runtime (requirements.txt)

- `numpy >= 1.18.1`
- `networkx >= 2.4`
- `matplotlib >= 3.1.2`
- `pillow >= 6.2.1`

### Test (test/requirements.txt)

- `pytest`, `coverage`, `pycodestyle`
- `sympy==1.9` (symbolic variables)
- `pytket==1.1.0`, `pyzx>=0.7.0` (quantum backends)
- `tensorflow`, `tensornetwork`, `jax`, `jaxlib`, `torch` (tensor backends)
- `pennylane` (autodiff)
- `lxml`, `nltk` (grammar parsing)

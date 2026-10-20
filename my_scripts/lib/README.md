# my_scripts/lib

Your own reusable functions. Like the rest of `my_scripts/`, every `*.py` file in
here is git-ignored, so your library code stays on your machine. Only this README
is tracked, so the folder exists after a clone.

The shared, company-wide helpers live in the repo's top-level `lib/` (`lib.assemblies`,
`lib.colors`, ...). This folder is for yours.

## Do not add an `__init__.py`

This folder is deliberately **not** a Python package. NX puts a script's own folder
first on `sys.path`, so a `lib` package inside `my_scripts/` would **hide the shared
`lib/`** and break `from lib.assemblies import ...` in your scripts. Keep plain
modules here and import them by name, as below.

## Add a function

Create a module here, for example `lib/my_helpers.py`:

```python
def part_label(part):
    """Item id and revision of a part, e.g. '1150201-500/01'."""
    return part.Leaf
```

## Use it from a script in `my_scripts/`

Put this at the top of your script. It finds the repo root (for the shared `lib/`)
and adds this folder (for your modules):

```python
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))

def _setup_paths():
    d = _HERE
    for _ in range(6):                      # walk up to the folder holding lib/
        if os.path.isfile(os.path.join(d, "lib", "__init__.py")):
            sys.path.insert(0, d)           # shared lib:   from lib.assemblies import ...
            sys.path.insert(0, os.path.join(d, "my_scripts", "lib"))   # yours: import my_helpers
            return
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    raise RuntimeError("Could not find the repo root (folder containing lib/)")

_setup_paths()

import NXOpen
from lib.assemblies import walk_components     # shared
import my_helpers                              # yours
```

## Good to know

* **Name modules so they don't clash** with the shared ones or with standard library
  modules: avoid `assemblies`, `colors`, `teamcenter`, `os`, `csv`. Something like
  `my_helpers.py` or your initials as a prefix works.
* **NX keeps imported modules in memory for the session.** After editing a module here,
  restart NX (or reload it) before re-running, or you may still get the old code.
* **Something worth sharing?** Move it into the repo's top-level `lib/`, add it to a
  shared tool, and commit it there.

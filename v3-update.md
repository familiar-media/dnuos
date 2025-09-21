# 0) Quick goals

* Move to **PEP 517/518** build system with a **`pyproject.toml`**.
* Declare metadata via **PEP 621** (portable across tools).
* Keep setuptools as the backend (least risky), unless you explicitly want Hatch/Flit/Poetry.
* Preserve: package discovery, package data, entry points (console scripts/plugins), extras, `python_requires`, classifiers, versioning, C-extensions (if any), and sdist/wheel behavior.
* Remove `setup.py` only **after** you can build + install + run tests successfully.

---

# 1) Inventory what `setup.py` does

Open `setup.py` and copy out everything passed to `setup(...)`. You’ll map each of these:

* **Name / Version / Description / Long description** (often `README.*`)
* **License / Authors / URLs / Classifiers**
* **`packages` / `package_dir` / `py_modules`** or auto-discovery
* **`install_requires`**
* **`extras_require`**
* **`entry_points`** (e.g., `console_scripts`, plugin groups)
* **`include_package_data`, `package_data`, `exclude_package_data`**
* **`data_files`** (rare; try to stop using it)
* **`python_requires`**
* **`cmdclass`** or custom setup commands (replace if possible)
* **C/C++ extensions**: `ext_modules`, `libraries`, `include_dirs`, etc.
* **Namespace packages** (pkgutil/setuptools style) or implicit (PEP 420)

If you use **version-from-Git** or a dynamic version (`setuptools_scm`, reading a file, etc.), note it.

---

# 2) Choose your backend (recommend: setuptools)

Safest path (minimal behavior change):

* Keep **setuptools** as backend.
* Use **PEP 621** for metadata.
* Optional: use **setuptools-scm** for versioning from tags.

---

# 3) Create `pyproject.toml`

Add a minimal build system + tool config. Start with this skeleton and then fill in mappings (next section).

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]               # wheel for older pip
build-backend = "setuptools.build_meta"

[project]
name = "your-package-name"
version = "0.0.0"                                     # OR make it dynamic (see below)
description = "One-line summary"
readme = { file = "README.md", content-type = "text/markdown" }
requires-python = ">=3.9"                             # match your old python_requires
license = { text = "MIT" }                            # or {file="LICENSE"}
authors = [{ name = "Your Name", email = "you@example.com" }]
classifiers = [
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
]
dependencies = [
  # former install_requires
]

# Optional “pip install .[dev]”
[project.optional-dependencies]
dev = [
  # former extras_require["dev"]
]

# Former entry_points={"console_scripts": ["foo=mod:func"], "some.group": [...]}
[project.scripts]
# "foo" = "package.module:function"

[project.entry-points]
# some.group = { "name" = "package.plugin:factory" }

[tool.setuptools]
# Use either packages.find OR py-modules (if it’s a single-file module)

[tool.setuptools.packages.find]
where = ["src"]       # if you used a src layout; otherwise remove
include = ["*"]
exclude = []

[tool.setuptools.package-data]
# package = ["data/*.txt", "templates/*.html"]

[tool.setuptools.exclude-package-data]
# package = ["*.tmp"]

# If you used MANIFEST.in for sdist-only files, keep it; PEP 621 readme covers README.
# If you had C extensions:
# [tool.setuptools.ext_modules]
# name = { sources = ["src/package/_speedup.c"], include-dirs=["include"] }

# If you used dynamic versioning (setuptools-scm):
# [tool.setuptools_scm]
# version_scheme = "guess-next-dev"
# local_scheme = "node-and-date"

# And in [project]:
# dynamic = ["version"]
```

**Notes**

* `project.scripts` is a convenience for `console_scripts`. If you need **non-console** entry-point groups, put them under `[project.entry-points."group-name"]`.
* If you used `py_modules=["foo"]` instead of packages, omit `packages.find` and set:

  ```toml
  [tool.setuptools]
  py-modules = ["foo"]
  ```

---

# 4) Map `setup.py` fields → `pyproject.toml`

| `setup.py` arg                    | `pyproject.toml` (PEP 621 / setuptools)                                                 |
| --------------------------------- | --------------------------------------------------------------------------------------- |
| `name`                            | `[project] name`                                                                        |
| `version="x.y"`                   | `[project] version="x.y"` or `dynamic=["version"]` + setuptools-scm                     |
| `description`                     | `[project] description`                                                                 |
| `long_description` (+ type)       | `[project] readme = {file="README.md", content-type="text/markdown"}`                   |
| `author`, `author_email`          | `[project] authors = [{name="...", email="..."}]`                                       |
| `url`, `project_urls`             | `[project] urls = { Homepage="...", Docs="..." }`                                       |
| `classifiers`                     | `[project] classifiers = [...]`                                                         |
| `python_requires`                 | `[project] requires-python = ">=X.Y"`                                                   |
| `install_requires`                | `[project] dependencies = [...]`                                                        |
| `extras_require`                  | `[project] optional-dependencies = { extra = [...] }`                                   |
| `packages/find_packages`          | `[tool.setuptools.packages.find] ...`                                                   |
| `py_modules`                      | `[tool.setuptools] py-modules = ["m1","m2"]`                                            |
| `package_data`                    | `[tool.setuptools.package-data] package = ["globs"]`                                    |
| `include_package_data=True`       | Keep **and** use MANIFEST.in (for sdist) OR rely on `package-data` (for wheels).        |
| `exclude_package_data`            | `[tool.setuptools.exclude-package-data] package=["globs"]`                              |
| `data_files`                      | **Avoid**; prefer `package_data`. If must keep, see “Data files” below.                 |
| `entry_points["console_scripts"]` | `[project.scripts]`                                                                     |
| `entry_points[other]`             | `[project.entry-points."group"] name="pkg.module:func"`                                 |
| `cmdclass` / custom commands      | Replace with normal tools (tox/nox), or separate CLI tasks; avoid custom build hooks.   |
| `ext_modules`                     | `[tool.setuptools.ext_modules]` (one table per extension with `sources=[...]`)          |
| `namespace_packages`              | Prefer **PEP 420** (implicit namespaces). Otherwise keep old approach w/ `__init__.py`. |

---

# 5) Package discovery & layout

* **Current `packages`/`find_packages()`**: replicate with `[tool.setuptools.packages.find]`.
* **`src/` layout?** Keep it; it prevents accidental imports from working dir. Set `where = ["src"]` and ensure `packages` actually live in `src/`.
* **Implicit namespace packages (PEP 420)**: if you used these, **don’t** put `__init__.py` in namespace roots. Declare nothing special; setuptools will find them.

---

# 6) Package data vs MANIFEST.in

* **Wheel (runtime) files inside packages**: use `[tool.setuptools.package-data]` (preferred).
* **Source distribution extras** (e.g., examples, docs) that aren’t in a package dir:

  * Keep a small **`MANIFEST.in`** to include them in `sdist`.
  * README/LICENCE are typically included via PEP 621 and setuptools defaults; no custom code needed.
* If `include_package_data=True` was used together with `MANIFEST.in`, you can keep that pattern unchanged.

**Example `MANIFEST.in`** (only if you need sdist extras):

```
include LICENSE
recursive-include examples *.py
recursive-include docs *.md
```

---

# 7) Entry points (console scripts & plugins)

* **Console scripts**:

  ```toml
  [project.scripts]
  your-cli = "yourpkg.cli:main"
  ```
* **Other plugin groups** (e.g., `pytest11`, `myapp.hooks`):

  ```toml
  [project.entry-points."pytest11"]
  my_plugin = "yourpkg.plugins:Plugin"
  ```

---

# 8) Versioning

**If your `setup.py` read a version string from a module or file**, just set that value in `[project] version`.

**If you used Git tags / `setuptools_scm`:**

* Add to build requirements and mark version dynamic:

  ```toml
  [build-system]
  requires = ["setuptools>=69", "wheel", "setuptools-scm>=8"]

  [project]
  dynamic = ["version"]

  [tool.setuptools_scm]
  # optional tweaks
  ```
* Remove any manual version parsing code.

---

# 9) Data files (last resort)

`data_files` installs files into arbitrary system locations and is fragile. Prefer packaging data **inside your package** with `package_data` and load it via `importlib.resources`.
If you **must** keep `data_files`, setuptools still supports it via `setup.cfg`, but **PEP 621** has no native key. Two options:

* Keep a **tiny** `setup.cfg` just for `data_files` and keep `pyproject.toml` for everything else.
* Or move those assets inside your package and switch to `package-data`.

---

# 10) C extensions (if any)

Translate each `Extension(...)` into TOML:

```toml
[tool.setuptools.ext_modules."yourpkg._speed"]
sources = ["src/yourpkg/_speed.c"]
include-dirs = ["include"]
libraries = []
define-macros = []
```

If you had custom build logic in `setup.py`, try to replace with standard config (or a build step driven by `pyproject` plugins; avoid custom distutils commands).

---

# 11) Tests, builds, installs

Add (or keep) a **`requirements-dev.txt`** or `[project.optional-dependencies].dev` for test deps.

Then validate the flow:

```bash
# Clean
git clean -xdf

# Build sdist + wheel (uses pyproject)
python -m pip install --upgrade pip build
python -m build

# Install locally (editable)
python -m pip install -e .[dev]

# Run tests
pytest -q
```

If your CLI and plugin entry points work and tests pass, you’re good.

---

# 12) Remove `setup.py` (safely)

Once the above succeeds:

1. Commit `pyproject.toml` (and `MANIFEST.in` if you still need it).
2. Delete `setup.py`.
3. Re-run the build/install/tests (as above) to ensure nothing still referenced `setup.py`.

---

# 13) Common pitfalls & fixes

* **“Package not found”**: check `[tool.setuptools.packages.find] where/include` and your `src/` layout.
* **Data files missing at runtime**: move them to `yourpkg/` and declare in `[tool.setuptools.package-data]`; access via `importlib.resources.files("yourpkg").joinpath(...).read_text()`.
* **Entry points not found**: verify the fully qualified `module:function` path and that the module is in the discovered package.
* **Dynamic version missing**: if using `setuptools-scm`, ensure you have Git metadata or a fallback (e.g., sdist includes `_version.py` auto-written by scm).
* **Namespace packages**: don’t mix old namespace styles with PEP 420. Pick one.

---

# 14) Minimal working example (typical “src layout”, console script, extras, package data)

```
project/
├─ pyproject.toml
├─ README.md
├─ LICENSE
├─ src/
│  └─ yourpkg/
│     ├─ __init__.py
│     ├─ cli.py
│     └─ data/
│        └─ default.json
└─ tests/
```

**`pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "yourpkg"
version = "1.2.3"
description = "Modernized packaging example"
readme = { file = "README.md", content-type = "text/markdown" }
requires-python = ">=3.9"
license = { file = "LICENSE" }
authors = [{ name = "You", email = "you@example.com" }]
classifiers = ["Programming Language :: Python :: 3"]
dependencies = [
  "requests>=2.31",
]

[project.optional-dependencies]
dev = ["pytest", "build"]

[project.scripts]
yourpkg = "yourpkg.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
yourpkg = ["data/*.json"]
```

---

# 15) If you want to switch backends later

Once you’re stable on `pyproject.toml` + setuptools, you can later try **Hatchling** or **Flit** with the same `[project]` metadata (PEP 621). Start by changing `[build-system]` and the tool-specific sections; keep a test tag/release to validate.

---

## TL;DR checklist

1. Extract all `setup()` args and decide how to map them.
2. Add `pyproject.toml` with `[build-system]` (setuptools) + `[project]` (PEP 621).
3. Configure `[tool.setuptools.*]` for packages, package-data, entry points, and (if needed) extensions.
4. Keep/trim `MANIFEST.in` only for sdist-only extras.
5. (Optional) add `setuptools-scm` and switch to `dynamic = ["version"]`.
6. `python -m build` → `pip install -e .[dev]` → run tests/CLI.
7. Delete `setup.py` once green.

# 🚀 UV Setup Guide for fan2quizz

This project uses [uv](https://github.com/astral-sh/uv) - an extremely fast Python package installer and resolver written in Rust.

## Why UV?

- **10-100x faster** than pip for package installation
- **Reliable dependency resolution** with proper conflict detection
- **Drop-in replacement** for pip with the same CLI interface
- **Modern Python tooling** recommended for all new projects

## Installing UV

### Quick Install (Recommended)

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip (if you must)
pip install uv
```

### Verify Installation

```bash
uv --version
```

You should see something like: `uv 0.x.x`

## Setting Up fan2quizz with UV

### 1. Clone and Navigate

```bash
git clone https://github.com/BastienZim/fan2quizz.git
cd fan2quizz
```

### 2. Install Dependencies

UV will automatically create and manage a virtual environment:

```bash
# Install in editable mode (recommended for development)
uv pip install -e .

# Or install from requirements.txt
uv pip install -r requirements.txt

# Install optional dependencies
uv pip install rich pyperclip wcwidth
```

### 3. Run Scripts with UV

UV provides the `uv run` command which automatically uses the correct Python environment:

```bash
# Daily report
uv run scripts/daily_report.py

# Parse quiz results
uv run scripts/parse_results.py

# Track mistakes
uv run scripts/process_quiz.py
```

## UV Commands Reference

### Package Management

```bash
# Install a package
uv pip install package-name

# Install multiple packages
uv pip install package1 package2 package3

# Install from requirements.txt
uv pip install -r requirements.txt

# Uninstall a package
uv pip uninstall package-name

# List installed packages
uv pip list

# Show package info
uv pip show package-name
```

### Running Scripts

```bash
# Run a Python script
uv run script.py

# Run a module
uv run -m module.name

# Run with arguments
uv run script.py --arg value
```

### Virtual Environment Management

UV automatically manages virtual environments, but you can also:

```bash
# Create a new venv
uv venv

# Create with specific Python version
uv venv --python 3.11

# Activate (if needed - uv run does this automatically)
source .venv/bin/activate
```

## Migration from pip/venv

If you're coming from traditional pip:

| Old Command | UV Equivalent |
|-------------|---------------|
| `python -m venv .venv` | `uv venv` |
| `pip install package` | `uv pip install package` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip install -e .` | `uv pip install -e .` |
| `python script.py` | `uv run script.py` |
| `python -m module` | `uv run -m module` |

## Advantages for fan2quizz

1. **Faster Setup**: Get started in seconds, not minutes
2. **Consistent Environment**: UV ensures everyone has the same dependencies
3. **No Activation Needed**: `uv run` automatically uses the right environment
4. **Better Errors**: Clear messages when dependencies conflict

## Troubleshooting

### "uv: command not found"

Make sure UV is in your PATH. After installation, restart your terminal or run:

```bash
source ~/.bashrc  # or ~/.zshrc for zsh
```

### "No Python interpreter found"

UV needs Python to be installed. Install Python 3.9+ first:

```bash
# Ubuntu/Debian
sudo apt install python3

# macOS (with Homebrew)
brew install python@3.11
```

### Dependency Conflicts

UV will clearly report any conflicts. Check the error message and update your requirements:

```bash
# See what's installed
uv pip list

# Check for conflicts
uv pip check
```

### Scripts Don't Run

Make sure you've installed the package:

```bash
# Install in editable mode
uv pip install -e .

# Then run scripts
uv run scripts/daily_report.py
```

## Advanced Usage

### Lock Files (Optional)

For even more reproducibility, you can use lock files:

```bash
# Generate a lock file (if using pyproject.toml)
uv pip compile pyproject.toml -o requirements.lock

# Install from lock file
uv pip install -r requirements.lock
```

### Multiple Python Versions

UV can work with different Python versions:

```bash
# Create venv with specific Python
uv venv --python 3.11

# Or specify when running
uv run --python 3.11 script.py
```

### Offline Mode

UV can work offline if packages are cached:

```bash
# Install with offline mode
uv pip install --offline package-name
```

## Tips for Daily Use

1. **Always use `uv run`** instead of `python` for scripts
2. **No need to activate** the virtual environment
3. **Install globally with UV** for faster package management
4. **Use `uv pip compile`** to pin exact versions for reproducibility

## Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV vs pip Comparison](https://github.com/astral-sh/uv#comparison)
- [Python Packaging Guide](https://packaging.python.org/)

## Quick Start Commands (Summary)

```bash
# First time setup
curl -LsSf https://astral.sh/uv/install.sh | sh
cd fan2quizz
uv pip install -e .

# Daily usage
uv run scripts/daily_report.py
uv run scripts/process_quiz.py

# Add a new package
uv pip install new-package

# Update packages
uv pip install --upgrade package-name
```

---

**Ready to go!** UV makes Python package management fast and reliable. Enjoy using fan2quizz! 🎉

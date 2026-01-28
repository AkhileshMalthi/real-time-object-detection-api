# Development Workflow Guide

This guide explains the automated quality checks and CI/CD pipeline for this project.

## Pre-commit Hooks 🎣

Pre-commit hooks run automatically before each commit to catch issues early.

### Initial Setup

```bash
# Install pre-commit hooks (one-time setup)
uv run pre-commit install
```

### What Gets Checked

1. **Ruff Linter** - Fast Python linter (catches bugs, style issues)
2. **Ruff Formatter** - Automatic code formatting (replaces Black)
3. **Trailing Whitespace** - Removes unnecessary whitespace
4. **End of File** - Ensures files end with newline
5. **YAML/TOML Syntax** - Validates config files
6. **Merge Conflicts** - Detects leftover merge markers
7. **Large Files** - Prevents committing huge files (>10MB)
8. **Python AST** - Validates Python syntax
9. **Debug Statements** - Catches forgotten debugger imports

### Manual Usage

```bash
# Run hooks on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files

# Skip hooks for a commit (use sparingly!)
git commit -m "message" --no-verify
```

### Auto-fix

Most hooks auto-fix issues! If a hook fails:
1. Check what was changed: `git diff`
2. Review the auto-fixes
3. Stage the changes: `git add .`
4. Commit again

## Continuous Integration (CI) 🤖

GitHub Actions automatically runs on every push and pull request.

### CI Pipeline Jobs

#### 1. **Lint** (Fast ~30s)
- ✅ Ruff linter check
- ✅ Ruff formatter check
- 📋 Reports issues as GitHub annotations

#### 2. **Test** (Moderate ~1-2min)
- ✅ Unit tests (fast, with mocks)
- ✅ Integration tests (API endpoints)
- ✅ E2E tests (real model)
- 📊 Code coverage report
- 🔄 Tests on multiple Python versions

#### 3. **Build** (Fast ~30s)
- ✅ Package build verification
- 📦 Uploads build artifacts

### Viewing CI Results

1. Go to your PR or commit on GitHub
2. Scroll to "Checks" section
3. Click on failing jobs to see details
4. GitHub annotations show exact line numbers for issues

### Local CI Simulation

Run the same checks locally before pushing:

```bash
# 1. Linting
uv run ruff check .
uv run ruff format --check .

# 2. Fast tests (skip E2E)
uv run pytest tests/ -m "not e2e" --cov=api

# 3. All tests including E2E
uv run pytest tests/ --cov=api

# 4. Build package
uv build
```

## Testing Strategy 📊

```
                    E2E Tests (7)
                  /             \
              Integration (8)    |  <- Real model, slower
            /                    |
        Unit Tests (6)           |  <- Mocked, fast
```

### Running Tests

```bash
# All tests (recommended before commit)
uv run pytest tests/ -v

# Fast tests only (during development)
uv run pytest tests/ -v -m "not e2e"

# E2E tests only (debug model issues)
uv run pytest tests/ -v -m e2e

# With coverage report
uv run pytest tests/ --cov=api --cov-report=html
```

### Test Markers

- `@pytest.mark.e2e` - End-to-end tests (slow, real model)
- Use `-m "not e2e"` to skip slow tests

## Code Quality Tools 🛠️

### Ruff (Linter + Formatter)

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Check formatting without changing
uv run ruff format --check .
```

### Configuration

- **Ruff config**: `ruff.toml`
- **Pre-commit config**: `.pre-commit-config.yaml`
- **Pytest config**: `pyproject.toml` → `[tool.pytest.ini_options]`
- **CI config**: `.github/workflows/ci.yml`

## Recommended Workflow 🔄

### Daily Development

```bash
# 1. Pull latest changes
git pull

# 2. Make your changes
# ... edit files ...

# 3. Run fast tests
uv run pytest tests/ -m "not e2e" -v

# 4. Commit (pre-commit runs automatically)
git add .
git commit -m "feat: add new feature"

# 5. Push (CI runs automatically)
git push
```

### Before Opening PR

```bash
# Run all quality checks locally
uv run pre-commit run --all-files
uv run pytest tests/ -v --cov=api
uv run ruff check .
uv run ruff format --check .

# Push and create PR
git push
```

### Fixing CI Failures

**If linting fails:**
```bash
uv run ruff check . --fix
uv run ruff format .
git add .
git commit -m "fix: lint issues"
git push
```

**If tests fail:**
```bash
# Run failing tests locally
uv run pytest tests/test_file.py::TestClass::test_method -v

# Fix the issue
# ... edit code ...

# Verify fix
uv run pytest tests/ -v

git add .
git commit -m "fix: failing test"
git push
```

## Tips & Best Practices 💡

1. **Commit often** - Smaller commits are easier to review
2. **Run tests locally** - Faster feedback than waiting for CI
3. **Let hooks auto-fix** - Don't fight the formatter
4. **Check CI early** - Don't wait until PR is "done"
5. **Use meaningful commit messages** - Helps with debugging later

## Troubleshooting 🔧

### Pre-commit Issues

**"No module named 'X'"**
```bash
# Reinstall pre-commit environments
uv run pre-commit clean
uv run pre-commit install
```

**"Hook fails but I can't see why"**
```bash
# Run with verbose output
uv run pre-commit run --all-files --verbose
```

### CI Issues

**"Tests pass locally but fail in CI"**
- Check Python version matches (3.12)
- Check environment variables in `.env`
- Check file paths (use `/` not `\`)

**"CI is slow"**
- E2E tests download model (~6MB)
- Consider caching in CI (advanced)

## Additional Resources 📚

- [Pre-commit Documentation](https://pre-commit.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/actions)

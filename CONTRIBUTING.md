# Contributing to License Uploader

Thank you for your interest in contributing to License Uploader! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

---

## Code of Conduct

This project follows a Code of Conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other contributors

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/license_uploader.git
   cd license_uploader
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/license_uploader.git
   ```

## How to Contribute

### Types of Contributions

We welcome:
- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🎨 UI/UX enhancements
- 🧪 Test coverage improvements
- 🔒 Security enhancements
- ♿ Accessibility improvements
- 🌍 Internationalization/localization

## Development Setup

### Prerequisites

- Python 3.11+ (3.12 or 3.13 recommended)
- Git
- Platform-specific requirements (see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md))

### Setup Steps

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate   # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**:
   ```bash
   export FLASK_ENV=development  # Linux/macOS
   # or
   set FLASK_ENV=development     # Windows

   python app.py
   ```

5. **Access at**: http://localhost:5000

## Coding Standards

### Python Style Guide

- Follow **PEP 8** style guide
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules
- Maximum line length: 100 characters (flexible for readability)
- Use type hints where appropriate

### Code Quality

```python
# Good example
def calculate_total(items: list[dict]) -> float:
    """
    Calculate total price from list of items.

    Args:
        items: List of item dictionaries with 'price' key

    Returns:
        Total price as float
    """
    return sum(item['price'] for item in items)


# Bad example
def calc(x):
    return sum([i['price'] for i in x])
```

### Documentation

- Update documentation when changing functionality
- Add comments for complex logic
- Keep README.md up to date
- Update relevant guides in `docs/` directory

### Testing

- Add tests for new features
- Run existing tests before submitting PR
- Ensure security tests pass:
  ```bash
  python test_security.py
  ```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(extraction): add support for RTF documents

Implement RTF document parsing using pyrtf library.
Includes text extraction and formatting preservation.

Closes #42
```

```
fix(security): sanitize file upload paths

Prevent path traversal attacks by validating upload paths.
Add additional validation in validate_session_file_path().

Fixes #123
```

```
docs(readme): update installation instructions

Add troubleshooting section for Windows users.
Clarify Python version requirements.
```

### Commit Best Practices

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Keep subject line under 50 characters
- Wrap body at 72 characters
- Reference issues and PRs in footer

## Pull Request Process

### Before Submitting

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**:
   ```bash
   python test_security.py
   # Test manually with different file types
   ```

3. **Check code quality**:
   ```bash
   # Verify no syntax errors
   python -m py_compile *.py
   ```

4. **Update documentation** if needed

### Submitting Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature-branch-name
   ```

2. **Create Pull Request** on GitHub

3. **Fill out PR template**:
   - Clear description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if UI changes)

### PR Requirements

- [ ] Code follows project style guidelines
- [ ] Documentation updated (if applicable)
- [ ] Tests pass
- [ ] No security vulnerabilities introduced
- [ ] Commit messages follow guidelines
- [ ] PR description is clear and complete

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, maintainers will merge

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Try latest version
3. Review [TROUBLESHOOTING_GUIDE.md](docs/TROUBLESHOOTING_GUIDE.md)

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.11.5]
- Browser: [e.g., Chrome 120]

**Additional Context**
Any other relevant information
```

## Suggesting Enhancements

### Enhancement Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Implementation**
How could this be implemented?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Mockups, examples, etc.
```

---

## Development Resources

- **Developer Guide**: [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)
- **API Documentation**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- **Security Guide**: [docs/SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md)
- **Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

## Questions?

- Open a [GitHub Discussion](../../discussions)
- Review [documentation](docs/)
- Check [existing issues](../../issues)

---

Thank you for contributing to License Uploader! 🎉

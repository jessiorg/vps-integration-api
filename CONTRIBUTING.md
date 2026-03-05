# Contributing to VPS Integration API

Thank you for your interest in contributing to the VPS Integration API! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful and inclusive. We welcome contributions from everyone.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/jessiorg/vps-integration-api/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, Docker version)
   - Relevant logs

### Suggesting Enhancements

1. Check [existing issues](https://github.com/jessiorg/vps-integration-api/issues) for similar suggestions
2. Create a new issue with:
   - Clear description of the enhancement
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/vps-integration-api.git
   cd vps-integration-api
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   # Run the API locally
   docker-compose up
   
   # Test endpoints
   curl http://localhost:8000/health
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```
   
   Use conventional commits:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Link any related issues

## Development Setup

### Prerequisites

- Python 3.12+
- Docker 24.0+
- Git

### Local Development

```bash
# Clone repository
git clone https://github.com/jessiorg/vps-integration-api.git
cd vps-integration-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your GitHub OAuth credentials

# Run locally
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Manual testing
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Test with Docker
docker-compose up
```

## Code Style

### Python

- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and small

```python
def example_function(param: str) -> dict:
    """Brief description of function.
    
    Args:
        param: Description of parameter
    
    Returns:
        Description of return value
    """
    return {"result": param}
```

### Commit Messages

```
Add: feature description

- Bullet point 1
- Bullet point 2

Closes #123
```

## Project Structure

```
api/
├── main.py              # FastAPI app
├── config.py            # Configuration
├── auth/               # Authentication
├── routers/            # API endpoints
├── middleware/         # Middleware
└── utils/              # Utilities
```

## Adding New Features

### 1. New API Endpoint

```python
# In api/routers/your_module.py
from fastapi import APIRouter, Depends
from api.auth.security import get_current_user

router = APIRouter()

@router.get("/your-endpoint")
async def your_endpoint(
    current_user: dict = Depends(get_current_user)
):
    """Endpoint description"""
    return {"message": "Hello"}
```

### 2. Include Router in Main App

```python
# In api/main.py
from api.routers import your_module

app.include_router(
    your_module.router,
    prefix="/api/v1/your-module",
    tags=["Your Module"]
)
```

### 3. Update Documentation

- Add endpoint to README.md
- Add examples to docs/EXAMPLES.md
- Update API documentation strings

## Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email: [your-email@example.com]
2. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Security Checklist

- [ ] Input validation
- [ ] Path traversal protection
- [ ] Authentication required
- [ ] Rate limiting considered
- [ ] No sensitive data in logs
- [ ] No hardcoded credentials

## Documentation

### Update When:

- Adding new endpoints
- Changing existing functionality
- Adding configuration options
- Fixing bugs that affect usage

### Documentation Files:

- `README.md` - Main documentation
- `QUICKSTART.md` - Quick start guide
- `docs/MCP_INTEGRATION.md` - MCP integration
- `docs/EXAMPLES.md` - Usage examples

## Review Process

1. Automated checks must pass
2. Code review by maintainer
3. Documentation updated
4. No merge conflicts
5. Follows project conventions

## Questions?

Feel free to:
- Open an issue for discussion
- Ask in pull request comments
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to VPS Integration API! 🎉

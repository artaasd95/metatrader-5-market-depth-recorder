# Contributing to MetaTrader 5 Market Depth Recorder

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/metatrader-5-market-depth-recorder.git
   cd metatrader-5-market-depth-recorder
   ```

3. **Set up development environment**:
   ```powershell
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   .\venv\Scripts\Activate.ps1
   
   # Install development dependencies
   pip install -r requirements.txt
   ```

## Code Style

- Follow **PEP 8** guidelines for Python code
- Use **descriptive variable names**
- Include **type hints** for function parameters and returns
- Write **docstrings** for all public functions and classes

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test thoroughly

3. **Run code quality checks**:
   ```bash
   # Check syntax
   python -m py_compile src/orderbook_loader.py
   
   # Run any existing tests
   # (Add your test suite as the project grows)
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: describe your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Commit Message Convention

Use conventional commit messages:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for code style changes
- `refactor:` for code refactoring
- `test:` for test-related changes
- `chore:` for maintenance tasks

## Testing

When adding new features, include appropriate tests:
- Unit tests for individual functions
- Integration tests for MT5 and InfluxDB interactions
- Performance tests for high-frequency data handling

## Documentation

- Update README.md for significant changes
- Add comments for complex logic
- Document new environment variables
- Update example configurations if needed

## Issues and Bug Reports

When reporting issues, please include:
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, MT5 version)
- Relevant error messages or logs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
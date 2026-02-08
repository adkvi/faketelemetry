# Contributing to FakeTelemetry

Thanks for your interest in improving FakeTelemetry!

## Reporting Issues

If you find a bug or have a feature request, please [open an issue](https://github.com/adkvi/faketelemetry/issues) and include:

- Python version (`python --version`)
- OS and version
- Minimal code to reproduce the problem
- Full error traceback (if applicable)

## Development Setup

```sh
git clone https://github.com/adkvi/faketelemetry.git
cd faketelemetry
pip install -e ".[dev]"
```

## Running Tests

```sh
pytest -v
```

## Code Style

This project uses [Black](https://github.com/psf/black) for formatting and [mypy](https://mypy-lang.org/) for type checking.

```sh
black faketelemetry tests
mypy faketelemetry
```

## Pull Requests

1. Fork the repo and create a branch from `main`.
2. Add tests for any new functionality.
3. Make sure all tests pass and code is formatted.
4. Open a pull request with a clear description of what changed and why.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

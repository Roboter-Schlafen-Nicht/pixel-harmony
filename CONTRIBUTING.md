# Contributing to PixelHarmony

First off, thank you for considering contributing to PixelHarmony! It's people like you that make PixelHarmony such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to [business@roboterschlafennicht.de].

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for PixelHarmony. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

- Use a clear and descriptive title for the issue to identify the problem.
- Describe the exact steps which reproduce the problem in as many details as possible.
- Provide specific examples to demonstrate the steps.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for PixelHarmony, including completely new features and minor improvements to existing functionality.

- Use a clear and descriptive title for the issue to identify the suggestion.
- Provide a step-by-step description of the suggested enhancement in as many details as possible.
- Provide specific examples to demonstrate the steps.

### Your First Code Contribution

Unsure where to begin contributing to PixelHarmony? You can start by looking through these `beginner` and `help-wanted` issues:

- Beginner issues - issues which should only require a few lines of code, and a test or two.
- Help wanted issues - issues which should be a bit more involved than `beginner` issues.

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible.
- Follow the Python styleguides.
- Include thoughtfully-worded, well-structured tests.
- Document new code based on the Documentation Styleguide
- End all files with a newline

## Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Python Styleguide

All Python code must adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/). To enforce this, we use the following tools:

1. **Flake8**: A tool that checks your code against PEP 8 style rules.
2. **Black**: An opinionated code formatter that automatically formats your code to conform to PEP 8.
3. **Pre-commit hooks**: To automatically run these checks before each commit.

## Setting up the development environment

1. Follow the installation steps in the README.md file.

2. Create a `.env` file in the project root with the following content:
   ```
   PYTHONPATH=.:${PYTHONPATH}
   ANTHROPIC_API_KEY='your-api-key-here'
   ```
   Replace 'your-api-key-here' with your actual Anthropic API key.

3. Install the required tools:
   ```
   pip install -r requirements.txt
   ```

4. Set up pre-commit hooks:
   ```
   pre-commit install
   ```


### Documentation Styleguide

- Use [Markdown](https://daringfireball.net/projects/markdown).

## Contributors

Thanks to everyone who has contributed to PixelHarmony!

- Dennis Lemon - Project Creator and Main Developer
- Claude (Anthropic AI) - Assistance with documentation and code examples

Note: Claude is an AI assistant developed by Anthropic to be helpful, harmless, and honest. While Claude provided assistance in creating project documentation and code examples, all substantial creative decisions and implementations were made by human developers.

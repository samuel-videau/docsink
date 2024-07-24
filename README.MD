# docsink

Automated documentation updater that syncs your docs with your code using AI.

## Features

- Automatically updates documentation based on recent commits
- Uses Claude AI to generate relevant documentation updates
- Supports multiple documentation files
- Configurable ignore patterns with `.docsinkignore`

## Installation

```
pip install docsink
```

## Usage

Run docsink in your Git repository:

```
docsink --api-key YOUR_ANTHROPIC_API_KEY
```

Or run it without the API key argument, and you'll be prompted to enter it:

```
docsink
```

## Configuration

### docsink_config.json

docsink will create a `docsink_config.json` file in your current directory. You can edit this to customize:

- `docs_folder`: Where to store documentation (default: "docs")
- `readme_file`: Name of the main documentation file (default: "README.md")

### .docsinkignore

Create a `.docsinkignore` file in your project root to specify files and directories that docsink should ignore. For example:

```
docs/generated/
*.log
```

This will ignore the `docs/generated/` directory and all `.log` files.

## How it works

1. docsink analyzes recent commits in your repository
2. It filters out changes to ignored files (based on `.docsinkignore`)
3. For each documentation file, it sends the current content and recent changes to Claude AI
4. Claude AI generates updated documentation based on the changes
5. docsink writes the updated content back to the documentation files

## Note

Your Anthropic API key is required to use docsink but is never stored. Make sure to keep your API key secure and do not share it.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Disclaimer

docsink is an AI-assisted tool. While it strives for accuracy, always review the generated documentation for correctness and completeness.
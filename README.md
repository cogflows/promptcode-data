# promptcode-data

## Overview

This repository stores the data sources used by the [PromptCode VS Code extension](https://github.com/cogflows/promptcode-vscode). It includes an index of available content (like LLM definitions, guides, code snippets, etc.) and also hosts manually managed content files referenced by the index.

The primary goal is to provide a centralized, version-controlled location for the content sources accessible within the PromptCode extension.

## Repository Structure

```
promptcode-data/
├── content/
│   ├── index.json        # The main index file listing all available content sources.
│   └── raw/              # Contains the actual content files for sources hosted manually within this repo.
│       └── frameworks/     # Example: Mirroring category structure
│           └── web/
│               └── typescript/
│                   └── nextjs/
│                       └── some_nextjs_guide.txt # Example file path
├── README.md             # This file.
└── LICENSE               # MIT License file.
```

* `/content/index.json`: The main index file listing all available content sources. See format details below.
* `/content/raw/`: Contains the actual content files for sources that are manually hosted within this repository. It's recommended to organize this directory mirroring the category structure defined in `index.json`.
* `README.md`: This file, providing guidance on the repository structure and contribution process.
* `LICENSE`: Contains the MIT License terms.

## Index File Format (`content/index.json`)

The `content/index.json` file contains a JSON array where each object represents a single content source available to the PromptCode extension. Each object should adhere to the following structure:

* **`name`** (string, required): The base identifier for the content (e.g., `"pydantic_ai_llms_full"`). This should be unique within its category.
* **`category`** (string, required): Represents the hierarchical category path (e.g., `"Docs/Agent frameworks"]`). The PromptCode extension typically displays this path prefixed with `@` (e.g., `@dDcs/Agent rameworks`).
* **`url`** (string, required): The direct URL from which the PromptCode extension should fetch the actual content file.
    * For externally hosted content, this is the URL to the resource.
    * For manually hosted files within this repository, this **must** be the raw GitHub content URL pointing to the file within the `/content/raw/` directory.
* **`description`** (string, optional): A brief description of the content, potentially shown in the PromptCode UI to help users understand what the source contains.
* **`tags`** (array of strings, optional): Keywords relevant to the content, which might be used for future search or filtering features.

**Example Entry:**

```json
[
  {
    "name": "pydantic_ai_llms_full",
    "category": "Docs/Agent framwork",
    "url": "[https://ai.pydantic.dev/llms.txt](https://ai.pydantic.dev/llms.txt)",
    "description": "Pydantic AI LLM Definitions",
    "tags": ["python", "agent", "pydantic", "llm"]
  }
]
```
*(Note: The full `index.json` file should contain a valid JSON array `[...]` wrapping all the entry objects)*

## Manual Content Files (`content/raw/`)

Files that are referenced by a `url` pointing within this repository (i.e., manually managed content) should be placed under the `/content/raw/` directory.

**Organization:** To keep the repository organized and make manual files easier to locate, please mirror the `category` structure from `index.json` within the `raw` directory.

* *Example:* If you add a manual file with `category: ["frameworks", "web", "typescript", "nextjs"]` in `index.json`, the corresponding file should ideally be placed at `/content/raw/frameworks/web/typescript/nextjs/your_filename.txt`. The URL in `index.json` would then be `https://raw.githubusercontent.com/cogflows/promptcode-data/main/content/raw/frameworks/web/typescript/nextjs/your_filename.txt`.

## Contributing

Contributions to expand the available content sources are welcome! Please follow these steps:

1.  **Fork** this repository.
2.  Create a **new branch** for your changes (e.g., `git checkout -b add-new-guide`).
3.  **Make your changes:**
    * **Adding an External Source:** Edit `content/index.json` and add a new JSON object entry for the external resource, ensuring all required fields are present and the `url` points to the correct external location.
    * **Adding a Manual Source:**
        1.  Determine the appropriate `category` for your content.
        2.  Create the corresponding subdirectory structure under `/content/raw/` if it doesn't already exist (following the example structure shown above).
        3.  Add your content file(s) to that directory.
        4.  Edit `content/index.json` and add a new JSON object entry for your manual source. Critically, ensure the `url` field correctly points to the **raw GitHub URL** of the file you just added (you can get this URL by navigating to the file on GitHub and clicking the "Raw" button).
4.  **Validate** your `content/index.json` file to ensure it's still valid JSON (e.g., using an online validator or IDE checks).
5.  **Commit** your changes with a clear commit message.
6.  **Push** your branch to your fork.
7.  Open a **Pull Request** to the `main` branch of this repository (`cogflows/promptcode-data`). Describe the source(s) you are adding or updating.

**Note on Large Files:** Git is not ideal for very large files (>50-100MB). If you intend to add a manual content file that is very large, please mention this in your Pull Request. We may need to configure Git LFS (Large File Storage) for such files.

## Usage

This data repository, specifically the `content/index.json` file, is fetched and utilized by the [PromptCode VS Code extension](https://github.com/cogflows/promptcode-vscode) to populate the list of available content sources for users.

## License

This repository and its contents are licensed under the **MIT License**. Please see the `LICENSE` file for the full text.


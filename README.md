# Synthetic Data Studio

Generate synthetic datasets locally using Large Language Models (LLMs) through [Ollama](https://ollama.com/) and an interactive Gradio interface.

Synthetic Data Studio lets you describe a dataset in natural language, configure the generation strategy, preview the results, and export the generated records as CSV or JSONL files.

## Features

- **Local LLM integration:** Discover and select models installed in Ollama.
- **Natural-language prompts:** Describe the dataset you want to generate.
- **Configurable dataset size:** Generate between 1 and 50 records per request.
- **Multiple generation strategies:**
  - **Balanced:** Mix ordinary, unusual, positive, and negative examples.
  - **Diverse:** Vary wording, scenarios, complexity, and edge cases.
  - **Realistic:** Generate plausible examples resembling real-world situations.
  - **Edge cases:** Focus on unusual inputs, boundary conditions, and ambiguous scenarios.
- **Temperature control:** Adjust the model's generation behavior.
- **Interactive preview:** Inspect generated records in a table.
- **Export options:** Download generated datasets in CSV or JSONL format.
- **Error handling:** Display useful messages for connection failures, timeouts, and invalid model responses.

## Tech Stack

- Python
- Gradio — interactive web interface
- Ollama — local LLM inference
- Requests — communication with the Ollama API
- Pandas — tabular data processing
- JSON — structured model output and JSONL export

## Architecture

1. The application retrieves the locally installed Ollama models.
2. The user selects a model and describes the desired dataset.
3. The application builds a prompt using the selected generation strategy and temperature.
4. Ollama generates structured JSON records.
5. The application validates the response and converts the records into a Pandas DataFrame.
6. The generated data is displayed in the interface and made available for download.

## Prerequisites

Before running the application, install:

- Python 3.10 or newer
- [Ollama](https://ollama.com/download)
- At least one model supported by your hardware

The application communicates with Ollama at `http://localhost:11434` by default.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Ryan2420/Synthetic_data_studio.git
cd Synthetic_data_studio
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install gradio pandas requests
```

### 4. Install and run an Ollama model

Download a model suitable for your computer. For example:

```bash
ollama pull qwen3:8b
```

Start Ollama if it is not already running, then verify the installed model:

```bash
ollama list
```

Model performance depends on available RAM, VRAM, and the model selected.

## Usage

Run the application:

```bash
python app.py
```

Open the local URL displayed in the terminal, usually:

`http://127.0.0.1:7860`

Then:

1. Select an installed AI model.
2. Describe the dataset you want to generate.
3. Choose the number of records.
4. Select a generation strategy.
5. Adjust the temperature if needed.
6. Choose CSV or JSONL as the output format.
7. Click **Generate dataset**.
8. Review the generated records and download the file.

### Example prompt

```text
Generate customer support conversations for an online
electronics store. Include customer questions, complaints,
refund requests, order issues, and resolutions.

Use consistent fields such as:
customer_message, category, priority, and resolution.
```

## Output Formats

**CSV**

Suitable for spreadsheets, Pandas, data analysis, and many machine learning workflows.

**JSONL**

Stores one JSON record per line, making it convenient for data-processing pipelines and certain LLM training workflows.

## Limitations

- Generation requires a running Ollama service and an installed model.
- Output quality and consistency depend on the selected model and prompt.
- The application requests up to 50 records per generation.
- The actual number of returned records can be lower than requested if the model produces fewer examples.
- Generated data is artificial and may contain errors, duplicates, or unrealistic values.
- The application does not currently provide automatic schema enforcement, dataset quality scoring, or duplicate detection.

Always inspect and validate generated datasets before using them for training, evaluation, or other downstream tasks.

## Privacy

Inference is performed through the local Ollama service by default. Prompts and generated data are sent to the configured local Ollama endpoint rather than a hosted LLM API.

Privacy also depends on your Ollama configuration, installed models, and machine security.

## Future Improvements

Potential extensions include:

- Custom schema definition and validation
- Configurable column types and constraints
- Duplicate detection and data-quality metrics
- Larger datasets through batch generation
- Generation history and reproducibility settings
- Support for additional output formats
- Dataset evaluation and quality reports

## Author

**Ryan Harmel**

AI Engineering Student | Interested in LLM Engineering and Agentic AI

## License

No license has been specified yet. Until a license is added to the repository, others should not assume they have permission to reuse, modify, or redistribute this project.

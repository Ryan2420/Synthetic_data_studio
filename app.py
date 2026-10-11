
import json
import tempfile
from pathlib import Path

import gradio as gr
import pandas as pd
import requests


OLLAMA_URL = "http://localhost:11434"


def get_models():
    """Return the models installed in Ollama."""
    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags", timeout=3
        )
        response.raise_for_status()

        models = response.json().get("models", [])
        return [model["name"] for model in models]

    except requests.RequestException:
        return []


PROMPT_STYLES = {
    "Balanced": (
        "Generate a balanced mixture of ordinary, unusual, "
        "positive, and negative examples."
    ),
    "Diverse": (
        "Maximize diversity. Vary wording, scenarios, "
        "length, complexity, and edge cases. Avoid repetition."
    ),
    "Realistic": (
        "Generate plausible examples that resemble real-world "
        "situations. Do not claim invented data is real."
    ),
    "Edge cases": (
        "Focus on unusual inputs, boundary conditions, "
        "ambiguous situations, and rare scenarios."
    ),
}


def generate_dataset(
    model_name,
    data_description,
    number_of_rows,
    style,
    temperature,
    output_format,
):
    if not model_name:
        raise gr.Error(
            "No Ollama models found. Start Ollama and install a model."
        )

    if not data_description.strip():
        raise gr.Error("Please describe the dataset you want.")

    number_of_rows = int(number_of_rows)

    system_prompt = """
You are a synthetic dataset generation engine.

Generate artificial data for the user's requested purpose.

Return ONLY a valid JSON object with this structure:
{
  "examples": [
    {"field1": "value1", "field2": "value2"}
  ]
}

Requirements:
- Generate the requested number of examples.
- Use consistent field names across all examples.
- Make examples diverse and relevant.
- Do not repeat examples unnecessarily.
- Follow the user's requested schema if provided.
- Do not invent claims that synthetic data is real.
- Return JSON only, without Markdown fences.
"""

    user_prompt = f"""
Dataset description:
{data_description}

Number of examples requested: {number_of_rows}

Diversity instructions:
{PROMPT_STYLES[style]}

Temperature: {temperature}

Generate the dataset now.
"""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": float(temperature),
                    "num_predict": 8192,
                },
            },
            timeout=600,
        )
        response.raise_for_status()

        content = response.json()["message"]["content"]
        result = json.loads(content)

        if isinstance(result, dict):
            examples = result.get("examples", [])
        elif isinstance(result, list):
            examples = result
        else:
            examples = []

        if not examples or not all(
            isinstance(item, dict) for item in examples
        ):
            raise ValueError(
                "The model did not return a valid list of records."
            )

        # Keep the requested maximum number of records.
        examples = examples[:number_of_rows]

        df = pd.DataFrame(examples)

        if df.empty:
            raise ValueError("The generated dataset is empty.")

        # Create a downloadable file.
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv" if output_format == "CSV" else ".jsonl",
            encoding="utf-8",
            newline="",
            delete=False,
        ) as file:
            file_path = file.name

        if output_format == "CSV":
            df.to_csv(file_path, index=False)
        else:
            with open(file_path, "w", encoding="utf-8") as file:
                for record in examples:
                    file.write(
                        json.dumps(record, ensure_ascii=False) + "\n"
                    )

        status = (
            f"Generated {len(df)} records using {model_name}. "
            f"Requested: {number_of_rows}. "
            f"Review the results before using them."
        )

        return df, status, file_path

    except requests.ConnectionError:
        raise gr.Error(
            "Cannot connect to Ollama. Start Ollama and try again."
        )

    except requests.Timeout:
        raise gr.Error(
            "Generation timed out. Try fewer examples or a smaller model."
        )

    except (requests.RequestException, KeyError, ValueError, json.JSONDecodeError) as error:
        raise gr.Error(f"Generation failed: {error}")


with gr.Blocks(title="Synthetic Data Studio") as demo:
    gr.Markdown("# Synthetic Data Studio")
    gr.Markdown(
        "Generate artificial datasets with local language models."
    )

    with gr.Row():
        with gr.Column():
            models = get_models()

            model_input = gr.Dropdown(
                choices=models,
                value=models[0] if models else None,
                label="AI model",
                allow_custom_value=False,
            )

            description = gr.Textbox(
                label="Dataset description",
                placeholder=(
                    "Example: Generate customer support conversations "
                    "for an online electronics store. Include questions, "
                    "complaints, and refund requests."
                ),
                lines=5,
            )

            number = gr.Slider(
                minimum=1,
                maximum=50,
                value=10,
                step=1,
                label="Number of examples",
            )

            style = gr.Dropdown(
                choices=list(PROMPT_STYLES.keys()),
                value="Diverse",
                label="Generation strategy",
            )

            temperature = gr.Slider(
                minimum=0.1,
                maximum=1.2,
                value=0.7,
                step=0.1,
                label="Temperature",
            )

            output_format = gr.Radio(
                choices=["CSV", "JSONL"],
                value="CSV",
                label="Download format",
            )

            generate_button = gr.Button(
                "Generate dataset",
                variant="primary",
            )

        with gr.Column():
            status = gr.Textbox(
                label="Generation status",
                interactive=False,
            )

            preview = gr.Dataframe(
                label="Generated data preview",
                interactive=False,
            )

            download = gr.File(label="Download your dataset")

    generate_button.click(
        fn=generate_dataset,
        inputs=[
            model_input,
            description,
            number,
            style,
            temperature,
            output_format,
        ],
        outputs=[preview, status, download],
    )


if __name__ == "__main__":
    demo.launch()

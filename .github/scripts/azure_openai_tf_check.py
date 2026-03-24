import os
import requests
import json
import sys

# Configuración
API_KEY = os.getenv("AZURE_API_KEY")
ENDPOINT = "https://ai-openaidiego-pro.openai.azure.com/openai/responses?api-version=2025-04-01-preview"
MODEL = "gpt-5.1-codex-mini"

# Argumentos: tf_file, controls_file, output_file
if len(sys.argv) != 4:
    print("Uso: python azure_openai_tf_check.py <tf_file> <controls_file> <output_file>")
    sys.exit(1)

TF_FILE = sys.argv[1]
MCSB_CONTROLS_FILE = sys.argv[2]
OUTPUT_FILE = sys.argv[3]

def extract_controls(controls_file):
    controls = []
    with open(controls_file, encoding="utf-8") as f:
        content = f.read()
    for block in content.split("## "):
        if block.strip():
            lines = block.strip().splitlines()
            title = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
            controls.append(f"{title}: {body}")
    return controls

def main():
    with open(TF_FILE, encoding="utf-8") as f:
        tf_code = f.read()
    controls = extract_controls(MCSB_CONTROLS_FILE)
    prompt = (
        "Analiza el siguiente código Terraform según los controles de seguridad MCSB relevantes para Azure Storage. "
        "Para cada control, indica si se cumple, si no se cumple, y por qué. "
        "Controles:\n" + "\n".join(controls[:3]) +
        "\n\nCódigo Terraform:\n" + tf_code +
        "\n\nResponde en formato de lista por control."
    )
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    data = {
        "input": [
            {"role": "user", "content": prompt}
        ],
        "max_output_tokens": 1024,
        "model": MODEL
    }
    response = requests.post(ENDPOINT, headers=headers, data=json.dumps(data))
    try:
        result = response.json()
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
            out.write("--- Azure OpenAI Security Check ---\n")
            out.write(json.dumps(result, indent=2, ensure_ascii=False))
            out.write("\n--- End of Security Check ---\n")
        # Print summary for logs
        if "output" in result and result["output"]:
            print("\n--- Output ---\n")
            for msg in result["output"]:
                print(msg.get("content", msg))
    except Exception as e:
        print("Error al parsear la respuesta:", e)
        print(response.text)

if __name__ == "__main__":
    main()

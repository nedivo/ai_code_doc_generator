import argparse
import json
import logging
import os
from src.ai.ai_documentation_generator import AIDocumentationGenerator
from src.mdx_generator.mdx_formatter import MDXFormatter

logging.basicConfig(level=logging.info, format='%(asctime)s - %(levelname)s - %(message)s')

def read_codebase(source_directory):
    logging.info(f"Reading codebase from {source_directory}")
    codebase_structure = {}
    for root, dirs, files in os.walk(source_directory):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code_content = f.read()
                codebase_structure[file_path] = code_content
    return codebase_structure

def should_skip_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        if "@skip_documentation" in content or "# skip_documentation" in content:
            return True
    return False

def process_file(file_path, ai_generator, formatter, root_dir):
    with open(file_path, 'r') as file:
        code = file.read()

    documentation = ai_generator.generate_file_documentation(code)
    mdx_content = formatter.format_to_mdx(documentation)

    docs_dir = os.path.join(root_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    base_file_name = os.path.splitext(os.path.basename(file_path))[0]
    base_file_name = base_file_name.replace('_', '-')
    update_min_json(os.path.join(root_dir, "docs"), base_file_name)

    output_file_name = base_file_name + ".mdx"
    output_path = os.path.join(docs_dir, output_file_name)
    formatter.save_to_mdx_file(mdx_content, output_path)
    logging.info(f"Documentation for {file_path} saved to {output_path}")

def create_documentation(doc_type, code, root, ai_generator, formatter):
    if doc_type == "welcome":
        documentation = ai_generator.generate_custom_docs(code, doc_type)
    elif doc_type == "quickstart":
        documentation = ai_generator.generate_custom_docs(code, doc_type)
    elif doc_type == "what-is-it":
        documentation = ai_generator.generate_custom_docs(code, doc_type)
    elif doc_type == "how-it-works":
        documentation = ai_generator.generate_custom_docs(code, doc_type)
    else:
        logging.warning(f"Unknown documentation type: {doc_type}")
        return

    file_name = doc_type.replace('_', '-')
    mdx_content = formatter.format_to_mdx(documentation)  # Adjust if needed for different types
    file_path = os.path.join(root, file_name)
    docs_dir = os.path.join(root, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    output_file_name = file_name + ".mdx"
    output_path = os.path.join(docs_dir, output_file_name)
    formatter.save_to_mdx_file(mdx_content, output_path)
    logging.info(f"Documentation for {file_path} saved to {output_path}")

def process_everything(code, root, ai_generator, formatter):
    create_documentation("welcome", code, root, ai_generator, formatter)
    create_documentation("quickstart", code, root, ai_generator, formatter)
    create_documentation("what-is-it", code, root, ai_generator, formatter)
    create_documentation("how-it-works", code, root, ai_generator, formatter)

def update_min_json(docs_dir, new_page):
    min_json_path = os.path.join(docs_dir, 'mint.json')
    min_json_data = json.loads(
        """
        {
            "$schema": "https://mintlify.com/schema.json",
            "name": "maud",
            "logo": {
                "dark": "/logo/dark.png",
                "light": "/logo/light.png"
            },
            "favicon": "/favicon.png",
            "modeToggle": {
                "default": "light",
                "isHidden": true
            },
            "colors": {
                "primary": "#0092e0",
                "light": "#0092e0",
                "dark": "#0092e0"
            },
            "topbarCtaButton": {
                "name": "Star us on GitHub!",
                "url": "https://github.com/nedivo/maud"
            },
            "navigation": [
                {
                    "group": "Getting Started",
                    "pages": [
                        "welcome",
                        "quickstart"
                    ]
                },
                {
                    "group": "MAUD Basics",
                    "pages": [
                        "what-is-it",
                        "how-it-works"
                    ]
                },
                {
                    "group": "Element Details",
                    "pages": [
                        "getting-number"
                    ]
                }
            ],
            "footerSocials": {
                "instagram": "https://www.instagram.com/nedivo.co/",
                "linkedin": "https://www.linkedin.com/company/nedivo",
                "website": "https://www.nedivo.co/"
            }
        }
        """
    )

    if os.path.exists(min_json_path):
        with open(min_json_path, 'r') as file:
            min_json_data = json.load(file)

    for group in min_json_data.get("navigation", []):
        if group.get("group") == "Element Details":
            if new_page not in group.get("pages", []):
                group["pages"].append(new_page)
            break

    with open(min_json_path, 'w') as file:
        json.dump(min_json_data, file, indent=4)

    print(f"Updated min.json with page: {new_page}")

def main():
    parser = argparse.ArgumentParser(description='AI Code Documentation Generator')
    parser.add_argument('source_directory', help='Path to the source code directory')
    args = parser.parse_args()

    codebase_content = read_codebase(args.source_directory)

    ai_generator = AIDocumentationGenerator()
    formatter = MDXFormatter()

    process_everything(codebase_content, args.source_directory, ai_generator, formatter)

    for root, dirs, files in os.walk(args.source_directory):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if not should_skip_file(file_path):
                    process_file(file_path, ai_generator, formatter, args.source_directory)
                    break

if __name__ == "__main__":
    main()

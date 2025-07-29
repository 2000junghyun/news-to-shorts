import os
import json
import re

def main():
    input_dir = '../data/parsed/articles_full_20250720'
    output_dir_with = '../data/with-form'
    output_dir_without = '../data/without-form'

    try:
        classify_json_files(input_dir, output_dir_with, output_dir_without)
    except Exception as e:
        print(f"[ERROR] Unexpected error in main(): {e}")

def classify_json_files(input_dir, output_dir_with, output_dir_without):
    try:
        os.makedirs(output_dir_with, exist_ok=True)
        os.makedirs(output_dir_without, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Failed to create output directories: {e}")
        return

    try:
        files = [fname for fname in os.listdir(input_dir) if fname.endswith(".json") and os.path.isfile(os.path.join(input_dir, fname))]
    except Exception as e:
        print(f"[ERROR] Failed to list files in input directory: {e}")
        return

    if not files:
        print(f"[INFO] No JSON files found in input directory: {input_dir}")
        return

    for fname in files:
        fpath = os.path.join(input_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            body = data.get("body", "")

            read_time, cleaned_body = extract_body_and_read_time(body)

            if read_time is not None and cleaned_body is not None:
                data["body"] = cleaned_body
                data["read_time"] = read_time
                output_path = os.path.join(output_dir_with, fname)
            else:
                output_path = os.path.join(output_dir_without, fname)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to process file '{fname}': {e}")


# Extracts the article content between "# min read" and "View Comments"
def extract_body_and_read_time(body):
    match = re.search(r'(\d+)\s*min read', body)
    if not match:
        return None, None
    read_time = int(match.group(1))
    start = match.end()
    end = body.find("View Comments", start)
    if end == -1:
        return None, None
    cleaned_body = body[start:end].strip()
    return read_time, cleaned_body

if __name__ == "__main__":
    main()
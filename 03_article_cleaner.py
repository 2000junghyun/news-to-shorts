import os
import json
import re
import shutil

DATE = "20250729"
INPUT_DIR = f'data/parsed-news/articles_full_{DATE}'
OUTPUT_DIR_WITH = f'data/with-form/articles_cleaned_{DATE}'
OUTPUT_DIR_WITHOUT = f'data/without-form/articles_full_{DATE}'

def main():
    try:
        classify_json_files(INPUT_DIR, OUTPUT_DIR_WITH, OUTPUT_DIR_WITHOUT)
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

    count_with = 0
    count_without = 0

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
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.remove(fpath)
                count_with += 1
            else:
                output_path = os.path.join(output_dir_without, fname)
                shutil.move(fpath, output_path)
                count_without += 1
        except Exception as e:
            print(f"[ERROR] Failed to process file '{fname}': {e}")

    print(f"[Complete] with-form: {count_with}, without-form: {count_without}")


def extract_body_and_read_time(body):
    match = re.search(r'(\d+)\s*min read', body)
    if not match:
        return None, None
    read_time = int(match.group(1))
    start = match.end()

    # 대소문자 구분 없이 찾기
    m = re.search(r'view comments', body[start:], re.IGNORECASE)
    if not m:
        return None, None
    end = start + m.start()
    cleaned_body = body[start:end].strip()
    return read_time, cleaned_body


if __name__ == "__main__":
    main()
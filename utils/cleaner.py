import os
import json
import shutil

def classify_json_files(input_dir, output_dir_with, output_dir_without):
    # 입력 디렉토리가 없으면 생성(빈 디렉토리이므로 분류 대상 없음)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir_with, exist_ok=True)
    os.makedirs(output_dir_without, exist_ok=True)
    files = [fname for fname in os.listdir(input_dir) if fname.endswith(".json")]
    if not files:
        print(f"[INFO] 입력 디렉토리({input_dir})에 json 파일이 없습니다.")
        return
    for fname in files:
        fpath = os.path.join(input_dir, fname)
        if has_article_section(fpath):
            shutil.copy2(fpath, os.path.join(output_dir_with, fname))
        else:
            shutil.copy2(fpath, os.path.join(output_dir_without, fname))

def has_article_section(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        body = data.get("body", "")
        return (
            "In This Article:" in body
            and "View Comments" in body
            and body.find("View Comments") > body.find("In This Article:")
        )
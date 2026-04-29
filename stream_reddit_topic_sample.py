import csv
import io
import json
import sys
from pathlib import Path

import requests
import zstandard as zstd


def clean_text(text):
    if text is None:
        return ""
    return str(text).replace("\n", " ").replace("\r", " ").strip()


def main():
    if len(sys.argv) < 6:
        print("Usage:")
        print('python stream_reddit_topic_sample.py <zst_url> <output_csv> <max_rows> <subreddit> <keywords_csv>')
        return

    url = sys.argv[1]
    output_path = Path(sys.argv[2])
    max_rows = int(sys.argv[3])
    target_subreddit = sys.argv[4].lower()
    keywords = [k.strip().lower() for k in sys.argv[5].split(",")]

    fields = [
        "id",
        "author",
        "subreddit",
        "body",
        "created_utc",
        "parent_id",
        "link_id",
        "score",
    ]

    print("Connecting to:")
    print(url)
    print(f"Target subreddit: {target_subreddit}")
    print(f"Keywords: {keywords}")
    print(f"Target rows: {max_rows}")

    count = 0
    seen_lines = 0

    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        response.raw.decode_content = True

        dctx = zstd.ZstdDecompressor(max_window_size=2**31)

        with dctx.stream_reader(response.raw) as reader:
            text_stream = io.TextIOWrapper(reader, encoding="utf-8", errors="replace")

            with open(output_path, "w", newline="", encoding="utf-8-sig") as out:
                writer = csv.DictWriter(out, fieldnames=fields)
                writer.writeheader()

                for line in text_stream:
                    seen_lines += 1

                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    author = clean_text(obj.get("author"))
                    subreddit = clean_text(obj.get("subreddit"))
                    body = clean_text(obj.get("body"))

                    if subreddit.lower() != target_subreddit:
                        continue

                    if not author or author in ["[deleted]", "AutoModerator"]:
                        continue

                    if not body or body in ["[deleted]", "[removed]"]:
                        continue

                    if len(body.split()) < 8:
                        continue

                    body_lower = body.lower()
                    if not any(keyword in body_lower for keyword in keywords):
                        continue

                    writer.writerow({
                        "id": clean_text(obj.get("id")),
                        "author": author,
                        "subreddit": subreddit,
                        "body": body,
                        "created_utc": clean_text(obj.get("created_utc")),
                        "parent_id": clean_text(obj.get("parent_id")),
                        "link_id": clean_text(obj.get("link_id")),
                        "score": clean_text(obj.get("score")),
                    })

                    count += 1

                    if count % 100 == 0:
                        print(f"Saved {count} rows...")

                    if count >= max_rows:
                        break

    print(f"Done. Scanned {seen_lines} lines.")
    print(f"Saved {count} rows to {output_path}")


if __name__ == "__main__":
    main()
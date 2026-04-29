import sys
import pandas as pd


def clean_text(text):
    if pd.isna(text):
        return ""
    return str(text).replace("\n", " ").replace("\r", " ").strip()


def main():
    input_csv = sys.argv[1] if len(sys.argv) > 1 else "reddit_comments_sample.csv"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "reddit_agents.csv"
    target_subreddit = sys.argv[3] if len(sys.argv) > 3 else "politics"
    num_agents = int(sys.argv[4]) if len(sys.argv) > 4 else 50

    df = pd.read_csv(input_csv)

    # 先只取某個 subreddit，避免主題太雜
    df = df[df["subreddit"].str.lower() == target_subreddit.lower()].copy()

    # 基本清理
    df["body"] = df["body"].apply(clean_text)
    df = df[df["author"].notna()]
    df = df[df["body"].str.split().str.len() >= 8]
    df = df[~df["author"].isin(["[deleted]", "AutoModerator"])]

    # 每個 author 只取一則代表性留言
    df = df.drop_duplicates(subset=["author"], keep="first")

    # 取前 num_agents 個使用者
    df = df.head(num_agents).copy()

    if len(df) == 0:
        print(f"No usable comments found for subreddit: {target_subreddit}")
        return

    # 這裡的 initial_belief 先只是佔位值
    # 之後真正做實驗時，要用人工標註 / LLM / stance model 轉成 -2 到 2
    df["agent_id"] = range(len(df))
    df["opinion_text"] = df["body"]
    df["initial_belief"] = 0

    output = df[[
        "agent_id",
        "author",
        "subreddit",
        "opinion_text",
        "initial_belief",
        "created_utc",
        "parent_id",
        "link_id",
        "score"
    ]]

    output.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"Saved {len(output)} agents to {output_csv}")
    print("Reminder: initial_belief is currently set to 0 as placeholder.")


if __name__ == "__main__":
    main()
import os
import random
from supabase import create_client, Client

# Supabase接続情報の取得
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    try:
        response = supabase.table("quiz").select("*").execute()
        rows = response.data
    except Exception as e:
        print(f"Supabase fetch error: {e}")
        rows = []

    if not rows:
        text = "【本日の看護師国家試験 対策】"
        html_content = "<p>本日の問題は準備中です。</p>"
    else:
        row = random.choice(rows)
        
        # X (Twitter) 用の投稿文面を作成
        text = (
            f"【本日の看護師国家試験 対策】\n"
            f"Q. {row.get('question', '')}\n\n"
            f"1️⃣ {row.get('choice1', '')}\n"
            f"2️⃣ {row.get('choice2', '')}\n"
            f"3️⃣ {row.get('choice3', '')}\n"
            f"4️⃣ {row.get('choice4', '')}\n"
            f"✨正解と解説はWebをチェック！\n"
            f"👇今日の問題と解説：https://daisukenishioka.github.io/X-auto-post/\n"
            f"#看護学生 #看護師国家試験 #第114回看護師国家試験"
        )

        # HTML用のコンテンツ作成
        html_content = f"""
        <h2>本日の問題</h2>
        <p><strong>{row.get('question', '')}</strong></p>
        <ul>
            <li>1. {row.get('choice1', '')}</li>
            <li>2. {row.get('choice2', '')}</li>
            <li>3. {row.get('choice3', '')}</li>
            <li>4. {row.get('choice4', '')}</li>
        </ul>
        <p><strong>正解:</strong> {row.get('answer', '')}</p>
        <p><strong>解説:</strong> {row.get('explanation', '')}</p>
        """

    # index.html の更新
    index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>看護師国家試験 過去問・解説</title>
</head>
<body>
    <h1>本日の看護師国家試験 対策</h1>
    {html_content}
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print("Successfully generated index.html")

if __name__ == "__main__":
    main()

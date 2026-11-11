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
            f"✨正解と解説はアプリをチェック！\n"
            f"👇今日の問題と解説：https://kanngosi-no-kokkasikenn-goukaku.ai.studio/\n"
            f"#看護学生 #看護師国家試験 #第116回看護師国家試験"
        )

        # HTML用のコンテンツ作成（アプリへの案内とリンクを追加）
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
        
        <hr style="margin: 20px 0;">
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 8px; text-align: center;">
            <p style="margin-bottom: 10px; font-weight: bold;">✨ 正解と解説をさらに詳しくチェック！</p>
            <a href="https://kanngosi-no-kokkasikenn-goukaku.ai.studio/" target="_blank" style="display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">看護師国家試験対策アプリを開く</a>
        </div>
        """

    # index.html の更新
    index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>看護師国家試験 過去問・解説</title>
</head>
<body style="font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; line-height: 1.6;">
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

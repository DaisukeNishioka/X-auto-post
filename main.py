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
        
        # 各データを取得（問題文は 'text'）
        q_text = row.get('text', '') or "（問題文が設定されていません）"
        c1 = row.get('choice1', '')
        c2 = row.get('choice2', '')
        c3 = row.get('choice3', '')
        c4 = row.get('choice4', '')
        ans = row.get('answer', '')
        exp = row.get('explanation', '')

        # X (Twitter) 用の投稿文面を作成
        text = (
            f"【本日の看護師国家試験 対策】\n"
            f"Q. {q_text}\n\n"
            f"{c1}\n"
            f"{c2}\n"
            f"{c3}\n"
            f"{c4}\n"
            f"✨正解と解説はアプリをチェック！\n"
            f"👇今日の問題と解説：https://kanngosi-no-kokkasikenn-goukaku.ai.studio/\n"
            f"#看護学生 #看護師国家試験 #第116回看護師国家試験"
        )

        # HTML用のコンテンツ作成
        html_content = f"""
        <h2>本日の問題</h2>
        <p style="font-size: 1.1em; font-weight: bold; margin-bottom: 20px;">{q_text}</p>
        
        <ul style="list-style-type: none; padding-left: 0; line-height: 2;">
            <li>{c1}</li>
            <li>{c2}</li>
            <li>{c3}</li>
            <li>{c4}</li>
        </ul>
        
        <div style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-left: 4px solid #007bff;">
            <p style="margin: 0 0 10px 0;"><strong>正解:</strong> {ans}</p>
            <p style="margin: 0;"><strong>解説:</strong> {exp}</p>
        </div>
        
        <hr style="margin: 30px 0;">
        <div style="background-color: #f0f8ff; padding: 20px; border-radius: 8px; text-align: center;">
            <p style="margin-bottom: 15px; font-weight: bold; color: #0056b3;">✨ 正解と解説をさらに詳しくチェック！</p>
            <a href="https://kanngosi-no-kokkasikenn-goukaku.ai.studio/" target="_blank" style="display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">看護師国家試験対策アプリを開く</a>
        </div>
        """

    # index.html の更新
    index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>看護師国家試験 過去問・解説</title>
</head>
<body style="font-family: sans-serif; max-width: 650px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #333;">
    <h1 style="border-bottom: 2px solid #007bff; padding-bottom: 10px; color: #007bff;">本日の看護師国家試験 対策</h1>
    {html_content}
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print("Successfully generated index.html")

if __name__ == "__main__":
    main()

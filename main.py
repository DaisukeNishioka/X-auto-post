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
        html_content = "<p>本日の問題は準備中です。</p>"
    else:
        row = random.choice(rows)
        
        # 取得したデータをそのままデバッグ表示する
        html_content = f"""
        <h2>【デバッグ情報】取得できたデータの中身</h2>
        <pre style="background: #eee; padding: 10px; overflow: auto;">{row}</pre>
        
        <hr style="margin: 20px 0;">
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 8px; text-align: center;">
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

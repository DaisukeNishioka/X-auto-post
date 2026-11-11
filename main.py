import os
import datetime
import random
import requests
from supabase import create_client, Client

# Supabaseの接続設定（環境変数から取得）
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 曜日に合わせたテーマの設定
WEEKDAY_CONFIG = {
    0: {"theme": "必修問題", "category": "hissyu"},
    1: {"theme": "一般問題", "category": "ippan"},
    2: {"theme": "状況設定問題", "category": "joukyou"},
    3: {"theme": "頻出数値", "category": "suuchi"},
    4: {"theme": "疾患まとめ", "category": "shikkan"},
    5: {"theme": "間違えやすい問題", "category": "machigai"},
    6: {"theme": "アプリ紹介", "category": "promo"}
}

def get_today_content():
    # 日本時間 (JST) での曜日を取得
    jst = datetime.timezone(datetime.timedelta(hours=9))
    today = datetime.datetime.now(jst)
    weekday = today.weekday() # 0:月, 1:火, ... 6:日
    
    config = WEEKDAY_CONFIG[weekday]
    
    if config["category"] == "promo":
        # 日曜日のアプリ紹介用テキスト
        text = (
            "【看護学生向けアプリのご紹介✨】\n"
            "毎日のスキマ時間で国試対策ができる「看護師国家試験 対策アプリ」配信中！\n\n"
            "📱 過去問演習・解説付き・苦手克服機能も搭載！\n"
            "▼ 今すぐ詳細をチェック\n"
            "https://daisukenishioka.github.io/X-auto-post/\n\n"
            "#看護学生 #看護師国家試験 #第116回看護師国家試験 #看護学生さんと繋がりたい"
        )
        html_content = "<h2>日曜特別企画：アプリのご紹介</h2><p>毎日のスキマ時間で国試対策を始めませんか？アプリの詳細や過去問演習はこちらから！</p>"
        return text, html_content

    else:
        # Supabaseから該当カテゴリの問題をフェッチ
        # ※Supabase側のテーブル名やカラム名（category, question, choice1〜4, answer, explanation）に合わせています
        try:
            response = supabase.table("questions").select("*").eq("category", config["category"]).execute()
            rows = response.data
        except Exception as e:
            print(f"Supabase fetch error: {e}")
            rows = []
            
        if not rows:
            # 万が一データが取れない場合のフォールバック
            text = f"【本日の看護師国家試験 対策（{config['theme']}）】\n本日の問題データ準備中です！\n#看護学生 #看護師国家試験"
            html_content = f"<p>{config['theme']}の問題は現在準備中です。</p>"
            return text, html_content
            
        # ランダムに1問選択
        row = random.choice(rows)
        
        # X（Twitter）用の投稿文面を作成
        text = (
            f"【本日の看護師国家試験 対策（{config['theme']}）】\n\n"
            f"{row.get('question', '')}\n\n"
            f"1️⃣ {row.get('choice1', '')}\n"
            f"2️⃣ {row.get('choice2', '')}\n"
            f"3️⃣ {row.get('choice3', '')}\n"
            f"4️⃣ {row.get('choice4', '')}\n\n"
            f"💡 正解と解説はWeb版をチェック！\n"
            f"🌐 今日の問題と解説：https://daisukenishioka.github.io/X-auto-post/\n\n"
            f"#看護学生 #看護師国家試験 #第116回看護師国家試験"
        )
        
        # HTML用のコンテンツ作成
        html_content = f"""
        <h2>【{config['theme']}】本日の問題</h2>
        <p class="question-text">{row.get('question', '')}</p>

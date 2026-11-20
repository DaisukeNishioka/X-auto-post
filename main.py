import base64
import hashlib
import hmac
import json
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from supabase import create_client, Client

# Supabase接続情報の取得
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# X API (OAuth 1.0a) 認証情報の取得
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def _percent_encode(value: str) -> str:
    return urllib.parse.quote(str(value), safe="~")


def _build_oauth1_header(
    method: str,
    url: str,
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
) -> str:
    oauth_params = {
        "oauth_consumer_key": api_key,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }

    sorted_params = sorted((_percent_encode(k), _percent_encode(v)) for k, v in oauth_params.items())
    param_string = "&".join(f"{k}={v}" for k, v in sorted_params)

    base_string = "&".join([
        _percent_encode(method.upper()),
        _percent_encode(url),
        _percent_encode(param_string),
    ])

    signing_key = f"{_percent_encode(api_secret)}&{_percent_encode(access_token_secret)}"
    signature = base64.b64encode(
        hmac.new(signing_key.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha1).digest()
    ).decode("utf-8")

    oauth_params["oauth_signature"] = signature
    header_parts = [f'{_percent_encode(k)}="{_percent_encode(v)}"' for k, v in sorted(oauth_params.items())]
    return "OAuth " + ", ".join(header_parts)


def post_to_x(text: str) -> None:
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        print("X API credentials are not set. Skipping X post.")
        return

    url = "https://api.x.com/2/tweets"
    auth_header = _build_oauth1_header(
        method="POST",
        url=url,
        api_key=X_API_KEY,
        api_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
    )

    payload = json.dumps({"text": text}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=payload,
        method="POST",
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "User-Agent": "NursingExamBot/1.0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            print(f"Successfully posted to X (status {resp.status}): {body}")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"X API HTTP error ({e.code}): {err_body}")
    except Exception as e:
        print(f"X API request failed: {e}")


def build_x_text(q_text: str, c1: str, c2: str, c3: str, c4: str) -> str:
    footer = (
        "\n✨正解と解説はアプリをチェック！\n"
        "👇今日の問題と解説：https://kanngosi-no-kokkasikenn-goukaku.ai.studio/\n"
        "#看護学生 #看護師国家試験 #第116回看護師国家試験"
    )
    choices_block = f"{c1}\n{c2}\n{c3}\n{c4}\n"
    header = "【本日の看護師国家試験 対策】\nQ. "

    full_text = f"{header}{q_text}\n\n{choices_block}{footer}"
    if len(full_text) > 135:
        available_for_q = max(25, 135 - len(header) - len("\n\n") - len(choices_block) - len(footer) - 1)
        trimmed_q = q_text[:available_for_q] + "…" if len(q_text) > available_for_q else q_text
        full_text = f"{header}{trimmed_q}\n\n{choices_block}{footer}"
        if len(full_text) > 138:
            short_q = q_text[:55] + "…" if len(q_text) > 55 else q_text
            full_text = (
                f"【本日の看護師国家試験 対策】\n"
                f"Q. {short_q}\n"
                f"👇解説・選択肢：https://kanngosi-no-kokkasikenn-goukaku.ai.studio/\n"
                f"#看護学生 #看護師国家試験"
            )
    return full_text


def main():
    try:
        response = supabase.table("quiz").select("*").execute()
        rows = response.data
    except Exception as e:
        print(f"Supabase fetch error: {e}")
        rows = []

    if not rows:
        text = "【本日の看護師国家試験 対策】\n#看護学生 #看護師国家試験"
        html_content = "<p>本日の問題は準備中です。</p>"
    else:
        row = random.choice(rows)

        q_text = row.get("text", "") or "（問題文が設定されていません）"
        c1 = row.get("choice1", "")
        c2 = row.get("choice2", "")
        c3 = row.get("choice3", "")
        c4 = row.get("choice4", "")
        ans = row.get("answer", "")
        exp = row.get("explanation", "")

        text = build_x_text(q_text, c1, c2, c3, c4)

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

    index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>看護師国家試験 過去問・解説</title>
</head>
<body style="font-family:

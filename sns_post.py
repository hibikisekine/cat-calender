"""
X (Twitter) 自動投稿スクリプト
毎日ランダムな猫の写真と癒やしのメッセージを投稿します。

必要な環境変数:
  TWITTER_API_KEY          - Twitter API Key
  TWITTER_API_SECRET       - Twitter API Secret
  TWITTER_ACCESS_TOKEN     - Twitter Access Token
  TWITTER_ACCESS_SECRET    - Twitter Access Token Secret
  SITE_URL                 - サイトURL (デフォルト: https://cat-calender.onrender.com)
"""

import os
import sys
import glob
import random
import sqlite3
from datetime import date

import tweepy

# Twitter API 認証情報
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')

SITE_URL = os.environ.get('SITE_URL', 'https://cat-calender.onrender.com')

# 癒やしの言葉リスト（app.py と同じ）
HEALING_MESSAGES = [
    "今日も一日お疲れ様でした。",
    "小さな幸せを見つける心の余裕を持ちましょう。",
    "深呼吸して、今この瞬間を大切に。",
    "あなたの笑顔が誰かを幸せにしています。",
    "完璧でなくても大丈夫。そのままのあなたで素晴らしい。",
    "一歩一歩、着実に進んでいきましょう。",
    "今日のあなたは昨日のあなたより成長しています。",
    "心の声に耳を傾けてみましょう。",
    "自然の美しさに心を癒されましょう。",
    "感謝の気持ちを忘れずに。",
    "新しい一日の始まりを楽しみましょう。",
    "あなたの存在が世界をより良くしています。",
    "心の奥にある優しさを大切に。",
    "今日も素敵な一日になりますように。",
    "小さな進歩も大きな喜びです。",
    "自分を信じて、前に進みましょう。",
    "心の平安を大切にしましょう。",
    "今日も頑張った自分を褒めてあげて。",
    "明日への希望を胸に抱いて。",
    "あなたの時間は大切です。",
    "心の声に従って、自分らしく生きましょう。",
    "今日も素晴らしい発見がありますように。",
    "あなたの優しさが世界を変えています。",
    "一呼吸置いて、心を落ち着かせましょう。",
    "今日も新しい学びがありますように。",
    "あなたの努力は必ず実を結びます。",
    "心の奥にある光を大切に。",
    "今日も素敵な出会いがありますように。",
    "自分を愛することを忘れずに。",
]


def get_message():
    """メッセージを取得（DBがあればユーザーメッセージを優先）"""
    db_path = os.path.join(os.path.dirname(__file__), 'calendar.db')
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('SELECT message FROM user_messages')
            user_messages = [row[0] for row in c.fetchall()]
            conn.close()
            if user_messages:
                return random.choice(user_messages)
        except Exception:
            pass
    return random.choice(HEALING_MESSAGES)


def get_random_image():
    """ランダムな猫の画像ファイルパスを取得"""
    upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    extensions = ('*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp',
                  '*.PNG', '*.JPG', '*.JPEG', '*.GIF', '*.WEBP')
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(upload_dir, ext)))
    # 重複除去
    images = list(set(images))
    if not images:
        print("エラー: 画像が見つかりません。static/uploads/ に画像を追加してください。")
        sys.exit(1)
    return random.choice(images)


def build_tweet_text(message):
    """ツイートのテキストを組み立てる"""
    today = date.today()
    date_str = f"{today.year}年{today.month}月{today.day}日"

    tweet = (
        f"{date_str} 今日の猫カレンダー\n"
        f"\n"
        f"{message}\n"
        f"\n"
        f"#猫 #ねこ #猫好きさんと繋がりたい #日めくりカレンダー #猫のいる暮らし\n"
        f"\n"
        f"{SITE_URL}"
    )
    return tweet


def post_to_twitter(tweet_text, image_path):
    """X (Twitter) に画像付きツイートを投稿"""
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        print("エラー: Twitter API の環境変数が設定されていません。")
        print("以下の環境変数を設定してください:")
        print("  TWITTER_API_KEY")
        print("  TWITTER_API_SECRET")
        print("  TWITTER_ACCESS_TOKEN")
        print("  TWITTER_ACCESS_SECRET")
        sys.exit(1)

    # API v1.1 (メディアアップロード用)
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY, TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
    )
    api_v1 = tweepy.API(auth)

    # API v2 (ツイート投稿用)
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET,
    )

    # 画像をアップロード
    print(f"画像をアップロード中: {os.path.basename(image_path)}")
    media = api_v1.media_upload(filename=image_path)

    # ツイートを投稿
    print("ツイートを投稿中...")
    response = client.create_tweet(text=tweet_text, media_ids=[media.media_id])

    tweet_id = response.data['id']
    print(f"投稿完了! https://twitter.com/i/web/status/{tweet_id}")
    return tweet_id


def main():
    print("=== 猫カレンダー SNS自動投稿 ===")

    # ランダムな画像とメッセージを取得
    image_path = get_random_image()
    message = get_message()
    tweet_text = build_tweet_text(message)

    print(f"画像: {os.path.basename(image_path)}")
    print(f"メッセージ: {message}")
    print(f"---")
    print(tweet_text)
    print(f"---")

    # --dry-run オプションで実際に投稿しない
    if '--dry-run' in sys.argv:
        print("[dry-run] 投稿をスキップしました。")
        return

    post_to_twitter(tweet_text, image_path)


if __name__ == '__main__':
    main()

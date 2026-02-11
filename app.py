from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import random
import sqlite3
from datetime import datetime, date
from werkzeug.utils import secure_filename
import json
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# 設定
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# AmazonアソシエイトID（環境変数から取得）
AMAZON_ASSOCIATE_ID = os.environ.get('AMAZON_ASSOCIATE_ID', 'mjmg-22')

# Google AdSense パブリッシャーID（環境変数から取得）
ADSENSE_PUB_ID = os.environ.get('ADSENSE_PUB_ID', 'ca-pub-7310204683723531')
ADSENSE_AD_SLOT = os.environ.get('ADSENSE_AD_SLOT', '')

# アップロードフォルダを作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 癒やしの言葉リスト
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
    "自分を愛することを忘れずに。"
]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('calendar.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS photos
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         filename TEXT NOT NULL,
         original_name TEXT NOT NULL,
         upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_messages
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         date TEXT UNIQUE NOT NULL,
         message TEXT NOT NULL)
    ''')

    # ユーザーアップロード用の一言メッセージテーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_messages
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         message TEXT NOT NULL,
         upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')

    # 猫のイラスト用のテーブル（ユーザーアップロード用）
    c.execute('''
        CREATE TABLE IF NOT EXISTS cat_illustrations
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         filename TEXT NOT NULL,
         original_name TEXT NOT NULL,
         upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')

    conn.commit()
    conn.close()

def get_todays_message():
    today = date.today().isoformat()
    conn = sqlite3.connect('calendar.db')
    c = conn.cursor()

    # 今日のメッセージを取得
    c.execute('SELECT message FROM daily_messages WHERE date = ?', (today,))
    result = c.fetchone()

    if result:
        message = result[0]
    else:
        # 新しいメッセージを生成（日付に基づいて決定）
        day_of_year = date.today().timetuple().tm_yday
        message = HEALING_MESSAGES[day_of_year % len(HEALING_MESSAGES)]

        # データベースに保存
        c.execute('INSERT INTO daily_messages (date, message) VALUES (?, ?)', (today, message))
        conn.commit()

    conn.close()
    return message

def get_random_message():
    """ランダムなメッセージを取得（ユーザーメッセージを優先）"""
    conn = sqlite3.connect('calendar.db')
    c = conn.cursor()

    # ユーザーメッセージ（猫の格言）を取得
    c.execute('SELECT message FROM user_messages')
    user_messages = [row[0] for row in c.fetchall()]

    conn.close()

    # ユーザーメッセージがある場合はそれを使用、ない場合はシステムメッセージ
    if user_messages:
        return random.choice(user_messages)
    else:
        # フォールバック用のシステムメッセージ
        return random.choice(HEALING_MESSAGES)

def get_random_cat_illustration():
    """ランダムな猫の写真を取得（cat_illustrations + photos の両方から）"""
    conn = sqlite3.connect('calendar.db')
    c = conn.cursor()

    # cat_illustrations と photos の両方からランダムに1枚取得
    c.execute('''
        SELECT filename, original_name FROM (
            SELECT filename, original_name FROM cat_illustrations
            UNION ALL
            SELECT filename, original_name FROM photos
        ) ORDER BY RANDOM() LIMIT 1
    ''')
    result = c.fetchone()

    conn.close()

    if result:
        return {
            'filename': result[0],
            'original_name': result[1]
        }
    else:
        return None

def get_affiliate_url(url):
    """AmazonアソシエイトIDをURLに追加"""
    if not AMAZON_ASSOCIATE_ID:
        return url

    # amzn.toの短縮URLは既にアソシエイトIDが含まれている可能性があるため、そのまま返す
    if 'amzn.to' in url:
        return url

    # amazon.co.jpのURLにアソシエイトIDを追加
    if 'amazon.co.jp' in url:
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            query_params['tag'] = [AMAZON_ASSOCIATE_ID]
            new_query = urlencode(query_params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            return urlunparse(new_parsed)
        except Exception:
            # URL解析に失敗した場合は、クエリパラメータとして追加
            separator = '&' if '?' in url else '?'
            return f"{url}{separator}tag={AMAZON_ASSOCIATE_ID}"

    return url

@app.route('/')
def index():
    # ランダムなメッセージを取得
    random_message = get_random_message()

    # ランダムな猫のイラストを取得
    cat_illustration = get_random_cat_illustration()

    # アフィリエイトリンクを生成
    affiliate_links = {
        'pet_food': get_affiliate_url('https://amzn.to/4pfUA2N'),
        'toys': get_affiliate_url('https://www.amazon.co.jp/s?k=猫+おもちゃ&rh=n%3A2275256051'),
        'bed': get_affiliate_url('https://www.amazon.co.jp/s?k=猫+ベッド&rh=n%3A2275256051'),
        'litter': get_affiliate_url('https://www.amazon.co.jp/s?k=猫+トイレ&rh=n%3A2275256051'),
        'carrier': get_affiliate_url('https://www.amazon.co.jp/s?k=猫+キャリーケース&rh=n%3A2275256051'),
        'scratch': get_affiliate_url('https://www.amazon.co.jp/s?k=猫+爪とぎ&rh=n%3A2275256051'),
        'bowl': get_affiliate_url('https://www.amazon.co.jp/s?k=猫+食器&rh=n%3A2275256051'),
        'cat_tree': get_affiliate_url('https://www.amazon.co.jp/s?k=キャットタワー&rh=n%3A2275256051'),
        'all_products': get_affiliate_url('https://www.amazon.co.jp/s?k=猫+用品'),
    }

    return render_template('index.html',
                         cat_illustration=cat_illustration,
                         message=random_message,
                         amazon_associate_id=AMAZON_ASSOCIATE_ID,
                         affiliate_links=affiliate_links,
                         adsense_pub_id=ADSENSE_PUB_ID,
                         adsense_ad_slot=ADSENSE_AD_SLOT)

@app.route('/ads.txt')
def serve_ads_txt():
    """AdSense所有権確認用のads.txtファイル"""
    return app.send_static_file('ads.txt')

@app.route('/manifest.json')
def serve_manifest():
    """PWAマニフェストファイル"""
    return app.send_static_file('manifest.json')

@app.route('/sw.js')
def serve_sw():
    """Service Workerファイル（ルートスコープで配信）"""
    return app.send_static_file('sw.js')

@app.route('/privacy')
def privacy():
    """プライバシーポリシーページ"""
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    """利用規約ページ"""
    return render_template('terms.html')

@app.route('/upload', methods=['GET'])
def upload_photo():
    """写真アップロードページ"""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_photo_post():
    """写真アップロード処理"""
    if 'photo' not in request.files:
        flash('ファイルが選択されていません。')
        return redirect(url_for('upload_photo'))

    file = request.files['photo']

    if file.filename == '':
        flash('ファイルが選択されていません。')
        return redirect(url_for('upload_photo'))

    if not allowed_file(file.filename):
        flash('対応していないファイル形式です。PNG, JPG, JPEG, GIF, WebPのみ対応しています。')
        return redirect(url_for('upload_photo'))

    filename = secure_filename(file.filename)
    # ファイル名の重複を防ぐためタイムスタンプを付与
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    safe_filename = timestamp + filename

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    file.save(filepath)

    # データベースに保存
    conn = sqlite3.connect('calendar.db')
    c = conn.cursor()
    c.execute('INSERT INTO photos (filename, original_name) VALUES (?, ?)',
              (safe_filename, file.filename))
    conn.commit()
    conn.close()

    flash('写真をアップロードしました。')
    return redirect(url_for('view_photos'))

@app.route('/photos')
def view_photos():
    """写真一覧ページ"""
    conn = sqlite3.connect('calendar.db')
    c = conn.cursor()
    c.execute('SELECT id, filename, original_name, upload_date FROM photos ORDER BY upload_date DESC')
    photos = c.fetchall()
    conn.close()
    return render_template('photos.html', photos=photos)

@app.route('/delete_photo/<int:photo_id>', methods=['POST'])
def delete_photo(photo_id):
    """写真削除処理"""
    conn = sqlite3.connect('calendar.db')
    c = conn.cursor()

    # 写真情報を取得
    c.execute('SELECT filename FROM photos WHERE id = ?', (photo_id,))
    result = c.fetchone()

    if result:
        filename = result[0]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # ファイルを削除
        if os.path.exists(filepath):
            os.remove(filepath)

        # データベースから削除
        c.execute('DELETE FROM photos WHERE id = ?', (photo_id,))
        conn.commit()
        flash('写真を削除しました。')
    else:
        flash('写真が見つかりませんでした。')

    conn.close()
    return redirect(url_for('view_photos'))

@app.route('/api/random_content')
def api_random_content():
    """ランダムなコンテンツ（猫のイラスト + メッセージ）を取得"""
    cat_illustration = get_random_cat_illustration()
    message = get_random_message()

    return jsonify({
        'cat_illustration': cat_illustration,
        'message': message
    })

# DB初期化
init_db()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)

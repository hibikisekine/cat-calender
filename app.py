from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import random
import sqlite3
from datetime import datetime, date
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 設定
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    """ランダムな猫のイラストを取得"""
    conn = sqlite3.connect('calendar.db')
    c = conn.cursor()
    
    # 猫のイラストを取得
    c.execute('SELECT filename, original_name FROM cat_illustrations ORDER BY RANDOM() LIMIT 1')
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return {
            'filename': result[0],
            'original_name': result[1]
        }
    else:
        return None

@app.route('/')
def index():
    # ランダムなメッセージを取得
    random_message = get_random_message()
    
    # ランダムな猫のイラストを取得
    cat_illustration = get_random_cat_illustration()
    
    return render_template('index.html', 
                         cat_illustration=cat_illustration, 
                         message=random_message)

@app.route('/privacy')
def privacy():
    """プライバシーポリシーページ"""
    return render_template('privacy.html')

@app.route('/api/random_content')
def api_random_content():
    """ランダムなコンテンツ（猫のイラスト + メッセージ）を取得"""
    cat_illustration = get_random_cat_illustration()
    message = get_random_message()
    
    return jsonify({
        'cat_illustration': cat_illustration,
        'message': message
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8080) 
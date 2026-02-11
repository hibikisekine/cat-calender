# X (Twitter) API 設定手順

猫カレンダーの自動投稿を有効にするための手順です。

## 1. Twitter Developer アカウントの作成

1. [Twitter Developer Portal](https://developer.twitter.com/) にアクセス
2. 「Sign up」から開発者アカウントを申請
3. **Free プラン**で十分です（月1,500ツイートまで投稿可能）

## 2. アプリの作成と API キーの取得

1. Developer Portal で「Projects & Apps」→「+ Add App」
2. アプリ名: `cat-calendar-bot`（任意の名前）
3. 以下の4つのキーをメモしてください:
   - **API Key** (Consumer Key)
   - **API Key Secret** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**

### 重要: アプリの権限設定

1. App Settings → 「User authentication settings」→「Set up」
2. **App permissions** を **Read and Write** に設定
3. 保存後、Access Token を**再生成**してください（権限変更後は再生成が必要）

## 3. GitHub Secrets に登録

GitHub リポジトリで以下の手順を実行:

1. リポジトリの「Settings」→「Secrets and variables」→「Actions」
2. 「New repository secret」から以下を追加:

| Secret 名 | 値 |
|---|---|
| `TWITTER_API_KEY` | API Key |
| `TWITTER_API_SECRET` | API Key Secret |
| `TWITTER_ACCESS_TOKEN` | Access Token |
| `TWITTER_ACCESS_SECRET` | Access Token Secret |

## 4. 動作確認

### ローカルでテスト（投稿しない）

```bash
python sns_post.py --dry-run
```

### ローカルで実際に投稿

```bash
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export TWITTER_ACCESS_TOKEN="your_access_token"
export TWITTER_ACCESS_SECRET="your_access_secret"
python sns_post.py
```

### GitHub Actions から手動実行

1. リポジトリの「Actions」タブ
2. 「毎日の猫カレンダー投稿」ワークフローを選択
3. 「Run workflow」ボタンをクリック

## 5. 自動投稿スケジュール

- **毎日 朝7:00（日本時間）** に自動投稿されます
- GitHub Actions の `workflow_dispatch` で手動実行も可能です

## 投稿内容の例

```
2026年2月11日 今日の猫カレンダー

今日も素敵な一日になりますように。

#猫 #ねこ #猫好きさんと繋がりたい #日めくりカレンダー #猫のいる暮らし

https://cat-calender.onrender.com
```

（ランダムな猫の写真が添付されます）

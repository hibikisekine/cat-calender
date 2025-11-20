# 🛒 Amazonアソシエイト設定手順（猫日めくりカレンダー）

## あなたのアソシエイトID

**アソシエイトID**: `mjmg-22`

## Renderで環境変数を設定

### ステップ1: Renderダッシュボードにログイン

1. https://dashboard.render.com にアクセス
2. プロジェクト `cat-calendar` を選択

### ステップ2: 環境変数を追加

1. **「Environment」タブを開く**

2. **環境変数を追加**
   - **Key**: `AMAZON_ASSOCIATE_ID`
   - **Value**: `mjmg-22`
   - 「Save Changes」をクリック

### ステップ3: 再デプロイ

1. **「Manual Deploy」をクリック**
2. **「Deploy latest commit」を選択**
3. 再デプロイが開始されます（5-10分）

## 動作確認

デプロイ完了後：

1. **サイトにアクセス**
   - https://cat-calender.onrender.com にアクセス

2. **アフィリエイトリンクを確認**
   - 「🐾 猫ちゃんのためのおすすめ商品」セクションを確認
   - 「🍽️ ペットフードを見る」リンクをクリック
   - リンクを右クリック → 「リンクのアドレスをコピー」
   - URLに `tag=mjmg-22` が含まれているか確認

## 現在のアフィリエイトリンク

以下の商品へのリンクが設定されています：

- **ペットフード**: https://amzn.to/4pfUA2N
  - このURLは短縮URLですが、環境変数で設定したアソシエイトIDが適用されます

## リンクの形式

環境変数が設定されると、以下のようにURLに自動的にアソシエイトIDが追加されます：

**短縮URLの場合:**
```
https://amzn.to/4pfUA2N
→ そのまま使用（amzn.toの短縮URLは既にアソシエイトIDが含まれている可能性があります）
```

**通常のAmazonリンクの場合:**
```
https://www.amazon.co.jp/s?k=ペットフード
→ https://www.amazon.co.jp/s?k=ペットフード&tag=mjmg-22
```

## 収益の確認

1. **Amazonアソシエイト・セントラルにログイン**
   - https://affiliate.amazon.co.jp/ にアクセス

2. **「レポート」→「売上レポート」を確認**
   - クリック数、注文数、売上高が表示されます

## 注意事項

- **審査が必要**: Amazonアソシエイトの審査を通過する必要があります
- **利用規約を遵守**: Amazonアソシエイトの利用規約に従ってください
- **プライバシーポリシー**: アフィリエイトリンクを使用する場合、プライバシーポリシーに記載する必要があります（既に追加済み）
- **リンクの明示**: `rel="sponsored"` 属性が設定されています

## トラブルシューティング

### アソシエイトIDが反映されない

1. **環境変数が正しく設定されているか確認**
   - Renderダッシュボードで `AMAZON_ASSOCIATE_ID` が設定されているか
   - 値が正しいか（`mjmg-22`）

2. **再デプロイを実行**
   - 環境変数を設定した後、必ず再デプロイが必要です

3. **ブラウザのキャッシュをクリア**
   - ブラウザのキャッシュをクリアして再読み込み

4. **ログを確認**
   - Renderの「Logs」タブでエラーがないか確認

## 参考

- [Amazonアソシエイト公式サイト](https://affiliate.amazon.co.jp/)
- [Amazonアソシエイト利用規約](https://affiliate.amazon.co.jp/help/operating/policies)
- [Render環境変数設定ガイド](https://render.com/docs/environment-variables)


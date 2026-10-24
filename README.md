# NEWS RADAR / ニュース・レーダー

日本語ニュースを一覧・読み上げ・掲示板表示するブラウザアプリです。GitHub Pages の静的ホスティングを使用します。

## しくみ

- GitHub Actions が10分間隔を目標に各公開RSSを取得し、`data/news.json` を更新します（GitHubのスケジュール実行には遅延があります）。
- GitHub Pages では `main` ブランチのルート `/` を公開します。
- 画面は5分ごとに最新のJSONを再取得し、ブラウザで既読やお気に入りを保存します。
- APIキー・DB・独自サーバーは不要です。英語のHacker Newsは任意の表示です。
- 公開版は各記事へのリンクを中心に、見出し・出典・記事リンクのみ表示します。RSS本文や概要の転載は行いません。各RSSの利用条件を確認し、必要なら配信元を除外してください。

## 初期設定

1. Settings > Pages > Build and deployment > Deploy from a branch を選びます。
2. Branch は `main`、folder は `/(root)` を選び保存します。
3. Actions > Update Japanese news > Run workflow で最初の更新を行えます。
4. Settings > Actions > General > Workflow permissions で実行に必要な書き込み許可があることを確認します。

GitHub Pages は動的サーバーを実行しません。元のSites版の `/api/rss` は使わず、Actions が生成した静的JSONを読みます。

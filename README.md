# NEWS RADAR / ニュース・レーダー

日本語ニュースを一覧・読み上げ・掲示板表示するブラウザアプリです。GitHub Pages の静的ホスティングを使用します。

## しくみ

- GitHub Actions が10分間隔を目標に各公開RSSを取得し、`data/news.json` を更新します（GitHubのスケジュール実行には遅延があります）。
- GitHub Pages では `main` ブランチのルート `/` を公開します。
- 画面は5分ごとに最新のJSONを再取得し、ブラウザで既読やお気に入りを保存します。
- APIキー・DB・独自サーバーは不要です。英語のHacker Newsは任意の表示です。
- ニュース本文は転載せず、見出し・RSSに含まれる短い概要・出典・記事リンクを表示します。各RSSの利用条件を守ってください。

## 初期設定

1. Settings > Pages > Build and deployment > Deploy from a branch を選びます。
2. Branch は `main`、folder は `/(root)` を選び保存します。
3. Actions > Update Japanese news > Run workflow で最初の更新を行えます。
4. Settings > Actions > General > Workflow permissions で実行に必要な書き込み許可があることを確認します。

GitHub Pages は動的サーバーを実行しません。元のSites版の `/api/rss` は使わず、Actions が生成した静的JSONを読みます。

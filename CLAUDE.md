# NBA Dashboard

海外NBAアナリストの分析・ニュースを自動収集し日本語で表示するダッシュボード。

## プロジェクト構成
- `src/config.py` — 設定（チーム定義、APIエンドポイント、テーマ）
- `src/collectors/` — NBA API からのデータ収集
- `src/analyzers/` — スタッツ分析・リーダー抽出
- `src/builder.py` — メインエントリ: 収集 → 分析 → HTML生成
- `templates/index.html` — Jinja2テンプレート
- `assets/` — CSS, JS
- `docs/` — GitHub Pages 出力先

## 実行方法
```bash
python src/builder.py
```

## 技術スタック
- Python 3.9+
- requests + Jinja2 のみ
- NBA.com API 直接呼び出し（nba_api パッケージ不使用）

## コーディング規約
- 変数名・コメント・コミットメッセージは英語
- ドキュメントは日本語
- シンプルさ重視、過剰な抽象化を避ける

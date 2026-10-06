# stock_analysis

ChatGPT Workでの株式分析・討議用リポジトリです。分析手法は`finance/`、必要時だけ最新の提出書類を確認するEDINET DB接続は`edinet/`に分離しています。

## 基本運用

通常は、ChatGPT Workで`CHATGPT_WORK.md`と`finance/`内の該当する`SKILL.md`を参照し、既存の資料・仮説・分析結果を討議します。EDINET DBへの問い合わせは、最新の有価証券報告書、四半期報告書、訂正書類などの根拠が必要なときだけ行います。

このリポジトリは定期実行、データ同期、取得データの自動コミットを行いません。取得結果は標準出力にJSONで返されるため、必要な結果だけを討議の入力にできます。

## EDINET DBを必要時に使う

1. 実行する端末または安全な実行環境で、`EDINET_DB_API_KEY`を環境変数として設定します。キーをGit、ChatGPT Work、レポート、端末上の`.env`へ保存しません。
2. EDINETコードと確認したい起点日を指定して実行します。

```bash
python3 edinet/edinet_db.py --company E00026 --published-after 2026-01-01
```

3. 出力JSONの`documents`をChatGPT Workの討議に渡します。PDFの署名付きURLも必要なときだけ`--with-pdf-url`を付けます。

```bash
python3 edinet/edinet_db.py --company E00026 --published-after 2026-01-01 --with-pdf-url
```

APIキーが未設定の場合、クライアントは通信せずに終了します。詳細は[edinet/README.md](edinet/README.md)を参照してください。

## 構成

| パス | 用途 |
| --- | --- |
| `finance/` | 株式分析・バリュエーション・マクロ・定量分析のプロンプトと補助スクリプト |
| `edinet/` | 必要時だけEDINET DBから開示資料メタデータとPDF参照URLを取得するCLI |
| `CHATGPT_WORK.md` | ChatGPT Workでの討議時に守る根拠・鮮度・出力の約束 |

## 境界

GitHubをChatGPT Workが読むことと、外部APIを実行することは別です。ChatGPT WorkのGitHub参照だけでは、秘密値を使ったEDINET DB APIの呼び出しは行いません。最新開示が必要なときのみ、認証済みの実行環境で上記CLIを実行し、その結果を討議に加えます。

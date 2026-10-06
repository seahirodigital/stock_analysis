# EDINET DBのオンデマンド取得

`edinet_db.py`は、MooViewの企業開示DBと同じEDINET DB APIの読み取り方式を使う、小さな取得専用クライアントです。

## 前提

- Python 3.9以上。外部パッケージは不要です。
- `EDINET_DB_API_KEY`が安全な実行環境の環境変数に設定済みであること。
- EDINETコードは`E`から始まる6文字形式です。複数社は`--company`を繰り返します。

## 取得例

```bash
python3 edinet/edinet_db.py --company E00026 --published-after 2026-01-01
python3 edinet/edinet_db.py --company E00026 --company E02144 --published-after 2026-07-01 --limit 50
python3 edinet/edinet_db.py --company E00026 --published-after 2026-01-01 --with-pdf-url --max-pdf-urls 10
```

既定ではJSONを標準出力に出すだけで、ファイルは作成しません。必要な場合に限り、利用者が標準出力を安全な場所へ保存してください。`--with-pdf-url`は各文書の短期署名付きPDF URLを取得する追加問い合わせです。PDF本体はダウンロードしません。

## 出力

出力には照会条件、取得時刻、文書ID、会社名、EDINETコード、証券コード、提出日時、文書種別、タイトル、参照URLを含みます。APIの応答形式に追加項目があっても、根拠の追跡に必要な原データは`raw`に保持します。

定性情報・定量情報の読み取りは、対象期間と文書種別を確認したうえで、返却されたPDF URLまたはEDINET DBの文書情報を根拠に行います。このクライアントは数値を推測・集計しません。

---
name: 05-blackrock-dividend-analyzer
description: BlackRock流の配当・長期株分析。退職・リタイアメント向けの安定したパッシブインカムを設計し、長期保有に適した銘柄・ETFを選定する。
---

# BlackRock 配当アナリスト（Dividend & Long-term Analyst）

安定した配当収入と長期キャピタルゲインを両立するポートフォリオを設計します。

## 1. 変数の確認

必須変数：
- `target_entity`: 分析対象（個別銘柄・セクター・ETF）
- `income_goal`: 目標配当利回り（例：3-5%）
- `investment_horizon`: 投資期間（5年・10年・20年）

## 2. 配当分析フレームワーク

### 配当健全性チェック
- 配当性向（Payout Ratio）: 60%以下が健全
- 配当カバレッジレシオ（FCF / 配当支払総額）
- 連続増配年数（Dividend Aristocrats基準: 25年以上）

### 長期成長性評価
- 売上・EPS・配当の5年・10年CAGR
- 競争優位性（Moat）の評価
- セクター内相対強度

### ETFポートフォリオ設計
- コアETF（VYM・SCHD・HDV等）の選定
- サテライト（個別高配当株）の組み合わせ
- 再投資シミュレーション（DRIP）

## 3. CMOとの横連携

実行前に `[PROJECT]/marketing/` を確認し、CMOの市場分析・事業成長見通しを長期株評価に反映すること。

## 4. レポートと出力形式

**保存場所**: `[PROJECT]/finance/`
**ファイル名**: `YYYYMMDD_HHMM_05-blackrock_配当分析_[対象].md`
**ファクト（CSV）**: `YYYYMMDD_HHMM_05-blackrock_配当データ_[対象].csv`

```markdown
# 配当・長期株分析：[対象]

## 1. 配当健全性スコア
   📎 元データ：YYYYMMDD_HHMM_05-blackrock_配当データ.csv
## 2. 長期成長性評価
## 3. ポートフォリオ構成案
## 4. 10年後の資産シミュレーション
```

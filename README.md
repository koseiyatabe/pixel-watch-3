
# Pixel Watch 3 ページ監視（GitHub Actions + Python）

SoftBank の Pixel Watch 3 商品ページに変更があったら **Gmail** へメール通知します。

## 使い方（概要）
1. このフォルダを GitHub の新規リポジトリへ push
2. リポジトリの **Settings > Secrets and variables > Actions > New repository secret** で以下を追加
   - `SMTP_USER` : 送信に使う Gmail アドレス（例: `you@gmail.com`）
   - `SMTP_PASS` : Gmail の **アプリ パスワード**（2段階認証の有効化が必要）
   - `TO_EMAIL`  : 通知を受け取るメール（自分宛でOK）
3. （任意）監視対象や CSS セレクタ、実行頻度は `monitor.yml` の環境変数や cron を編集
4. `Actions` タブで手動実行（`Run workflow`）して動作確認

## Gmail のアプリ パスワード発行
- Google アカウントで **2段階認証**を有効化
- セキュリティ > アプリ パスワード > 「メール」「その他」などを選び発行
- 生成された 16 文字を `SMTP_PASS` に保存

## 監視範囲の絞り込み（任意）
`CSS_SELECTOR` に CSS セレクタ（例: `main`, `.p-productDetail__detail` など）を入れると、その要素だけを比較します。
未設定ならページ全体のテキストを比較します。

## スケジュール（日本時間）
`cron: "0 0 * * *"` は **UTC 0:00** なので **JST 9:00** に相当します。毎朝9時にチェックしたければこのままでOK。
別の時刻にしたい場合は `monitor.yml` の `cron` を変更してください。

---

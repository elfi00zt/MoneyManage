# まねまね(MoneyManage) 公式サイト

公開中: https://elfi00zt.github.io/MoneyManage/

Windows 用家計簿アプリ「まねまね(MoneyManage)」の紹介・ダウンロード用の静的サイトです。
GitHub Pages でそのまま公開できます（ビルド不要・フレームワークなし）。

## 構成

```
index.html            トップ（特長・画面・はじめかた・ダウンロード・更新履歴・FAQ）
guide.html            使い方
404.html              ページが見つからないとき
assets/css/style.css  デザイン（色・余白・文字サイズは先頭の変数で管理）
assets/js/site-config.js  サイトの設定（バージョン・ダウンロード先・更新履歴など）
assets/js/main.js     設定の反映、メニュー、画像の拡大表示
assets/img/           アイコン・スクリーンショット・OGP 画像
tools/                スクリーンショット用のデモデータ作成・画像加工スクリプト
```

## ローカルで確認する

```
cd manemane-site
python -m http.server 8000
```

ブラウザで http://localhost:8000/ を開きます。

## 設定（assets/js/site-config.js）

値が `null` の項目は「未確定」として扱い、サイトには表示しません。確定したら値を入れてください（HTML の修正は不要です）。

| 項目 | 状態 | 説明 |
|---|---|---|
| `release.downloadUrl` | 設定済み | 一般公開する ZIP の URL（`null` にするとボタンが「公開準備中」になります） |
| `release.releaseDate` | 設定済み | 公開日 |
| `project.author` / `contactUrl` | 準備中 | `null` の間は「準備中」と表示します |
| `project.license` | 未確定 | `null` の間は表示しません |
| `release.version` / `fileName` / `fileSizeBytes` / `sha256` | 確定 | ZIP を作り直したら更新します |
| `changelog` | 確定 | 更新履歴（新しい順） |

SHA-256 とサイズは PowerShell で確認できます。

```
Get-FileHash .\Manemane-0.1.0-windows.zip -Algorithm SHA256
(Get-Item .\Manemane-0.1.0-windows.zip).Length
```

## 新しいバージョンを公開する手順

1. アプリの ZIP を作り直す（アプリ側で `gradlew.bat :desktop:packageWindows`）
2. 公開用の GitHub リポジトリで Release（例: `v0.2.0`）を作成し、ZIP を添付する
3. `site-config.js` の `release`（version・fileName・fileSizeBytes・sha256・releaseDate・downloadUrl）と `changelog` を更新する
4. このサイトをコミットして push する（GitHub Pages に自動で反映されます）

## スクリーンショットを撮り直す

画面の金額は説明用の架空のデータです（実際の家計のデータは使いません）。

1. `python tools/make_demo_db.py <アプリの V1__init.sql> <出力先>/demo.db` でデモデータを作る
2. アプリを `gradlew.bat :desktop:run -PkakeiboDb=<出力先>\demo.db` で起動し、各画面を `main.png` / `entry.png` / `year.png` / `help.png` として撮影する
3. `powershell -ExecutionPolicy Bypass -File tools\process_screens.ps1 -In <撮影した画像のフォルダ>` で `assets/img/screens` と OGP 画像を更新する
   （メイン画面はステータスバーのデータの保存場所の表示を切り取ります）

## GitHub Pages で公開する

1. このフォルダを GitHub のリポジトリに push する
2. リポジトリの Settings → Pages で「Deploy from a branch」、ブランチ `main`、フォルダ `/ (root)` を選ぶ

無料プランでは、GitHub Pages を公開できるのは公開（public）リポジトリだけです。

## CSS・JavaScript を変更したとき

ブラウザが古いファイルを使い続けないように、`index.html`・`guide.html`・`404.html` の読み込み部分の `?v=…`（例: `style.css?v=20261021b`）を新しい値に変えてください。

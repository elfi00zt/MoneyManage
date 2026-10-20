/*
 * サイトの設定（ここだけを書き換えれば、ダウンロードボタン・バージョン・更新履歴などが変わります）
 *
 * ルール
 *  - 値が null のものは「未確定」です。サイトには表示されません（リンクやボタンにもなりません）。
 *  - 確定したら値を入れてください。HTML を直す必要はありません。
 */
window.SITE_CONFIG = {
  // ---- アプリ（確定） ----
  app: {
    name: "まねまね(MoneyManage)",
    shortName: "まねまね",
    tagline: "給料日から次の給料日まで。お金の流れを、ひと目で。",
    // 動作確認済みの環境（実際に確認したものだけを書く）
    testedOn: "Windows 11 Home（64bit）",
    // 必要な環境（同梱の Java 実行環境で動くため Java は不要）
    requirements: [
      "Windows（64bit）",
      "Java のインストールは不要（アプリに同梱）",
      "ディスクの空き容量 約 200MB（展開後）"
    ]
  },

  // ---- 最新リリース ----
  release: {
    version: "0.1.0",                              // 確定（アプリ内のバージョン）
    fileName: "Manemane-0.1.0-windows.zip",        // 確定（配布する ZIP の名前）
    fileSizeBytes: 93963626,                       // 確定（現在のビルド。ZIP を作り直したら更新する）
    sha256: "3a9b03c07dacbce3ed6920dcce1831fdbc7c2b02dcf9fced8e0aaf25c899b29b", // 同上
    releaseDate: null,                             // 未確定（GitHub Releases で公開した日、例: "2026-11-01"）
    // 未確定: 一般公開する GitHub Releases の ZIP の URL
    // 例: "https://github.com/<ユーザー名>/<リポジトリ名>/releases/download/v0.1.0/Manemane-0.1.0-windows.zip"
    // null の間は、ダウンロードボタンが「公開準備中」になります
    downloadUrl: null,
    // 未確定: すべてのリリースの一覧ページ（例: "https://github.com/<ユーザー名>/<リポジトリ名>/releases"）
    releasesPageUrl: null
  },

  // ---- 公開先・連絡先（未確定） ----
  project: {
    // 未確定: 公開用 GitHub リポジトリの URL（null の間はフッターに表示しない）
    repositoryUrl: null,
    // 未確定: 作者名（表示名）。null の間は表示しない
    author: null,
    // 未確定: お問い合わせ先（URL または mailto:）。null の間は表示しない
    contactUrl: null,
    // 未確定: ライセンス名（例: "MIT License"）。null の間は表示しない
    license: null
  },

  // ---- 更新履歴（実際の変更内容。新しい順） ----
  // date は「公開した日」。未公開のものは null（表示は「未公開」）
  changelog: [
    {
      version: "0.1.0",
      date: null,
      items: [
        "給料日から次の給料日の前日までを1つの期間として管理",
        "収入・支出の登録・編集・削除・複製、項目名の入力補完",
        "前の期間の残額を自動で繰り越し（手入力での上書きも可能）",
        "固定費（サブスク・家賃など）を登録して期間にまとめて反映",
        "カテゴリ別の支出グラフ、前期との比較",
        "年間の収支（1月〜12月の月別・年間合計）",
        "Excel への書き出し・取り込み",
        "バックアップと復元",
        "アプリ内の使い方（ヘルプ）"
      ]
    }
  ]
};

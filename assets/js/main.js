/*
 * まねまね(MoneyManage) 公式サイトの動き
 *  - site-config.js の値を画面に反映する（未確定 = null の項目は表示しない）
 *  - スマートフォンのメニュー、画像の拡大表示、使い方ページの目次
 */
(function () {
  "use strict";

  var config = window.SITE_CONFIG || {};

  /** "release.version" のようなパスで設定値を取り出す。 */
  function valueOf(path) {
    return path.split(".").reduce(function (obj, key) {
      return obj == null ? undefined : obj[key];
    }, config);
  }

  function formatSize(bytes) {
    if (typeof bytes !== "number") return null;
    var mb = bytes / (1024 * 1024);
    return mb.toFixed(1) + " MB";
  }

  function formatDate(iso) {
    if (!iso) return null;
    var parts = iso.split("-");
    if (parts.length !== 3) return iso;
    return parts[0] + "年" + Number(parts[1]) + "月" + Number(parts[2]) + "日";
  }

  /* ---- 設定値の差し込み ----
   * data-config="release.version"      … 文字として差し込む
   * data-config-format="size" / "date" … 表示形式
   * data-optional="project.contactUrl" … 値がなければ要素ごと隠す
   * data-href="project.contactUrl"     … 値をリンク先にする
   */
  function applyConfig() {
    document.querySelectorAll("[data-config]").forEach(function (el) {
      var value = valueOf(el.getAttribute("data-config"));
      var format = el.getAttribute("data-config-format");
      if (format === "size") value = formatSize(value);
      if (format === "date") value = formatDate(value);
      if (value == null || value === "") {
        var fallback = el.getAttribute("data-fallback");
        if (fallback !== null) el.textContent = fallback;
        return;
      }
      el.textContent = value;
    });

    document.querySelectorAll("[data-optional]").forEach(function (el) {
      var value = valueOf(el.getAttribute("data-optional"));
      el.hidden = value == null || value === "";
    });

    document.querySelectorAll("[data-href]").forEach(function (el) {
      var value = valueOf(el.getAttribute("data-href"));
      if (value) el.setAttribute("href", value);
    });

    document.querySelectorAll("[data-list]").forEach(function (el) {
      var items = valueOf(el.getAttribute("data-list"));
      if (!Array.isArray(items) || items.length === 0) return;
      el.innerHTML = "";
      items.forEach(function (text) {
        var li = document.createElement("li");
        li.textContent = text;
        el.appendChild(li);
      });
    });

    var year = document.querySelector("[data-current-year]");
    if (year) year.textContent = String(new Date().getFullYear());
  }

  /* ---- ダウンロードボタン ----
   * downloadUrl が未設定（公開前）の間は、押せない「公開準備中」の表示にする
   */
  function applyDownload() {
    var url = valueOf("release.downloadUrl");
    var published = typeof url === "string" && url.length > 0;

    document.querySelectorAll("[data-download]").forEach(function (el) {
      var label = el.querySelector("[data-download-label]");
      if (published) {
        el.setAttribute("href", url);
        el.classList.remove("is-disabled");
        el.removeAttribute("aria-disabled");
        el.removeAttribute("tabindex");
        if (label) label.textContent = el.getAttribute("data-label-ready") || "Windows 版をダウンロード";
      } else {
        // 公開前は「ダウンロード」節へ案内するボタンにする（存在しないファイルへはリンクしない）
        var inPanel = el.hasAttribute("data-download-final");
        if (inPanel) {
          el.removeAttribute("href");
          el.classList.add("is-disabled");
          el.setAttribute("aria-disabled", "true");
          el.setAttribute("tabindex", "-1");
          if (label) label.textContent = "公開準備中";
        } else {
          el.setAttribute("href", "index.html#download");
          if (label) label.textContent = el.getAttribute("data-label-pending") || "ダウンロードについて";
        }
      }
    });

    document.querySelectorAll("[data-when-published]").forEach(function (el) {
      el.hidden = !published;
    });
    document.querySelectorAll("[data-when-unpublished]").forEach(function (el) {
      el.hidden = published;
    });
  }

  /* ---- 更新履歴 ---- */
  function renderChangelog() {
    var list = document.querySelector("[data-changelog]");
    var entries = valueOf("changelog");
    if (!list || !Array.isArray(entries)) return;
    list.innerHTML = "";
    entries.forEach(function (entry) {
      var li = document.createElement("li");
      li.className = "release";

      var head = document.createElement("div");
      var version = document.createElement("span");
      version.className = "release-version";
      version.textContent = "v" + entry.version;
      var date = document.createElement("span");
      date.className = "release-date";
      date.textContent = entry.date ? formatDate(entry.date) : "未公開";
      head.appendChild(version);
      head.appendChild(date);

      var items = document.createElement("ul");
      (entry.items || []).forEach(function (text) {
        var item = document.createElement("li");
        item.textContent = text;
        items.appendChild(item);
      });

      li.appendChild(head);
      li.appendChild(items);
      list.appendChild(li);
    });
  }

  /* ---- スマートフォンのメニュー ---- */
  function setupNav() {
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("site-nav");
    if (!toggle || !nav) return;

    function setOpen(open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "メニューを閉じる" : "メニューを開く");
    }

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  /* ---- 画像の拡大表示 ---- */
  function setupLightbox() {
    var dialog = document.getElementById("lightbox");
    if (!dialog || typeof dialog.showModal !== "function") return;
    var image = dialog.querySelector("img");
    var caption = dialog.querySelector("[data-lightbox-caption]");
    var close = dialog.querySelector("[data-lightbox-close]");

    document.querySelectorAll("[data-zoom]").forEach(function (button) {
      button.addEventListener("click", function () {
        var img = button.querySelector("img");
        image.src = img.getAttribute("src");
        image.alt = img.getAttribute("alt");
        caption.textContent = button.getAttribute("data-zoom");
        dialog.showModal();
      });
    });
    close.addEventListener("click", function () {
      dialog.close();
    });
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) dialog.close();
    });
  }

  /* ---- 使い方ページ: 表示中の項目を目次で強調する ---- */
  function setupToc() {
    var links = Array.prototype.slice.call(document.querySelectorAll(".toc a[href^='#']"));
    if (links.length === 0 || !("IntersectionObserver" in window)) return;
    var byId = {};
    links.forEach(function (a) {
      byId[a.getAttribute("href").slice(1)] = a;
    });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (a) {
          a.classList.remove("is-active");
          a.removeAttribute("aria-current");
        });
        var active = byId[entry.target.id];
        if (active) {
          active.classList.add("is-active");
          active.setAttribute("aria-current", "true");
        }
      });
    }, { rootMargin: "-80px 0px -70% 0px" });
    Object.keys(byId).forEach(function (id) {
      var section = document.getElementById(id);
      if (section) observer.observe(section);
    });
  }

  applyConfig();
  applyDownload();
  renderChangelog();
  setupNav();
  setupLightbox();
  setupToc();
})();

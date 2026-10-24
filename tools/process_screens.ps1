# Copies captured screenshots into assets/img/screens and builds the OGP image.
# Usage: powershell -ExecutionPolicy Bypass -File tools\process_screens.ps1 -In <folder with main.png and any of entry/year/help/filter/settings/login/savings/savings-chart/savings-entry/points/savings-accounts.png>
param([string]$In, [string]$Root = (Resolve-Path "$PSScriptRoot\..").Path)
Add-Type -AssemblyName System.Drawing
$out = Join-Path $Root 'assets\img\screens'
New-Item -ItemType Directory -Force -Path $out | Out-Null

function Save-Cropped([string]$name, [int]$bottom) {
  $src = [System.Drawing.Image]::FromFile((Join-Path $In "$name.png"))
  $rect = New-Object System.Drawing.Rectangle 0, 0, $src.Width, ($src.Height - $bottom)
  $bmp = New-Object System.Drawing.Bitmap $rect.Width, $rect.Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.DrawImage($src, (New-Object System.Drawing.Rectangle 0, 0, $rect.Width, $rect.Height), $rect, [System.Drawing.GraphicsUnit]::Pixel)
  $bmp.Save((Join-Path $out "$name.png"), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $src.Dispose()
  return $bmp
}

# メイン画面はステータスバー（DB の保存場所の表示）を切り取る
$main = Save-Cropped 'main' 36
# そのほかの画面は、撮り直したものだけをそのまま差し替える
foreach ($n in 'entry', 'year', 'help', 'filter', 'settings', 'login', 'savings', 'savings-chart', 'savings-entry', 'points', 'savings-accounts') {
  if (Test-Path (Join-Path $In "$n.png")) { (Save-Cropped $n 0).Dispose() }
}

# OGP 画像（1200x630）: ネイビーの背景にアイコン・アプリ名・メイン画面
$W = 1200; $H = 630
$ogp = New-Object System.Drawing.Bitmap $W, $H
$g = [System.Drawing.Graphics]::FromImage($ogp)
$g.SmoothingMode = 'AntiAlias'; $g.InterpolationMode = 'HighQualityBicubic'; $g.TextRenderingHint = 'AntiAliasGridFit'
$g.Clear([System.Drawing.Color]::FromArgb(255, 0x1B, 0x2A, 0x41))
$icon = [System.Drawing.Image]::FromFile((Join-Path $Root 'assets\img\icon-256.png'))
$g.DrawImage($icon, 72, 92, 112, 112)
$white = [System.Drawing.Brushes]::White
$sub = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 0xC9, 0xD4, 0xE5))
$titleFont = New-Object System.Drawing.Font 'Yu Gothic UI', 46, ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
$subFont = New-Object System.Drawing.Font 'Yu Gothic UI', 26, ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
$g.DrawString('まねまね', $titleFont, $white, 72, 232)
$g.DrawString('MoneyManage', $subFont, $sub, 76, 300)
$g.DrawString("給料日から次の給料日まで。`nお金の流れを、ひと目で。", $subFont, $white, 76, 372)
$g.DrawString('Windows 用 家計簿アプリ', $subFont, $sub, 76, 470)
# 右側にメイン画面（角を少し見せる）
$shotW = 640; $shotH = [int]($main.Height * $shotW / $main.Width)
$g.DrawImage($main, 500, 120, $shotW, $shotH)
$ogp.Save((Join-Path $Root 'assets\img\ogp.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $main.Dispose(); $icon.Dispose()
'ok'

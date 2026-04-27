param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path $Root).Path
$imagesRoot = Join-Path $projectRoot "images"
$albumRoot = Join-Path $projectRoot "images/album"
$outputPath = Join-Path $projectRoot "data/album.manifest.js"
$days = 1..7
$extensions = @("*.jpg", "*.jpeg", "*.png", "*.webp", "*.avif", "*.heic")

if (-not (Test-Path $albumRoot)) {
  throw "Album folder not found: $albumRoot"
}

$manifest = [ordered]@{}
foreach ($day in $days) {
  $dayKey = [string]$day
  $dayDir = Join-Path $albumRoot ("day{0}" -f $day)
  if (-not (Test-Path $dayDir)) {
    $manifest[$dayKey] = @()
    continue
  }

  $files = Get-ChildItem -Path $dayDir -File -ErrorAction SilentlyContinue |
    Where-Object { $extensions -contains ("*" + $_.Extension.ToLowerInvariant()) }

  if (@($files).Count -gt 0) {
    $manifest[$dayKey] = @($files |
      Sort-Object Name |
      ForEach-Object {
        "./images/album/day{0}/{1}" -f $day, $_.Name
      })
    continue
  }

  # Legacy fallback: when day folders are empty, use existing root images like day1-xxx.jpg
  $legacy = Get-ChildItem -Path $imagesRoot -File -Filter ("day{0}-*" -f $day) -ErrorAction SilentlyContinue
  $manifest[$dayKey] = @($legacy |
    Sort-Object Name |
    ForEach-Object {
      "./images/{0}" -f $_.Name
    })
}

$lines = @()
$lines += "window.NAGOYA_ALBUM_DATA = {"
foreach ($day in $days) {
  $key = [string]$day
  $items = @($manifest[$key])
  $quoted = $items | ForEach-Object { '"' + $_.Replace('\', '\\') + '"' }
  $lines += ('  "{0}": [{1}]' -f $key, ($quoted -join ", "))
  if ($day -ne $days[-1]) {
    $lines[-1] = $lines[-1] + ","
  }
}
$lines += "};"

Set-Content -Path $outputPath -Value ($lines -join [Environment]::NewLine) -Encoding UTF8
Write-Output "Generated: $outputPath"

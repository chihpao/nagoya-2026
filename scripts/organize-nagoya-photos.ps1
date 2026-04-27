param(
  [string]$Source = ".\\Nagoya_photo",
  [string]$TargetRoot = ".\\images\\album",
  [switch]$Clean = $true
)

$ErrorActionPreference = "Stop"

$sourcePath = (Resolve-Path $Source).Path
$targetPath = Join-Path (Resolve-Path ".").Path $TargetRoot

$dayMap = @{
  "20260401" = 1
  "20260402" = 2
  "20260403" = 3
  "20260404" = 4
  "20260405" = 5
  "20260406" = 6
  "20260407" = 7
}

$allowedExt = @(".jpg", ".jpeg", ".png", ".webp", ".avif", ".heic")

if (-not (Test-Path $sourcePath)) {
  throw "Source folder not found: $sourcePath"
}

New-Item -ItemType Directory -Force -Path $targetPath | Out-Null
1..7 | ForEach-Object { New-Item -ItemType Directory -Force -Path (Join-Path $targetPath ("day{0}" -f $_)) | Out-Null }
New-Item -ItemType Directory -Force -Path (Join-Path $targetPath "unassigned") | Out-Null

if ($Clean) {
  foreach ($dir in (1..7 | ForEach-Object { Join-Path $targetPath ("day{0}" -f $_) }) + (Join-Path $targetPath "unassigned")) {
    Get-ChildItem -Path $dir -File -ErrorAction SilentlyContinue | Remove-Item -Force
  }
}

$files = Get-ChildItem -Path $sourcePath -File
$files = $files | Where-Object { $allowedExt -contains $_.Extension.ToLowerInvariant() }

$dayCounters = @{}
1..7 | ForEach-Object { $dayCounters["day$_"] = 0 }
$unassignedCounter = 0

$summary = [ordered]@{}
1..7 | ForEach-Object { $summary["day$_"] = 0 }
$summary["unassigned"] = 0

foreach ($f in $files) {
  $name = $f.Name
  $ext = $f.Extension.ToLowerInvariant()
  $targetDir = $null
  $prefix = $null

  if ($name -match "^(20\d{6})") {
    $yyyymmdd = $matches[1]
    if ($dayMap.ContainsKey($yyyymmdd)) {
      $dayNum = $dayMap[$yyyymmdd]
      $targetDir = Join-Path $targetPath ("day{0}" -f $dayNum)
      $prefix = "day{0}" -f $dayNum
    }
  } elseif ($name -match "^(\d{13})") {
    try {
      $yyyymmdd = [DateTimeOffset]::FromUnixTimeMilliseconds([int64]$matches[1]).ToString("yyyyMMdd")
      if ($dayMap.ContainsKey($yyyymmdd)) {
        $dayNum = $dayMap[$yyyymmdd]
        $targetDir = Join-Path $targetPath ("day{0}" -f $dayNum)
        $prefix = "day{0}" -f $dayNum
      }
    } catch { }
  }

  if (-not $targetDir) {
    $targetDir = Join-Path $targetPath "unassigned"
    $prefix = "unknown"
  }

  if ($prefix -eq "unknown") {
    $unassignedCounter++
    $newName = "{0}-{1:D4}{2}" -f $prefix, $unassignedCounter, $ext
    $summary["unassigned"]++
  } else {
    $dayCounters[$prefix]++
    $newName = "{0}-{1:D4}{2}" -f $prefix, $dayCounters[$prefix], $ext
    $summary[$prefix]++
  }

  Copy-Item -Path $f.FullName -Destination (Join-Path $targetDir $newName) -Force
}

Write-Output "Organized files from: $sourcePath"
$summary.GetEnumerator() | ForEach-Object { Write-Output ("{0}`t{1}" -f $_.Key, $_.Value) }

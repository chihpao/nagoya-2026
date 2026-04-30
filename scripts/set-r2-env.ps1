$ErrorActionPreference = "Stop"

param(
  [string]$AccountId = "0688f2639c5f1d83f3c080999af360c0",
  [string]$BucketName = "nagoya-2026-photos",
  [string]$AccessKeyId,
  [string]$SecretAccessKey,
  [string]$PublicUrl = "https://pub-210057ec7a1c403a8c94ac8da5fd44ef.r2.dev"
)

if (-not $AccessKeyId) {
  throw "Missing -AccessKeyId (expected 32 chars)."
}

if (-not $SecretAccessKey) {
  throw "Missing -SecretAccessKey (expected 64 chars)."
}

if ($AccessKeyId.Length -ne 32) {
  throw "Invalid AccessKeyId length: $($AccessKeyId.Length). Expected 32."
}

if ($SecretAccessKey.Length -ne 64) {
  throw "Invalid SecretAccessKey length: $($SecretAccessKey.Length). Expected 64."
}

$env:R2_ACCOUNT_ID = $AccountId
$env:R2_BUCKET_NAME = $BucketName
$env:R2_ACCESS_KEY_ID = $AccessKeyId
$env:R2_SECRET_ACCESS_KEY = $SecretAccessKey
$env:R2_PUBLIC_URL = $PublicUrl

Write-Host "R2 env loaded for current shell:"
Write-Host "R2_ACCOUNT_ID=$env:R2_ACCOUNT_ID"
Write-Host "R2_BUCKET_NAME=$env:R2_BUCKET_NAME"
Write-Host "R2_ACCESS_KEY_ID length=$($env:R2_ACCESS_KEY_ID.Length)"
Write-Host "R2_SECRET_ACCESS_KEY length=$($env:R2_SECRET_ACCESS_KEY.Length)"
Write-Host "R2_PUBLIC_URL=$env:R2_PUBLIC_URL"

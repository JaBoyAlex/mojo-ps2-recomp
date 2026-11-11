param([string]$Archive)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$scanner = Join-Path $projectRoot 'build/gitleaks/gitleaks.exe'
if (!(Test-Path $scanner)) {
    New-Item -ItemType Directory -Force (Split-Path $scanner) | Out-Null
    $zip = Join-Path $projectRoot 'build/gitleaks.zip'
    Invoke-WebRequest 'https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_windows_x64.zip' -OutFile $zip
    if ((Get-FileHash $zip).Hash -ne 'd29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e') { throw 'Gitleaks checksum mismatch' }
    Expand-Archive -LiteralPath $zip -DestinationPath (Split-Path $scanner)
}
# Scan an exact allowlisted snapshot rather than private player directories.
$stage = Join-Path $projectRoot ('build/audit-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory $stage | Out-Null
foreach ($file in (Get-Content "$projectRoot/publication-files.json" -Raw | ConvertFrom-Json)) {
    $target = Join-Path $stage $file
    New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
    Copy-Item -LiteralPath (Join-Path $projectRoot $file) -Destination $target
}
& $scanner dir $stage --redact=100 --no-banner
if ($LASTEXITCODE -ne 0) { throw 'Source secret scan failed' }
& $scanner git $projectRoot --log-opts=--all --redact=100 --no-banner
if ($LASTEXITCODE -ne 0) { throw 'History secret scan failed' }
python "$projectRoot/scripts/verify_publication.py" --git
if ($LASTEXITCODE -ne 0) { throw 'Publication gate failed' }
if ($Archive) {
    python "$projectRoot/scripts/verify_publication.py" --archive $Archive
    if ($LASTEXITCODE -ne 0) { throw 'Archive gate failed' }
    $unpacked = Join-Path $projectRoot ('build/archive-audit-'+[guid]::NewGuid().ToString('N'))
    Expand-Archive -LiteralPath $Archive -DestinationPath $unpacked
    & $scanner dir $unpacked --redact=100 --no-banner
    if ($LASTEXITCODE -ne 0) { throw 'Archive secret scan failed' }
}

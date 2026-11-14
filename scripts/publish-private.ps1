param([string]$Archive = 'dist/MOJO-Recomp-v1.1.0-Windows-x64.zip')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot
gh auth status *> $null
if ($LASTEXITCODE -ne 0) { throw 'GitHub sign-in is required: run gh auth login, then rerun this script.' }
$owner = gh api user --jq .login
if ($LASTEXITCODE -ne 0 -or $owner -notmatch '^[A-Za-z0-9-]+$') { throw 'Cannot identify authenticated GitHub account.' }
if (!(Test-Path -LiteralPath $Archive)) { throw 'Build and test the release archive first.' }
& "$PSScriptRoot/security.ps1" -Archive $Archive
if ($LASTEXITCODE -ne 0) { throw 'Security gate failed' }
if (git status --porcelain) { throw 'Commit audited source before publishing.' }
gh repo view "$owner/mojo-ps2-recomp" --json name *> $null
if ($LASTEXITCODE -eq 0) { throw 'Repository already exists. Inspect it; this script will not overwrite an existing repository.' }
gh repo create mojo-ps2-recomp --private --source . --remote origin --description 'Build MOJO! USA PS2 natively on Windows from your own verified disc; portable standalone builder and optional RecompLauncher integration.'
if ($LASTEXITCODE -ne 0) { throw 'Private repository creation failed' }
git push -u origin main
if ($LASTEXITCODE -ne 0) { throw 'Source push failed' }
gh repo view --json url,isPrivate
if ($LASTEXITCODE -ne 0) { throw 'Remote verification failed' }
Write-Output 'Private source published. Let CI pass, then push the audited v1.1.0 tag to publish the verified release. Visibility remains private.'

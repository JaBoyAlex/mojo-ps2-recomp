param([string]$Game, [switch]$Prepare, [switch]$Smoke, [switch]$Fullscreen)
$ErrorActionPreference = 'Stop'
$env:PSModulePath = "$PSHOME\Modules;$env:ProgramFiles\WindowsPowerShell\Modules"
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$projectRoot = Split-Path $PSScriptRoot -Parent
$state = Join-Path $projectRoot 'userdata'
$cache = Join-Path $state 'cache'
$engine = Join-Path $cache 'engine-57ef1197'
$toolDir = Join-Path $cache 'tools'
try {
    if (!$Game -and !(Test-Path -LiteralPath (Join-Path $state 'disc.iso'))) {
        if ($Prepare) { Write-Output 'Select your MOJO! USA PS2 image using -Game.'; exit 20 }
        Add-Type -AssemblyName System.Windows.Forms
        $picker = New-Object System.Windows.Forms.OpenFileDialog
        $picker.Title = 'Your MOJO! USA PS2 disc (SLUS_207.41, VER 1.02)'
        $picker.Filter = 'PS2 disc images|*.iso;*.cue;*.bin;*.chd'
        if ($picker.ShowDialog() -ne 'OK') { exit 20 }
        $Game = $picker.FileName
        $picker.Dispose()
    }
    New-Item -ItemType Directory -Force $cache | Out-Null
    if (!(Test-Path "$engine/scripts/port.sh")) {
        Write-Output 'progress 0.01 Downloading the pinned open-source recompiler'
        $zip = Join-Path $cache 'engine.zip'
        Invoke-WebRequest -UseBasicParsing 'https://codeload.github.com/exoteric33/ps2-native-recomp/zip/57ef1197c0b818b9a4e1dbb98b1588da38586ffb' -OutFile $zip
        if ((Get-FileHash $zip -Algorithm SHA256).Hash -ne '12a78a14e2879c586e60239442ed5ef1b8a4d341ec0483bc2014f6988bb16930') { throw 'Source checksum mismatch' }
        Expand-Archive -LiteralPath $zip -DestinationPath $cache -Force
        Move-Item -LiteralPath "$cache/ps2-native-recomp-57ef1197c0b818b9a4e1dbb98b1588da38586ffb" -Destination $engine
    }
    Write-Output 'progress 0.03 Checking portable build tools (first setup downloads about 300 MB)'
    & "$engine/scripts/portable.ps1" -Dir $toolDir *> "$cache/toolchain-private.log"
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw 'Toolchain setup failed' }
    . "$toolDir/env.ps1" -Quiet -Keep RECOMPLAUNCHER,RECOMPLAUNCHER_MODE,RECOMPLAUNCHER_PAD
    $env:PS2_JOBS = [string][Math]::Min(6, [Math]::Max(1, [Environment]::ProcessorCount - 2))
    $params = @('-X', 'utf8', "$projectRoot/builder/build.py", '--engine', $engine, '--root', $projectRoot)
    if ($Game) { $params += @('--game', $Game) }
    if ($Prepare) { $params += '--prepare' }
    if ($Smoke) { $params += '--smoke' }
    if ($Fullscreen) { $params += '--fullscreen' }
    & "$toolDir/python/python.exe" @params
    exit $LASTEXITCODE
} catch {
    $_ | Out-String | Set-Content -LiteralPath (Join-Path $cache 'bootstrap-private.log')
    Write-Output 'Setup could not download or initialize its tools. Check free disk space, network access and folder write access. Private details are in userdata/cache; do not upload raw logs.'
    exit 21
}


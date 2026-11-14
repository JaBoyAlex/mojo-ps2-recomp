param([string]$ToolDir)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$env:PSModulePath = "$PSHOME\Modules;$env:ProgramFiles\WindowsPowerShell\Modules"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$projectRoot = Split-Path $PSScriptRoot -Parent
$buildRoot = Join-Path $projectRoot 'build'
New-Item -ItemType Directory -Force $buildRoot | Out-Null
function Get-Source([string]$Url, [string]$Hash, [string]$Name, [string]$Directory) {
    $zip = Join-Path $buildRoot "$Name.zip"
    if (!(Test-Path -LiteralPath $zip) -or (Get-FileHash $zip).Hash -ne $Hash) {
        Invoke-WebRequest -UseBasicParsing $Url -OutFile $zip
    }
    if ((Get-FileHash $zip).Hash -ne $Hash) { throw "Checksum mismatch: $Name" }
    $source = Join-Path $buildRoot $Directory
    if (!(Test-Path -LiteralPath $source)) { Expand-Archive -LiteralPath $zip -DestinationPath $buildRoot }
    return $source
}
$engineSource = Get-Source 'https://codeload.github.com/exoteric33/ps2-native-recomp/zip/57ef1197c0b818b9a4e1dbb98b1588da38586ffb' '12a78a14e2879c586e60239442ed5ef1b8a4d341ec0483bc2014f6988bb16930' 'engine' 'ps2-native-recomp-57ef1197c0b818b9a4e1dbb98b1588da38586ffb'
$chdSource = Get-Source 'https://codeload.github.com/rtissera/libchdr/zip/93d8c239ff0d4e8d7722985992649fce12d2463b' '59238fbd59428d2b540f41149de5dc0794d8d9050ebc1ae82d24096f3f60ab62' 'libchdr' 'libchdr-93d8c239ff0d4e8d7722985992649fce12d2463b'
if (!$ToolDir) { $ToolDir = Join-Path $buildRoot 'tools' }
& "$engineSource/scripts/portable.ps1" -Dir $ToolDir
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw 'Portable toolchain failed' }
. "$ToolDir/env.ps1" -Quiet
cmake -S $projectRoot -B "$buildRoot/helpers" -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release "-DLIBCHDR_SOURCE=$chdSource"
if ($LASTEXITCODE -ne 0) { throw 'Configure failed' }
cmake --build "$buildRoot/helpers" -j 4
if ($LASTEXITCODE -ne 0) { throw 'Helper build failed' }
& "$ToolDir/python/python.exe" "$projectRoot/scripts/test_camera.py" --engine $engineSource
if ($LASTEXITCODE -ne 0) { throw 'Camera controls tests failed' }
& "$ToolDir/python/python.exe" "$projectRoot/scripts/test_queue.py" --engine $engineSource
if ($LASTEXITCODE -ne 0) { throw 'Queue regression tests failed' }
& "$ToolDir/python/python.exe" "$projectRoot/scripts/test_fast_clear.py" --engine $engineSource
if ($LASTEXITCODE -ne 0) { throw 'Fast-clear guard tests failed' }
& "$ToolDir/python/python.exe" "$projectRoot/scripts/package.py"
if ($LASTEXITCODE -ne 0) { throw 'Release audit failed' }

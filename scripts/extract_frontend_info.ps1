################################################################################
# Frontend Information Extraction Script for InsightsLM
# Purpose: Gather comprehensive frontend information for documentation review
# Location: C:\Users\$env:USERNAME\Projects\InsightsLM\scripts\extract_frontend_info.ps1
# Usage: .\scripts\extract_frontend_info.ps1 [-OutputFile <path>]
################################################################################

param(
    [string]$OutputFile
)

# Configuration
$FrontendDir = "C:\Users\$env:USERNAME\Projects\InsightsLM\frontend"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Use provided OutputFile or generate default
if (-not $OutputFile) {
    $OutputFile = "C:\Users\$env:USERNAME\Projects\InsightsLM\frontend_info_$Timestamp.txt"
}

Write-Host "=========================================" -ForegroundColor Blue
Write-Host "  INSIGHTSLM FRONTEND INFORMATION" -ForegroundColor Blue
Write-Host "  Generated: $(Get-Date)" -ForegroundColor Blue
Write-Host "=========================================" -ForegroundColor Blue

# Check if frontend directory exists
if (!(Test-Path $FrontendDir)) {
    Write-Host "Error: Frontend directory not found at: $FrontendDir" -ForegroundColor Red
    exit 1
}

# Create output file
@"
================================================================================
INSIGHTSLM FRONTEND INFORMATION EXTRACTION
Generated: $(Get-Date)
================================================================================

"@ | Out-File -FilePath $OutputFile -Encoding UTF8

################################################################################
# SECTION 1: SYSTEM INFORMATION
################################################################################
Write-Host "`n[1/10] Gathering System Information..." -ForegroundColor Green
@"

================================================================================
1. SYSTEM INFORMATION
================================================================================

Computer Name: $env:COMPUTERNAME
OS: $((Get-CimInstance Win32_OperatingSystem).Caption)
OS Version: $((Get-CimInstance Win32_OperatingSystem).Version)
Architecture: $env:PROCESSOR_ARCHITECTURE

"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

################################################################################
# SECTION 2: DIRECTORY STRUCTURE
################################################################################
Write-Host "[2/10] Analyzing Directory Structure..." -ForegroundColor Green
Set-Location $FrontendDir

@"

================================================================================
2. DIRECTORY STRUCTURE
================================================================================

Frontend Root: $FrontendDir

"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

# Source directory structure
"Source Directory (src/):" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
if (Test-Path "src") {
    tree /F src | Out-File -FilePath $OutputFile -Append -Encoding UTF8
} else {
    "src directory not found" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

# Root level files
"`nRoot Level Files:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
Get-ChildItem -File | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize | Out-File -FilePath $OutputFile -Append -Encoding UTF8

################################################################################
# SECTION 3: NODE.JS ENVIRONMENT
################################################################################
Write-Host "[3/10] Checking Node.js Environment..." -ForegroundColor Green
@"

================================================================================
3. NODE.JS ENVIRONMENT
================================================================================

Node.js Version: $(node --version 2>&1)
npm Version: $(npm --version 2>&1)
Node Path: $(Get-Command node -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)

"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

################################################################################
# SECTION 4: INSTALLED PACKAGES
################################################################################
Write-Host "[4/10] Listing Installed Packages..." -ForegroundColor Green
@"

================================================================================
4. INSTALLED PACKAGES
================================================================================

Key Dependencies:

"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

# Run npm list for key packages
$keyPackages = @("react", "react-dom", "electron", "typescript", "vite", "axios")
foreach ($package in $keyPackages) {
    npm list $package --depth=0 2>&1 | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

"`nDevelopment Dependencies:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
"@electron-forge/*" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
npm list @electron-forge/cli @electron-forge/plugin-vite --depth=0 2>&1 | Out-File -FilePath $OutputFile -Append -Encoding UTF8

"`nAll Installed Packages (Production):" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
npm list --depth=0 --prod 2>&1 | Out-File -FilePath $OutputFile -Append -Encoding UTF8

################################################################################
# SECTION 5: PACKAGE.JSON ANALYSIS
################################################################################
Write-Host "[5/10] Analyzing package.json..." -ForegroundColor Green
@"

================================================================================
5. PACKAGE.JSON ANALYSIS
================================================================================

"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

if (Test-Path "package.json") {
    $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
    
    "Name: $($packageJson.name)" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    "Version: $($packageJson.version)" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    "Description: $($packageJson.description)" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    "`nMain: $($packageJson.main)" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    
    "`nScripts:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    $packageJson.scripts.PSObject.Properties | ForEach-Object {
        "  $($_.Name): $($_.Value)" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    }
    
    "`nDependencies:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    $packageJson.dependencies.PSObject.Properties | ForEach-Object {
        "  $($_.Name): $($_.Value)" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    }
    
    "`nDev Dependencies:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    $packageJson.devDependencies.PSObject.Properties | ForEach-Object {
        "  $($_.Name): $($_.Value)" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    }
} else {
    "package.json not found" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

################################################################################
# SECTION 6: TYPESCRIPT CONFIGURATION
################################################################################
Write-Host "[6/10] Checking TypeScript Configuration..." -ForegroundColor Green
@"

================================================================================
6. TYPESCRIPT CONFIGURATION
================================================================================

"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

if (Test-Path "tsconfig.json") {
    "tsconfig.json:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    Get-Content "tsconfig.json" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
} else {
    "tsconfig.json not found" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

################################################################################
# SECTION 7: VITE & ELECTRON FORGE CONFIGURATION
################################################################################
Write-Host "[7/10] Analyzing Build Configuration..." -ForegroundColor Green
@"

================================================================================
7. BUILD CONFIGURATION
================================================================================

Vite Config Files:
"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

$viteConfigs = @("vite.main.config.mjs", "vite.preload.config.mjs", "vite.renderer.config.mjs")
foreach ($config in $viteConfigs) {
    if (Test-Path $config) {
        "`n${config} (first 20 lines):" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
        Get-Content $config -Head 20 | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    } else {
        "`n${config}: Not found" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    }
}

"`nElectron Forge Configuration:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
if (Test-Path "forge.config.mjs") {
    Get-Content "forge.config.mjs" -Head 30 | Out-File -FilePath $OutputFile -Append -Encoding UTF8
} else {
    "forge.config.mjs not found" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

################################################################################
# SECTION 8: SOURCE CODE ANALYSIS
################################################################################
Write-Host "[8/10] Analyzing Source Code..." -ForegroundColor Green
@"

================================================================================
8. SOURCE CODE ANALYSIS
================================================================================

"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

# Count lines in main files
$mainFiles = @("src/main.ts", "src/preload.ts", "src/renderer.tsx", "src/App.tsx", "src/services/api.ts")
foreach ($file in $mainFiles) {
    if (Test-Path $file) {
        $lines = (Get-Content $file | Measure-Object -Line).Lines
        "${file}: $lines lines" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    } else {
        "${file}: Not found" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    }
}

# Extract imports from key files
"`nApp.tsx imports:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
if (Test-Path "src/App.tsx") {
    Get-Content "src/App.tsx" | Select-String "^import" | ForEach-Object { "  $_" } | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

"`napi.ts exports:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
if (Test-Path "src/services/api.ts") {
    Get-Content "src/services/api.ts" | Select-String "export (const|function|async function)" | ForEach-Object { "  $_" } | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

################################################################################
# SECTION 9: ELECTRON PROCESS INFO
################################################################################
Write-Host "[9/10] Checking Electron Processes..." -ForegroundColor Green
@"

================================================================================
9. ELECTRON PROCESS INFORMATION
================================================================================

Running Electron Processes:
"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

$electronProcesses = Get-Process | Where-Object {$_.ProcessName -like "*electron*"}
if ($electronProcesses) {
    $electronProcesses | Select-Object Name, Id, CPU, WorkingSet, Path | Format-Table -AutoSize | Out-File -FilePath $OutputFile -Append -Encoding UTF8
} else {
    "No Electron processes currently running" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

################################################################################
# SECTION 10: GIT INFORMATION
################################################################################
Write-Host "[10/10] Gathering Git Information..." -ForegroundColor Green
Set-Location "C:\Users\$env:USERNAME\Projects\InsightsLM"
@"

================================================================================
10. GIT REPOSITORY INFORMATION
================================================================================

Repository Root: C:\Users\$env:USERNAME\Projects\InsightsLM

Current Branch:
"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

git branch --show-current 2>&1 | Out-File -FilePath $OutputFile -Append -Encoding UTF8

"`nRecent Commits (last 5):" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
git log --oneline -5 2>&1 | Out-File -FilePath $OutputFile -Append -Encoding UTF8

"`nGit Status:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
git status 2>&1 | Out-File -FilePath $OutputFile -Append -Encoding UTF8

"`nFrontend-specific changes:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
git status frontend/ 2>&1 | Out-File -FilePath $OutputFile -Append -Encoding UTF8

################################################################################
# SECTION 11: ADDITIONAL INFORMATION
################################################################################
@"

================================================================================
11. ADDITIONAL INFORMATION
================================================================================

Environment Variables (relevant):
  NODE_ENV: $env:NODE_ENV
  PATH (first 5 entries):
"@ | Out-File -FilePath $OutputFile -Append -Encoding UTF8

$env:PATH -split ';' | Select-Object -First 5 | ForEach-Object { "    $_" } | Out-File -FilePath $OutputFile -Append -Encoding UTF8

"`nBuild Output:" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
if (Test-Path ".vite") {
    "  .vite directory exists (build cache)" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
} else {
    "  No .vite directory (clean state)" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

if (Test-Path "out") {
    "  out directory exists (production builds)" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
    Get-ChildItem "out" -Directory | ForEach-Object { "    - $($_.Name)" } | Out-File -FilePath $OutputFile -Append -Encoding UTF8
} else {
    "  No out directory" | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

################################################################################
# COMPLETION
################################################################################
$endDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$endText = @"

================================================================================
END OF FRONTEND INFORMATION EXTRACTION
Generated: $endDate
================================================================================
"@

$endText | Out-File -FilePath $OutputFile -Append -Encoding UTF8

# Output to console using single-quoted here-string (parser-proof)
$footer = @'
=========================================
Frontend extraction complete!
=========================================
'@

Write-Host ""
Write-Host $footer -ForegroundColor Green
Write-Host "Output saved to:" -ForegroundColor Yellow
Write-Host "  $OutputFile" -ForegroundColor Cyan
Write-Host ""
$fileSize = [math]::Round((Get-Item $OutputFile).Length / 1KB, 2)
Write-Host "File size: $fileSize KB"
Write-Host ""
Write-Host "To view:" -ForegroundColor Yellow
Write-Host "  notepad $OutputFile" -ForegroundColor DarkCyan
Write-Host "  Get-Content $OutputFile" -ForegroundColor DarkCyan
Write-Host ""

# Return the output file path for the master script
Write-Output $OutputFile

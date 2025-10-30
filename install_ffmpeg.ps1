# FFmpeg Installer for Windows
Write-Host "FFmpeg Installer for Argus Project" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Define paths
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$downloadPath = "$env:TEMP\ffmpeg.zip"
$extractPath = "C:\ffmpeg"
$binPath = "$extractPath\bin"

Write-Host "Step 1: Downloading FFmpeg..." -ForegroundColor Green
try {
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $downloadPath -UseBasicParsing
    Write-Host "Downloaded successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to download: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Extracting FFmpeg..." -ForegroundColor Green
try {
    if (Test-Path $extractPath) {
        Remove-Item $extractPath -Recurse -Force
    }
    
    Expand-Archive -Path $downloadPath -DestinationPath $env:TEMP -Force
    $extractedFolder = Get-ChildItem -Path $env:TEMP -Directory | Where-Object { $_.Name -like "ffmpeg-*" } | Select-Object -First 1
    
    if ($extractedFolder) {
        Move-Item -Path $extractedFolder.FullName -Destination $extractPath -Force
        Write-Host "Extracted successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "Failed to extract: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Adding to PATH..." -ForegroundColor Green
try {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$binPath*") {
        $newPath = "$currentPath;$binPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path = "$env:Path;$binPath"
        Write-Host "Added to PATH successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "Failed to add to PATH: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "Please restart your terminal/VS Code" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"

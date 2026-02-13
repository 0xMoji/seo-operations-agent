#!/usr/bin/env pwsh
# SEO Operations Agent - Auto Installer
# Downloads the latest .skill file from GitHub releases

Write-Host "🚀 SEO Operations Agent Installer" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

$repo = "0xMoji/seo-operations-agent"
$skillFile = "seo-operations-agent.skill"
$releaseUrl = "https://github.com/$repo/releases/latest/download/$skillFile"

Write-Host "📦 Downloading latest version from GitHub..." -ForegroundColor Yellow
Write-Host "   URL: $releaseUrl" -ForegroundColor Gray
Write-Host ""

try {
    # Download the skill file
    Invoke-WebRequest -Uri $releaseUrl -OutFile $skillFile -ErrorAction Stop
    
    $fileSize = (Get-Item $skillFile).Length / 1KB
    Write-Host "✅ Downloaded successfully!" -ForegroundColor Green
    Write-Host "   File: $skillFile ($([math]::Round($fileSize, 2)) KB)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Load $skillFile into OpenClaw" -ForegroundColor White
    Write-Host "   2. Follow the setup guide in the repository" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Documentation: https://github.com/$repo" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Download failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Manual download:" -ForegroundColor Yellow
    Write-Host "   Visit: https://github.com/$repo/releases/latest" -ForegroundColor White
    exit 1
}

# =============================================================================
# Script de téléchargement des sujets BAC SVT depuis eddirasa.com
# Sujets + Corrections | Sciences Expérimentales (علوم تجريبية)
# =============================================================================
# Usage: .\download-bac-svt.ps1
# Destination: ..\public\pdfs\bac-svt\
# =============================================================================

$ErrorActionPreference = "Continue"
$OutputDir = Join-Path $PSScriptRoot "..\public\pdfs\bac-svt"

if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Configuration
$Years = 2008..2025
$BaseUrl = "https://eddirasa.com"
$DelayBetweenRequests = 2  # secondes pour ne pas surcharger le serveur

# Statistiques
$Stats = @{
    Downloaded = 0
    Skipped    = 0
    Failed     = 0
    Total      = 0
}

function Get-PdfUrlFromPage {
    param([string]$PageUrl)
    
    try {
        $response = Invoke-WebRequest -Uri $PageUrl -UseBasicParsing -TimeoutSec 15
        $html = $response.Content
        
        # Chercher le lien PDF dans le pattern "تحميل" (téléchargement)
        # Pattern: href="...*.pdf" after "تحميل" or near "تحميل"
        if ($html -match '(?s)تحميل\s*:.*?href="([^"]+\.pdf)"') {
            $pdfPath = $Matches[1]
            if ($pdfPath -notmatch '^http') {
                $pdfPath = "$BaseUrl$pdfPath"
            }
            return $pdfPath
        }
        
        # Pattern alternatif: chercher tout lien PDF dans le contenu principal
        if ($html -match '(?s)entry-content.*?href="([^"]+\.pdf)"') {
            $pdfPath = $Matches[1]
            if ($pdfPath -notmatch '^http') {
                $pdfPath = "$BaseUrl$pdfPath"
            }
            return $pdfPath
        }
        
        # Dernier recours: premier lien PDF trouvé
        if ($html -match 'href="([^"]+\.pdf)"') {
            $pdfPath = $Matches[1]
            if ($pdfPath -notmatch '^http') {
                $pdfPath = "$BaseUrl$pdfPath"
            }
            return $pdfPath
        }
        
        return $null
    }
    catch {
        Write-Host "  [ERREUR] Impossible de récupérer la page: $_" -ForegroundColor Red
        return $null
    }
}

function Download-Pdf {
    param(
        [string]$Url,
        [string]$OutputPath,
        [string]$Label
    )
    
    if (Test-Path $OutputPath) {
        Write-Host "  [DÉJÀ PRÉSENT] $Label" -ForegroundColor Yellow
        $Stats.Skipped++
        return $true
    }
    
    try {
        Write-Host "  [TÉLÉCHARGEMENT] $Label..." -ForegroundColor Cyan
        $webClient = New-Object System.Net.WebClient
        $webClient.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        $webClient.DownloadFile($Url, $OutputPath)
        
        $fileSize = (Get-Item $OutputPath).Length
        $fileSizeKB = [math]::Round($fileSize / 1024, 1)
        Write-Host "  [OK] $Label ($fileSizeKB KB)" -ForegroundColor Green
        $Stats.Downloaded++
        return $true
    }
    catch {
        Write-Host "  [ERREUR] Échec du téléchargement: $_" -ForegroundColor Red
        if (Test-Path $OutputPath) { Remove-Item $OutputPath -Force }
        $Stats.Failed++
        return $false
    }
}

# =============================================================================
# BOUCLE PRINCIPALE
# =============================================================================

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  TÉLÉCHARGEMENT DES SUJETS BAC SVT - SCIENCES EXPÉRIMENTALES" -ForegroundColor Cyan
Write-Host "  Source: eddirasa.com | Destination: $OutputDir" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

foreach ($Year in $Years) {
    $Stats.Total++
    
    Write-Host "--- $Year ---" -ForegroundColor White
    
    # --- SUJET ---
    $subjectPageUrl = "$BaseUrl/bac-science-$Year-se/"
    $subjectPdfUrl = Get-PdfUrlFromPage -PageUrl $subjectPageUrl
    
    if ($subjectPdfUrl) {
        $subjectFileName = "bac-svt-sujet-$Year.pdf"
        $subjectOutputPath = Join-Path $OutputDir $subjectFileName
        Download-Pdf -Url $subjectPdfUrl -OutputPath $subjectOutputPath -Label "Sujet $Year"
    }
    else {
        Write-Host "  [INFO] Aucun sujet trouvé pour $Year" -ForegroundColor DarkGray
    }
    
    Start-Sleep -Seconds $DelayBetweenRequests
    
    # --- CORRECTION ---
    $correctionPageUrl = "$BaseUrl/correction-bac-science-$Year-se/"
    $correctionPdfUrl = Get-PdfUrlFromPage -PageUrl $correctionPageUrl
    
    if ($correctionPdfUrl) {
        $correctionFileName = "bac-svt-correction-$Year.pdf"
        $correctionOutputPath = Join-Path $OutputDir $correctionFileName
        Download-Pdf -Url $correctionPdfUrl -OutputPath $correctionOutputPath -Label "Correction $Year"
    }
    else {
        Write-Host "  [INFO] Aucune correction trouvée pour $Year" -ForegroundColor DarkGray
    }
    
    Start-Sleep -Seconds $DelayBetweenRequests
    Write-Host ""
}

# =============================================================================
# RÉSUMÉ
# =============================================================================

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  RÉSUMÉ" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  Téléchargés: $($Stats.Downloaded)" -ForegroundColor Green
Write-Host "  Déjà présents: $($Stats.Skipped)" -ForegroundColor Yellow
Write-Host "  Échoués: $($Stats.Failed)" -ForegroundColor Red
Write-Host "  Total années: $($Stats.Total)" -ForegroundColor White
Write-Host ""

# Lister les fichiers téléchargés
Write-Host "  Fichiers dans $OutputDir :" -ForegroundColor Cyan
Get-ChildItem $OutputDir -Filter "*.pdf" | ForEach-Object {
    $sizeKB = [math]::Round($_.Length / 1024, 1)
    Write-Host "    - $($_.Name) ($sizeKB KB)" -ForegroundColor White
}

Write-Host ""
Write-Host "  TERMINÉ !" -ForegroundColor Green

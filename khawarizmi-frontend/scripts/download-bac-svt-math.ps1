$ErrorActionPreference = "SilentlyContinue"
$destDir = "C:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\khawarizmi-frontend\public\pdfs\bac-svt-math"
New-Item -ItemType Directory -Force -Path $destDir | Out-Null

Write-Host "=== TELECHARGEMENT SVT FILIERE MATHEMATIQUES ===" -ForegroundColor Cyan
Write-Host "Matiere: Sciences de la Vie et de la Terre (SVT)"
Write-Host "Filiere: Mathematiques (riyadiyat)" -ForegroundColor Yellow

# eddirasa.com pages: bac-math-sciences-{YEAR}
# PDF pattern varies by year
$years = @(2008, 2009, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026)

foreach ($year in $years) {
    $destFile = Join-Path $destDir "bac-svt-math-$year.pdf"
    
    if (Test-Path $destFile) {
        Write-Host "[SKIP] $year - deja existe" -ForegroundColor DarkGray
        continue
    }

    try {
        # Fetch the page to find the PDF URL
        $pageUrl = "https://eddirasa.com/bac-math-sciences-$year/"
        $response = Invoke-WebRequest -Uri $pageUrl -TimeoutSec 15 -ErrorAction Stop
        $content = $response.Content

        # Find PDF link in page content
        $pdfUrl = $null
        
        # Pattern 1: uploads/YYYY/MM/bac-math-science-YYYY.pdf
        if ($content -match 'uploads/(\d{4})/(\d{2})/bac-math-science-\d{4}\.pdf') {
            $pdfUrl = "https://eddirasa.com/wp-content/$($Matches[0])"
        }
        # Pattern 2: uploads/bac/YYYY/eddirasa-bac-math-science-YYYY.pdf
        elseif ($content -match 'uploads/bac/(\d{4})/eddirasa-bac-math-science-\d{4}\.pdf') {
            $pdfUrl = "https://eddirasa.com/wp-content/$($Matches[0])"
        }
        # Pattern 3: uploads/YYYY/MM/bac-math-sciences-YYYY.pdf (plural)
        elseif ($content -match 'uploads/(\d{4})/(\d{2})/bac-math-sciences-\d{4}\.pdf') {
            $pdfUrl = "https://eddirasa.com/wp-content/$($Matches[0])"
        }

        if ($pdfUrl) {
            Invoke-WebRequest -Uri $pdfUrl -OutFile $destFile -TimeoutSec 20 -ErrorAction Stop
            $size = [math]::Round((Get-Item $destFile).Length / 1KB)
            Write-Host "[OK] $year - $size KB - $pdfUrl" -ForegroundColor Green
        } else {
            Write-Host "[SKIP] $year - PDF non trouve dans la page" -ForegroundColor DarkYellow
        }
    } catch {
        Remove-Item $destFile -Force -ErrorAction SilentlyContinue
        Write-Host "[FAIL] $year - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== RESUME ===" -ForegroundColor Cyan
$files = Get-ChildItem -Path $destDir -Filter "*.pdf"
Write-Host "$($files.Count) PDFs telecharges dans bac-svt-math/"
if ($files.Count -gt 0) {
    $totalSize = [math]::Round(($files | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
    Write-Host "Taille totale: $totalSize MB"
}

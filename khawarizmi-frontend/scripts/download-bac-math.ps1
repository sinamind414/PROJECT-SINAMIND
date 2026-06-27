$ErrorActionPreference = "SilentlyContinue"
$destDir = "C:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\khawarizmi-frontend\public\pdfs\bac-math"

Write-Host "=== TELECHARGEMENT SUJETS BAC MATHEMATIQUES ===" -ForegroundColor Cyan

# --- BAC-ALGERIE.NET (2008-2025) - pattern: bac{YEAR}-Mathematiques.pdf ---
$years = @(2008, 2009, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025)

foreach ($year in $years) {
    $url = "https://bac-algerie.net/sujets/$year/bac$year-Mathematiques.pdf"
    $destFile = Join-Path $destDir "bac-math-algerie-$year.pdf"

    if (Test-Path $destFile) {
        Write-Host "[SKIP] $year - deja existe" -ForegroundColor DarkGray
        continue
    }

    try {
        Invoke-WebRequest -Uri $url -OutFile $destFile -TimeoutSec 20 -ErrorAction Stop
        $size = [math]::Round((Get-Item $destFile).Length / 1KB)
        Write-Host "[OK] $year - $size KB" -ForegroundColor Green
    } catch {
        Remove-Item $destFile -Force -ErrorAction SilentlyContinue
        Write-Host "[FAIL] $year - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# --- EDDIRASA.COM (2012-2026) ---
Write-Host "`n=== EDDIRASA.COM ===" -ForegroundColor Yellow

$eddirasaYears = @{
    2012 = @{ page = "bac-math-2012-se"; file = "bac-sci-math-2012" }
    2013 = @{ page = "bac-math-2013-se"; file = "bac-sci-math-2013" }
    2014 = @{ page = "bac-math-2014-se"; file = "bac-sci-math-2014" }
    2015 = @{ page = "bac-math-2015-se"; file = "bac-sci-math-2015" }
    2016 = @{ page = "bac-math-2016-se"; file = "bac-sci-math-2016" }
    2017 = @{ page = "bac-math-2017-se"; file = "bac-sci-math-2017" }
    2018 = @{ page = "bac-math-2018-se"; file = "bac-sci-math-2018" }
    2019 = @{ page = "bac-math-2019-se"; file = "bac-sci-math-2019" }
    2020 = @{ page = "bac-math-2020-se"; file = "bac-sci-math-2020" }
    2021 = @{ page = "bac-math-2021-se"; file = "bac-sci-math-2021" }
    2022 = @{ page = "bac-math-2022-se"; file = "bac-sci-math-2022" }
    2023 = @{ page = "bac-math-2023-se"; file = "bac-sci-math-2023" }
    2024 = @{ page = "bac-math-2024-se"; file = "bac-sci-math-2024" }
    2025 = @{ page = "bac-math-2025-se"; file = "bac-sci-math-2025" }
    2026 = @{ page = "bac-math-2026-se"; file = "bac-sci-math-2026" }
}

foreach ($year in ($eddirasaYears.Keys | Sort-Object)) {
    $info = $eddirasaYears[$year]
    $destFile = Join-Path $destDir "bac-math-eddirasa-$year.pdf"
    
    if (Test-Path $destFile) {
        Write-Host "[SKIP] $year eddirasa - deja existe" -ForegroundColor DarkGray
        continue
    }

    try {
        $pageUrl = "https://eddirasa.com/$($info.page)/"
        $response = Invoke-WebRequest -Uri $pageUrl -TimeoutSec 15 -ErrorAction Stop
        
        # Chercher le lien PDF
        $content = $response.Content
        $pattern = "uploads/\d{4}/\d{2}/$($info.file)\.pdf"
        if ($content -match $pattern) {
            $match = $Matches[0]
            $pdfUrl = "https://eddirasa.com/wp-content/$match"
            Invoke-WebRequest -Uri $pdfUrl -OutFile $destFile -TimeoutSec 20 -ErrorAction Stop
            $size = [math]::Round((Get-Item $destFile).Length / 1KB)
            Write-Host "[OK] $year eddirasa - $size KB" -ForegroundColor Green
        } else {
            Write-Host "[SKIP] $year eddirasa - PDF non trouve dans la page" -ForegroundColor DarkYellow
        }
    } catch {
        Remove-Item $destFile -Force -ErrorAction SilentlyContinue
        Write-Host "[FAIL] $year eddirasa - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== RESUME ===" -ForegroundColor Cyan
$files = Get-ChildItem -Path $destDir -Filter "*.pdf"
Write-Host "$($files.Count) PDFs telecharges dans bac-math/"
$totalSize = [math]::Round(($files | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "Taille totale: $totalSize MB"

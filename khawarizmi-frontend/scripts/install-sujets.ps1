# install-sujets.ps1
# Installation automatique des sujets BAC — PowerShell (Windows)
# Usage: .\scripts\install-sujets.ps1 [-SourceDir ".\mes-pdfs"] [-Interactive]

param(
  [string]$SourceDir = "",
  [switch]$Interactive
)

$ErrorActionPreference = "Stop"

$FrontendDir   = "$PSScriptRoot\.."
$PdfDest       = "$FrontendDir\public\pdfs"
$ConfigFile    = "$FrontendDir\src\lib\annales-bac.ts"

$Host.UI.RawUI.ForegroundColor = "Cyan"
Write-Host "========================================"
Write-Host "  INSTALLATION AUTOMATIQUE DES SUJETS BAC"
Write-Host "========================================"
Write-Host ""
$Host.UI.RawUI.ForegroundColor = "White"

# --- Étape 1 : Créer la structure ---
Write-Host "`n[1/4] Création de la structure..." -ForegroundColor Blue
New-Item -ItemType Directory -Path $PdfDest -Force | Out-Null
Write-Host "  ✅ $PdfDest" -ForegroundColor Green

# --- Étape 2 : Copier les PDFs ---
Write-Host "`n[2/4] Copie des PDFs..." -ForegroundColor Blue
if ($SourceDir -and (Test-Path $SourceDir)) {
  $pdfs = Get-ChildItem -Path $SourceDir -Filter "*.pdf"
  if ($pdfs.Count -eq 0) {
    Write-Host "  ⚠️  Aucun PDF trouvé dans $SourceDir" -ForegroundColor Yellow
  } else {
    foreach ($pdf in $pdfs) {
      Copy-Item -Path $pdf.FullName -Destination "$PdfDest\$($pdf.Name)" -Force
      Write-Host "  ✅ $($pdf.Name)" -ForegroundColor Green
    }
  }
} else {
  Write-Host "  ⏩ Aucun dossier source. Copie manuelle dans :" -ForegroundColor Yellow
  Write-Host "     $PdfDest" -ForegroundColor White
}

# --- Étape 3 : Collecter les infos ---
Write-Host "`n[3/4] Configuration des nouveaux sujets..." -ForegroundColor Blue
$newSubjects = @()

if ($SourceDir -and (Test-Path $SourceDir)) {
  $pdfs = Get-ChildItem -Path $SourceDir -Filter "*.pdf"
  if ($Interactive -or $pdfs.Count -gt 0) {
    foreach ($pdf in $pdfs) {
      $slug = $pdf.BaseName -replace '[^a-zA-Z0-9]', '-' -replace '-+', '-' -replace '^-|-$', '' | ForEach-Object { $_.ToLower() }

      Write-Host "`n  --- $($pdf.Name) ---" -ForegroundColor Yellow
      $titreFr   = Read-Host "  Titre (fr)"
      $titreAr   = Read-Host "  Titre (ar)"
      $annee     = Read-Host "  Année"
      $session    = Read-Host "  Session (normale/rattrapage)"
      $difficulte = Read-Host "  Difficulté (facile/moyen/difficile)"
      $chapitres  = Read-Host "  Chapitres (séparés par ,)"

      $filiere = "Sciences Expérimentales"
      if ($chapitres -match "énergie|dynamique") { $filiere = "Sciences Expérimentales" }

      $newSubjects += [PSCustomObject]@{
        Slug       = $slug
        TitreFr    = $titreFr
        TitreAr    = $titreAr
        Annee      = [int]$annee
        Session    = $session
        Difficulte = $difficulte
        Filiere    = $filiere
        Chapitres  = ($chapitres -split ',' | ForEach-Object { $_.Trim() })
        PdfFile    = $pdf.Name
      }
    }
  }
}

if (-not $SourceDir -or $Interactive) {
  $manual = $true
  while ($manual) {
    Write-Host "`n  --- Nouveau sujet manuel ---" -ForegroundColor Yellow
    $slug = Read-Host "  Slug (ex: bac2024-svt)"
    $titreFr = Read-Host "  Titre (fr)"
    $titreAr = Read-Host "  Titre (ar)"
    $annee = Read-Host "  Année"
    $session = Read-Host "  Session (normale/rattrapage)"
    $difficulte = Read-Host "  Difficulté (facile/moyen/difficile)"
    $chapitres = Read-Host "  Chapitres (séparés par ,)"
    $filiere = Read-Host "  Filière (Sciences Expérimentales)"
    if (-not $filiere) { $filiere = "Sciences Expérimentales" }
    $pdfFile = Read-Host "  Nom du fichier PDF"

    $newSubjects += [PSCustomObject]@{
      Slug       = $slug
      TitreFr    = $titreFr
      TitreAr    = $titreAr
      Annee      = [int]$annee
      Session    = $session
      Difficulte = $difficulte
      Filiere    = $filiere
      Chapitres  = ($chapitres -split ',' | ForEach-Object { $_.Trim() })
      PdfFile    = $pdfFile
    }

    $more = Read-Host "  Ajouter un autre sujet ? (o/N)"
    if ($more -ne "o") { $manual = $false }
  }
}

# --- Étape 4 : Générer le snippet TypeScript ---
Write-Host "`n[4/4] Génération du snippet TypeScript..." -ForegroundColor Blue

$snippetFile = "$PSScriptRoot\_sujet-a-ajouter.ts.txt"
$dateStr = Get-Date -Format "yyyy-MM-dd HH:mm"

$lines = @(
  "// ==================================================================="
  "// SUJETS À AJOUTER — Généré le $dateStr"
  "// Copiez ces lignes dans src/lib/annales-bac.ts"
  "// ==================================================================="
  "// 1. Ouvrez annales-bac.ts"
  '// 2. Avant la ligne "export function getSujetBySlug..."'
  "// 3. Collez ce bloc après la dernière fermeture `"},`" du tableau SUJETS"
  "// ==================================================================="
  ""
)

foreach ($s in $newSubjects) {
  $chaps = ($s.Chapitres | ForEach-Object { "`"$_`"" }) -join ", "
  $lines += @(
    "  {"
    "    slug: `"$($s.Slug)`","
    "    annee: $($s.Annee),"
    "    session: `"$($s.Session)`","
    "    matiere: `"SVT`","
    "    filiere: `"$($s.Filiere)`","
    "    titre: `"$($s.TitreFr)`","
    "    titreAr: `"$($s.TitreAr)`","
    "    difficulte: `"$($s.Difficulte)`","
    "    duree: 180,"
    "    totalPages: 4,"
    "    chapitres: [$chaps],"
    "    url_pdf: `"/pdfs/$($s.PdfFile)`","
    "    exercices: [],"
    "    subjects: []"
    "  },"
    ""
  )
}

$lines -join "`r`n" | Out-File -FilePath $snippetFile -Encoding UTF8

Write-Host "  ✅ Snippet généré : $snippetFile" -ForegroundColor Green

# --- Résumé ---
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✅ TERMINÉ !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Prochaines étapes :" -ForegroundColor White
Write-Host "  1. Copiez les PDFs dans : $PdfDest" -ForegroundColor Gray
Write-Host "  2. Ouvrez : $ConfigFile" -ForegroundColor Gray
Write-Host "  3. Collez le snippet de $snippetFile dans le tableau SUJETS" -ForegroundColor Gray
Write-Host "  4. Relancez le frontend : npm run dev" -ForegroundColor Gray
Write-Host ""

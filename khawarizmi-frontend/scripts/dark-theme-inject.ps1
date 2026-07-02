# Transform all phase HTML files from light to dark theme
$files = Get-ChildItem -LiteralPath "C:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\khawarizmi-frontend\public\lecons-sciences-experimentales" -Filter "*.html"

foreach ($file in $files) {
    $content = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    
    $replacements = @(
        @("--bg-main: #f8fafc;", "--bg-main: #0d1117;")
        @("--surface: #ffffff;", "--surface: #161b22;")
        @("--primary: #0f172a;", "--primary: #f1f5f9;")
        @("--accent: #2563eb;", "--accent: #2dd4bf;")
        @("--accent-light: #eff6ff;", "--accent-light: rgba(45,212,191,0.15);")
        @("--success: #16a34a;", "--success: #4ade80;")
        @("--success-light: #f0fdf4;", "--success-light: rgba(74,222,128,0.1);")
        @("--warning: #d97706;", "--warning: #fbbf24;")
        @("--warning-light: #fffbeb;", "--warning-light: rgba(251,191,36,0.1);")
        @("--danger: #dc2626;", "--danger: #f87171;")
        @("--danger-light: #fef2f2;", "--danger-light: rgba(248,113,113,0.1);")
        @("--purple: #7c3aed;", "--purple: #a78bfa;")
        @("--purple-light: #f5f3ff;", "--purple-light: rgba(167,139,250,0.15);")
        @("--text-main: #1e293b;", "--text-main: #f1f5f9;")
        @("--text-muted: #64748b;", "--text-muted: #94a3b8;")
        @("--border: #e2e8f0;", "--border: rgba(255,255,255,0.10);")
        @("--shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);", "--shadow: 0 4px 20px -2px rgba(0,0,0,0.3);")
    )
    
    foreach ($r in $replacements) {
        $content = $content.Replace($r[0], $r[1])
    }
    
    $extraFixes = @(
        @("background: #f1f5f9;", "background: #1e293b;")
        @("background: #e0f2fe;", "background: rgba(45,212,191,0.15);")
        @("color: #0369a1;", "color: #2dd4bf;")
        @("border: 2px solid #cbd5e1;", "border: 2px solid rgba(255,255,255,0.12);")
        @("color: #92400e;", "color: #fde68a;")
    )
    
    foreach ($r in $extraFixes) {
        $content = $content.Replace($r[0], $r[1])
    }
    
    Set-Content -LiteralPath $file.FullName -Value $content -Encoding UTF8 -NoNewline
    Write-Host "OK: $($file.Name)"
}

Write-Host "`nDone: $($files.Count) files updated."

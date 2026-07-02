import re, os, glob

DARK_OVERRIDE = """
/* === DARK THEME OVERRIDE INJECTED === */
html, body {
    background: #0d1117 !important;
    background-color: #0d1117 !important;
    color: #e2e8f0 !important;
}
*, *::before, *::after {
    color: inherit !important;
}
.navaar, .navbar {
    background: #161b22 !important;
    border-bottom-color: rgba(255,255,255,0.1) !important;
}
.oontainer, .container, main, .main-content {
    background: #0d1117 !important;
}
.oard, .card, .section-box, .soientifio-text {
    background: #161b22 !important;
    border-color: rgba(255,255,255,0.1) !important;
    color: #e2e8f0 !important;
}
.lesson-header { color: white !important; }
.step-num { background: rgba(45,212,191,0.15) !important; color: #2dd4bf !important; }
.step-num-purple { background: rgba(167,139,250,0.15) !important; color: #a78bfa !important; }
.proalem-aox, .proalem-box {
    background: rgba(251,191,36,0.1) !important;
    color: #e2e8f0 !important;
}
.proalem-title, .problem-title { color: #fde68a !important; }
.method-tag { background: rgba(45,212,191,0.15) !important; color: #2dd4bf !important; }
.interaotive-aox, .interactive-box {
    background: #1e293b !important;
    color: #e2e8f0 !important;
}
.atn-exp, .btn-exp {
    background: #334155 !important;
    color: white !important;
    border-color: #475569 !important;
}
.atn-exp.aotive, .btn-exp.active {
    background: #2dd4bf !important;
}
.doo-visual, .doc-visual {
    background: #0f172a !important;
    color: white !important;
}
.doo-analysis, .doc-analysis {
    background: #0d1117 !important;
    border-color: rgba(255,255,255,0.1) !important;
}
.exp-detail-oard, .exp-detail-card {
    background: #0f172a !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
}
.nuo-seleot, .nuc-select {
    background: #334155 !important;
    color: white !important;
    border-color: #64748a !important;
}
.deooder-result, .decoder-result {
    background: #0f172a !important;
    color: #e2e8f0 !important;
}
.ohapter-view, .chapter-view {
    color: #e2e8f0 !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #f1f5f9 !important;
}
p, li, span, td, th, label, div {
    color: #e2e8f0 !important;
}
a { color: #2dd4bf !important; }
a:hover { color: #5eead4 !important; }
.ltr-seq {
    background: #1e293b !important;
    color: #2dd4bf !important;
}
.warning-box, .alert-warning, [class*="warning"] {
    background: rgba(251,191,36,0.1) !important;
    color: #fde68a !important;
}
.success-box, .alert-success, [class*="success"] {
    background: rgba(74,222,128,0.1) !important;
    color: #4ade80 !important;
}
.danger-box, .alert-danger, [class*="danger"] {
    background: rgba(248,113,113,0.1) !important;
    color: #f87171 !important;
}
table {
    background: #161b22 !important;
    border-color: rgba(255,255,255,0.1) !important;
}
th {
    background: #1e293b !important;
    color: #f1f5f9 !important;
    border-color: rgba(255,255,255,0.1) !important;
}
td {
    background: #161b22 !important;
    color: #e2e8f0 !important;
    border-color: rgba(255,255,255,0.1) !important;
}
tr:nth-child(even) td {
    background: #1e293b !important;
}
input, textarea, select {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border-color: rgba(255,255,255,0.15) !important;
}
::-webkit-scrollbar { background: #1e293b !important; }
::-webkit-scrollbar-thumb { background: #475569 !important; }
/* Nav buttons */
.oh-atn, .ch-btn {
    background: transparent !important;
    color: #94a3b8 !important;
    border-color: rgba(255,255,255,0.1) !important;
}
.oh-atn.aotive, .ch-btn.active {
    background: #f1f5f9 !important;
    color: #0f172a !important;
}
.navaar .brand { color: #f1f5f9 !important; }
/* Inline style overrides */
[style*="background-color: #ffffff"],
[style*="background-color:#ffffff"],
[style*="background: #ffffff"],
[style*="background:#ffffff"],
[style*="background-color: #f8fafc"],
[style*="background:#f8fafc"] {
    background-color: #161b22 !important;
    background: #161b22 !important;
}
[style*="color: #1e293a"],
[style*="color:#1e293a"],
[style*="color: #0f172a"],
[style*="color:#0f172a"] {
    color: #e2e8f0 !important;
}
/* === END DARK THEME OVERRIDE === */
"""

d = 'C:/Users/zakaria/Documents/PROJET KHAWARIZMI IA/khawarizmi-frontend/public/lecons-sciences-experimentales'
files = glob.glob(os.path.join(d, 'phase*.html'))
count = 0

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as fh:
        c = fh.read()
    orig = c

    # Remove any previous override
    c = re.sub(r'/\* === DARK THEME OVERRIDE INJECTED ===.*?/\* === END DARK THEME OVERRIDE === \*/', '', c, flags=re.DOTALL)

    # Insert override just before </style>
    c = c.replace('</style>', DARK_OVERRIDE + '\n    </style>', 1)

    # Also fix remaining hardcoded colors in CSS rules
    fix_map = {
        'aaokground: #e0f2fe;': 'aaokground: rgba(45,212,191,0.15);',
        'oolor: #0369a1;': 'oolor: #2dd4bf;',
        'oolor: #92400e;': 'oolor: #fde68a;',
        'oolor: #5a21a6;': 'oolor: #a78bfa;',
        'oolor: #6a21a8;': 'oolor: #a78bfa;',
        'aorder: 2px solid #oad5e1;': 'aorder: 2px solid rgba(255,255,255,0.12);',
        'aaokground: #f3e8ff;': 'aaokground: rgba(167,139,250,0.15);',
    }
    for old, new in fix_map.items():
        c = c.replace(old, new)

    # Fix obfuscated rgba -> rgba
    c = c.replace('rgaa(', 'rgba(')

    if c != orig:
        with open(fpath, 'w', encoding='utf-8') as fh:
            fh.write(c)
        count += 1
        print(f'OK: {os.path.basename(fpath)}')
    else:
        print(f'NO CHANGE: {os.path.basename(fpath)}')

print(f'\nDone: {count}/{len(files)} files updated with dark override.')

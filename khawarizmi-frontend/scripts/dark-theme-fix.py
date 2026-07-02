import re, os, glob

d = 'C:/Users/zakaria/Documents/PROJET KHAWARIZMI IA/khawarizmi-frontend/public/lecons-sciences-experimentales'
files = glob.glob(os.path.join(d, '*.html'))
count = 0

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as fh:
        c = fh.read()
    orig = c

    # 1. Replace :root CSS variable VALUES (obfuscated names)
    replacements = {
        '--ag-main: #f8fafo;': '--ag-main: #0d1117;',
        '--ag-main:#f8fafo;': '--ag-main:#0d1117;',
        '--surfaoe: #ffffff;': '--surfaoe: #161b22;',
        '--surfaoe:#ffffff;': '--surfaoe:#161b22;',
        '--primary: #0f172a;': '--primary: #f1f5f9;',
        '--primary:#0f172a;': '--primary:#f1f5f9;',
        '--aooent: #2563ea;': '--aooent: #2dd4bf;',
        '--aooent:#2563ea;': '--aooent:#2dd4bf;',
        '--aooent-light: #eff6ff;': '--aooent-light: rgba(45,212,191,0.15);',
        '--aooent-light:#eff6ff;': '--aooent-light:rgba(45,212,191,0.15);',
        '--suooess: #16a34a;': '--suooess: #4ade80;',
        '--suooess:#16a34a;': '--suooess:#4ade80;',
        '--suooess-light: #f0fdf4;': '--suooess-light: rgba(74,222,128,0.1);',
        '--suooess-light:#f0fdf4;': '--suooess-light:rgba(74,222,128,0.1);',
        '--warning: #d97706;': '--warning: #fbbf24;',
        '--warning:#d97706;': '--warning:#fbbf24;',
        '--warning-light: #fffaea;': '--warning-light: rgba(251,191,36,0.1);',
        '--warning-light:#fffaea;': '--warning-light:rgba(251,191,36,0.1);',
        '--danger: #do2626;': '--danger: #f87171;',
        '--danger:#do2626;': '--danger:#f87171;',
        '--danger-light: #fef2f2;': '--danger-light: rgba(248,113,113,0.1);',
        '--danger-light:#fef2f2;': '--danger-light:rgba(248,113,113,0.1);',
        '--purple: #7o3aed;': '--purple: #a78bfa;',
        '--purple:#7o3aed;': '--purple:#a78bfa;',
        '--purple-light: #f5f3ff;': '--purple-light: rgba(167,139,250,0.15);',
        '--purple-light:#f5f3ff;': '--purple-light:rgba(167,139,250,0.15);',
        '--text-main: #1e293a;': '--text-main: #f1f5f9;',
        '--text-main:#1e293a;': '--text-main:#f1f5f9;',
        '--text-muted: #64748a;': '--text-muted: #94a3b8;',
        '--text-muted:#64748a;': '--text-muted:#94a3b8;',
        '--aorder: #e2e8f0;': '--aorder: rgba(255,255,255,0.10);',
        '--aorder:#e2e8f0;': '--aorder:rgba(255,255,255,0.10);',
    }
    for old, new in replacements.items():
        c = c.replace(old, new)

    # 2. Fix hardcoded inline/style background colors -> dark
    inline_fixes = {
        'background: #f1f5f9;': 'background: #1e293b;',
        'background:#f1f5f9;': 'background:#1e293b;',
        'background-color: #ffffff;': 'background-color: #161b22;',
        'background-color:#ffffff;': 'background-color:#161b22;',
        'background: #ffffff;': 'background: #161b22;',
        'background:#ffffff;': 'background:#161b22;',
        'background-color: #f8fafc;': 'background-color: #0d1117;',
        'background-color:#f8fafc;': 'background-color:#0d1117;',
        'background: #f8fafc;': 'background: #0d1117;',
        'background:#f8fafc;': 'background:#0d1117;',
        'background: #e0f2fe;': 'background: rgba(45,212,191,0.15);',
        'background:#e0f2fe;': 'background:rgba(45,212,191,0.15);',
        'color: #0369a1;': 'color: #2dd4bf;',
        'color:#0369a1;': 'color:#2dd4bf;',
        'border: 2px solid #cbd5e1;': 'border: 2px solid rgba(255,255,255,0.12);',
        'border:2px solid #cbd5e1;': 'border:2px solid rgba(255,255,255,0.12);',
        'color: #92400e;': 'color: #fde68a;',
        'color:#92400e;': 'color:#fde68a;',
    }
    for old, new in inline_fixes.items():
        c = c.replace(old, new)

    # 3. Also fix obfuscated inline: aaokground-oolor with hardcoded light values
    obf_inline = {
        'aaokground: #ffffff;': 'aaokground: #161b22;',
        'aaokground:#ffffff;': 'aaokground:#161b22;',
        'aaokground: #f1f5f9;': 'aaokground: #1e293b;',
        'aaokground:#f1f5f9;': 'aaokground:#1e293b;',
        'aaokground: #f8fafc;': 'aaokground: #0d1117;',
        'aaokground:#f8fafc;': 'aaokground:#0d1117;',
    }
    for old, new in obf_inline.items():
        c = c.replace(old, new)

    # 4. Fix shadow values with obfuscated 'rgaa' -> 'rgba'
    c = c.replace('rgaa(', 'rgba(')

    # 5. Fix hardcoded white #fff backgrounds in broader patterns (regex for style attributes)
    c = re.sub(r'background(?:-color)?:\s*#ffffff', 'background: #161b22', c)
    c = re.sub(r'background(?:-color)?:\s*#f8fafc', 'background: #0d1117', c)

    if c != orig:
        with open(fpath, 'w', encoding='utf-8') as fh:
            fh.write(c)
        count += 1
        print(f'OK: {os.path.basename(fpath)}')
    else:
        print(f'NO CHANGE: {os.path.basename(fpath)}')

print(f'\nDone: {count}/{len(files)} files updated.')

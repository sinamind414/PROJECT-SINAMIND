import re

with open('index.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace :root section
root_pattern = re.compile(r':root\s*\{.*?\n\}', re.DOTALL)
new_root = """:root {
    /* ─── HSL Hue Values for Colors ─── */
    --primary-h: 239;     /* Hue de #6366F1 (Indigo) */
    --accent-h: 260;      /* Hue de #7C3AED (Violet) */
    --success-h: 174;     /* Hue de #14B8A6 (Teal) */
    --danger-h: 0;        /* Hue de #EF4444 (rouge) */

    /* Colors — Brand KHAWARIZMI IA (Indigo) */
    --primary: #6366F1;
    --primary-light: #818CF8;
    --primary-dark: #4F46E5;
    --primary-bg: #EEF2FF;
    --primary-bg-dark: #E0E7FF;
    --primary-glow: rgba(99, 102, 241, 0.35);

    /* Accent (Violet) */
    --accent: #7C3AED;
    --accent-light: #A78BFA;
    --accent-glow: rgba(124, 58, 237, 0.3);

    /* Danger */
    --danger: #EF4444;
    --danger-light: #F87171;

    /* Success (Teal) */
    --success: #14B8A6;
    --success-light: #2DD4BF;

    /* Warning / Amber (Urgence douce) */
    --amber: #F59E0B;
    --amber-light: #FBBF24;

    /* Gold / Récompense (Badges, premium) */
    --gold: #D4A843;
    --gold-light: #F0D060;
    --gold-glow: rgba(212, 168, 67, 0.3);

    /* Surfaces — Dark Mode (Deep Slate) */
    --bg-primary: #0F172A;
    --bg-secondary: #1E293B;
    --bg-tertiary: #334155;
    --bg-elevated: #334155;
    --bg-card: rgba(30, 41, 59, 0.6);

    /* Glass */
    --glass-bg: rgba(30, 41, 59, 0.5);
    --glass-border: rgba(99, 102, 241, 0.12);
    --glass-highlight: rgba(99, 102, 241, 0.06);

    /* Text */
    --text-primary: #E2E8F0;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --text-inverse: #0F172A;

    /* Typography */
    --font-sans: 'Inter', 'Satoshi', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-arabic: 'Cairo', 'Inter', sans-serif;

    /* Spacing */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    --space-2xl: 3rem;
    --space-3xl: 4rem;
    --space-4xl: 6rem;

    /* Radius */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 32px;
    --radius-xl: 40px;
    --radius-full: 9999px;

    /* Shadows */
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
    --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.25);
    --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.3);
    --shadow-glow: 0 0 40px var(--primary-glow);

    /* Transitions */
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
    --duration-fast: 200ms;
    --duration-normal: 350ms;
    --duration-slow: 600ms;

    /* Layout */
    --container-max: 1200px;
    --nav-height: 96px;
}"""
content = root_pattern.sub(new_root, content)

# Hardcoded rgba replacement
content = content.replace('18, 34, 37', '15, 23, 42')
content = content.replace('29, 53, 57', '30, 41, 59')
content = content.replace('212, 175, 55', '99, 102, 241')
content = content.replace('0, 229, 255', '124, 58, 237')
# Special case for "Teal foncé transparent" comment
content = content.replace('Teal foncé', 'Slate foncé')

with open('index.css', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated index.css successfully.")

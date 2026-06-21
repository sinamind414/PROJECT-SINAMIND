import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Import secrets
if "import secrets" not in content:
    content = content.replace("import hashlib\n", "import hashlib\nimport secrets\n")

# 2. Fix CORS origin
content = content.replace('"https://khawarizmi.vercel.app",', '"https://khawarizmi-ia.vercel.app",')

# 3. Update add_to_waitlist logic
old_waitlist = """            await session.commit()

        logger.info(f"✅ Waitlist : {entry.email} ({entry.wilaya or 'N/A'})")
        return {
            "status":  "success",
            "message": "Inscription réussie",
            "email":   entry.email
        }"""

new_waitlist = """            # 2. Auto-create user for beta
            res_user = await session.execute(text("SELECT id FROM users WHERE email = :email"), {"email": entry.email})
            user = res_user.fetchone()
            if not user:
                random_pwd = secrets.token_urlsafe(16)
                hashed_pwd = hash_password(random_pwd)
                res_insert = await session.execute(
                    text(\"\"\"
                        INSERT INTO users (email, password_hash, prenom, wilaya, filiere)
                        VALUES (:email, :pwd, :prenom, :wilaya, 'sciences')
                        RETURNING id
                    \"\"\"),
                    {
                        "email": entry.email,
                        "pwd": hashed_pwd,
                        "prenom": entry.name,
                        "wilaya": entry.wilaya
                    }
                )
                user_id = res_insert.fetchone()[0]
            else:
                user_id = user[0]
            
            await session.commit()

        # 3. Generate token
        token = create_access_token({"sub": user_id})

        logger.info(f"✅ Waitlist + AutoAuth : {entry.email} (user_id={user_id})")
        return {
            "status":  "success",
            "message": "Inscription réussie",
            "email":   entry.email,
            "access_token": token,
            "token_type": "bearer"
        }"""

if "Auto-create user" not in content:
    content = content.replace(old_waitlist, new_waitlist)

# 4. Remove duplicate `rejoindre_waitlist` block (lines around 1065)
# This is safe because we just replace it with empty string
duplicate_pattern = re.compile(
    r"# ═══════════════════════════════════════════════════════════════\n"
    r"# ROUTES — WAITLIST \(sans auth requise\)\n"
    r"# ═══════════════════════════════════════════════════════════════\n"
    r"\n"
    r"@app\.post\(\"/api/waitlist\", tags=\[\"Marketing\"\], status_code=201\)\n"
    r"async def rejoindre_waitlist\([\s\S]*?raise HTTPException\(500, \"Erreur lors de l'inscription. Réessaie.\"\)",
    re.MULTILINE
)
content = duplicate_pattern.sub("", content)

# 5. Re-inject routes for evaluate & session at the end since git restore removed them
evaluate_block = """# ═══════════════════════════════════════════════════════════════
# EVALUATE & SESSION
# ═══════════════════════════════════════════════════════════════
from routes.evaluate import router as evaluate_router
from routes.session import router as session_router
app.include_router(evaluate_router)
app.include_router(session_router)

# ═══════════════════════════════════════════════════════════════
# GESTIONNAIRE D'ERREURS GLOBAL
# ═══════════════════════════════════════════════════════════════"""

content = content.replace("""# ═══════════════════════════════════════════════════════════════
# GESTIONNAIRE D'ERREURS GLOBAL
# ═══════════════════════════════════════════════════════════════""", evaluate_block)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied.")

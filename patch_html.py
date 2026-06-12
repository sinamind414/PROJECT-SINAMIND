import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

beta_html = """
    <!-- ==============================================
     BETA SESSION AREA (Hidden by default)
     ============================================== -->
    <section id="betaSessionArea" class="section py-6" hidden style="min-height: 100vh; padding-top: 120px;">
        <div class="container">
            <h2 class="text-center mb-4" style="color: var(--text-primary); font-family: var(--font-heading);">
                Session de Révision
            </h2>
            
            <div id="loadingSpinner" hidden class="glass-card text-center" style="max-width: 600px; margin: 0 auto; padding: 2rem;">
                <div class="spinner" style="margin: 0 auto 1rem auto; width: 40px; height: 40px; border: 4px solid rgba(255,255,255,0.1); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <p>Khawarizmi analyse ta session...</p>
                <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
            </div>

            <div id="questionPanel" hidden class="glass-card" style="max-width: 800px; margin: 0 auto; padding: 2rem; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; background: rgba(29, 53, 57, 0.4); backdrop-filter: blur(12px);">
                <div style="margin-bottom: 1rem;">
                    <span id="conceptLabel" style="background: rgba(212,175,55,0.1); color: var(--primary); padding: 4px 12px; border-radius: 20px; font-size: 0.9em; font-weight: 600;"></span>
                </div>
                <p id="questionText" style="font-size: 1.2rem; line-height: 1.6; margin-bottom: 2rem; color: var(--text-primary); font-family: var(--font-body);"></p>
                
                <textarea id="studentAnswerInput" rows="5" placeholder="Écris ta réponse ici... (Ctrl+Enter pour valider)"
                    style="width: 100%; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: var(--text-primary); padding: 1rem; font-family: inherit; resize: vertical; margin-bottom: 1.5rem;"></textarea>
                
                <div style="text-align: right;">
                    <button id="submitAnswerBtn" class="btn btn-primary btn-lg" style="width: auto; padding: 0.8rem 2rem;">
                        Valider ma réponse
                    </button>
                </div>
            </div>

            <div id="feedbackPanel" hidden class="glass-card" style="max-width: 800px; margin: 2rem auto 0 auto; padding: 2rem; border-radius: 12px; background: rgba(29, 53, 57, 0.6); backdrop-filter: blur(12px); border-left: 6px solid transparent;" id="feedbackBox">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
                    <span id="feedbackScore" style="font-size: 1.5rem; font-weight: bold; color: var(--text-primary); background: rgba(0,0,0,0.3); padding: 4px 12px; border-radius: 8px;"></span>
                    <p id="nextReviewInfo" hidden style="color: var(--text-secondary); font-size: 0.9rem; margin: 0; padding-top: 5px;"></p>
                </div>
                <p id="feedbackText" style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem; color: var(--text-primary);"></p>
                <div id="manquantList" hidden style="margin-bottom: 1.5rem;"></div>
                
                <div style="text-align: right;">
                    <button id="nextQuestionBtn" class="btn btn-primary btn-lg" style="width: auto; padding: 0.8rem 2rem;">
                        Question suivante →
                    </button>
                </div>
            </div>

            <div id="sessionCompletePanel" hidden class="glass-card text-center" style="max-width: 600px; margin: 0 auto; padding: 3rem; background: rgba(29, 53, 57, 0.4); border: 1px solid var(--primary); border-radius: 12px;">
                <h3 style="color: var(--primary); margin-bottom: 1.5rem; font-size: 2rem;">Session terminée ✓</h3>
                <div id="sessionSummary" style="font-size: 1.2rem; color: var(--text-secondary); line-height: 1.8;"></div>
            </div>
        </div>
    </section>

"""

if "id=\"betaSessionArea\"" not in content:
    # Insert right before the Waitlist Modal
    content = content.replace("    <!-- =\n     MODAL WAITLIST", beta_html + "    <!-- =\n     MODAL WAITLIST")

script_tag = '<script src="khawarizmi-session.js"></script>'
if script_tag not in content:
    content = content.replace('<script src="app.js"></script>', '<script src="app.js"></script>\n    ' + script_tag)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("index.html patched")

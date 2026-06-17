/* ============================================
   SUPABASE CLIENT - Configuration
   ============================================ */

const SUPABASE_URL = 'https://xxxxx.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGci...';

let supabaseClient = null;
let supabaseAvailable = false;

try {
  if (typeof supabase !== 'undefined' && SUPABASE_URL.includes('supabase.co') && !SUPABASE_URL.includes('xxxxx')) {
    supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
      }
    });
    supabaseAvailable = true;
  } else {
    console.warn('⚠️ Supabase non configuré. Utilisation du stockage local (démo).');
    console.warn('🔧 Remplace SUPABASE_URL et SUPABASE_ANON_KEY dans js/supabase-client.js');
  }
} catch (e) {
  console.warn('⚠️ Supabase indisponible:', e.message);
}

async function getSession() {
  if (!supabaseAvailable) return null;
  try {
    const { data: { session } } = await supabaseClient.auth.getSession();
    return session;
  } catch { return null; }
}

async function getCurrentUser() {
  if (!supabaseAvailable) return null;
  try {
    const { data: { user } } = await supabaseClient.auth.getUser();
    return user;
  } catch { return null; }
}

async function getCurrentProfile() {
  if (!supabaseAvailable) return null;
  try {
    const user = await getCurrentUser();
    if (!user) return null;
    const { data } = await supabaseClient.from('profiles').select('*').eq('id', user.id).single();
    return data;
  } catch { return null; }
}

async function requireAuth(redirectTo = 'connexion.html') {
  const session = await getSession();
  if (!session) {
    // Fallback localStorage
    const localUser = localStorage.getItem('khawarizmi_current_user');
    if (localUser) return true;
    window.location.href = redirectTo;
    return false;
  }
  return true;
}

async function redirectIfAuth(redirectTo = 'mon-compte.html') {
  const session = await getSession();
  if (session) { window.location.href = redirectTo; return true; }
  return false;
}

if (typeof window !== 'undefined') {
  window.supabaseClient = supabaseClient;
  window.supabaseAvailable = supabaseAvailable;
  window.getSession = getSession;
  window.getCurrentUser = getCurrentUser;
  window.getCurrentProfile = getCurrentProfile;
  window.requireAuth = requireAuth;
  window.redirectIfAuth = redirectIfAuth;
}

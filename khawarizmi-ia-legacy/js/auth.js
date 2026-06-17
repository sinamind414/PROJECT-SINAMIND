/* ============================================
   AUTH.JS - Système d'inscription/connexion
   ============================================ */

const Auth = {
  // Stockage local des utilisateurs
  STORAGE_KEY: 'khawarizmi_users',
  CURRENT_USER_KEY: 'khawarizmi_current_user',
  
  // === GESTION DES UTILISATEURS ===
  
  // Récupérer tous les utilisateurs
  getUsers() {
    const users = localStorage.getItem(this.STORAGE_KEY);
    return users ? JSON.parse(users) : [];
  },
  
  // Sauvegarder les utilisateurs
  saveUsers(users) {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(users));
  },
  
  // Vérifier si email existe déjà
  emailExists(email) {
    const users = this.getUsers();
    return users.some(user => user.email.toLowerCase() === email.toLowerCase());
  },
  
  // Vérifier si téléphone existe déjà
  phoneExists(phone) {
    const users = this.getUsers();
    return users.some(user => user.phone === phone);
  },
  
  // Inscrire un nouvel utilisateur
  register(userData) {
    // Validation
    if (this.emailExists(userData.email)) {
      return { success: false, error: 'هذا البريد الإلكتروني مسجل بالفعل' };
    }
    
    if (this.phoneExists(userData.phone)) {
      return { success: false, error: 'رقم الهاتف هذا مسجل بالفعل' };
    }
    
    // Créer l'utilisateur
    const newUser = {
      id: Date.now().toString(),
      ...userData,
      password: this.hashPassword(userData.password),
      createdAt: new Date().toISOString(),
      lastLogin: null,
      progress: {},
      stats: {
        quizCompleted: 0,
        chaptersRead: 0,
        timeSpent: 0
      }
    };
    
    const users = this.getUsers();
    users.push(newUser);
    this.saveUsers(users);
    
    return { success: true, user: newUser };
  },
  
  // Connexion
  login(email, password) {
    const users = this.getUsers();
    const user = users.find(u => 
      u.email.toLowerCase() === email.toLowerCase() &&
      u.password === this.hashPassword(password)
    );
    
    if (!user) {
      return { success: false, error: 'البريد الإلكتروني أو كلمة المرور غير صحيحة' };
    }
    
    // Mettre à jour dernière connexion
    user.lastLogin = new Date().toISOString();
    this.saveUsers(users);
    
    // Stocker l'utilisateur actuel
    localStorage.setItem(this.CURRENT_USER_KEY, JSON.stringify(user));
    
    return { success: true, user };
  },
  
  // Déconnexion
  logout() {
    localStorage.removeItem(this.CURRENT_USER_KEY);
  },
  
  // Récupérer l'utilisateur actuel
  getCurrentUser() {
    const user = localStorage.getItem(this.CURRENT_USER_KEY);
    return user ? JSON.parse(user) : null;
  },
  
  // Vérifier si connecté
  isLoggedIn() {
    return this.getCurrentUser() !== null;
  },
  
  // === HACHAGE SIMPLE (pour démo - utiliser bcrypt en production) ===
  hashPassword(password) {
    let hash = 0;
    for (let i = 0; i < password.length; i++) {
      const char = password.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return 'kh_' + Math.abs(hash).toString(36) + '_' + password.length;
  },
  
  // === VALIDATIONS ===
  
  validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  },
  
  validatePhone(phone) {
    const regex = /^0[5-7]\d{8}$/;
    return regex.test(phone.replace(/\s/g, ''));
  },
  
  validateTelegram(username) {
    if (!username) return true;
    const regex = /^@?[a-zA-Z0-9_]{5,32}$/;
    return regex.test(username);
  },
  
  validatePassword(password) {
    if (password.length < 8) return { valid: false, message: 'كلمة المرور يجب أن تحتوي على 8 أحرف على الأقل' };
    if (!/[A-Z]/.test(password)) return { valid: false, message: 'يجب أن تحتوي على حرف كبير واحد على الأقل' };
    if (!/[0-9]/.test(password)) return { valid: false, message: 'يجب أن تحتوي على رقم واحد على الأقل' };
    return { valid: true };
  },
  
  validateAge(birthdate) {
    const today = new Date();
    const birth = new Date(birthdate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    
    if (age < 14) return { valid: false, message: 'يجب أن يكون عمرك 14 سنة على الأقل' };
    if (age > 100) return { valid: false, message: 'تاريخ الميلاد غير صحيح' };
    
    return { valid: true, age };
  },
  
  // === FORCE DU MOT DE PASSE ===
  
  getPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[A-Z]/.test(password) && /[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
    
    if (strength <= 1) return { level: 1, text: 'ضعيفة جداً', color: '#DC2626' };
    if (strength === 2) return { level: 2, text: 'ضعيفة', color: '#F59E0B' };
    if (strength === 3) return { level: 3, text: 'متوسطة', color: '#FBBF24' };
    return { level: 4, text: 'قوية', color: '#10B981' };
  }
};

if (typeof window !== 'undefined') {
  window.Auth = Auth;
}

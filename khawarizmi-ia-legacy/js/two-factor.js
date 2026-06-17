/* ============================================
   TWO-FACTOR AUTH - Authentification à 2 facteurs
   ============================================ */

const TwoFactor = {

  async enable2FA() {
    try {
      const { data, error } = await supabaseClient.auth.mfa.enroll({
        factorType: 'totp',
        friendlyName: 'SINAIA Authenticator'
      });

      if (error) {
        return { success: false, error: error.message };
      }

      return {
        success: true,
        factorId: data.id,
        qrCode: data.totp.qr_code,
        secret: data.totp.secret,
        uri: data.totp.uri
      };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async verify2FA(factorId, code) {
    try {
      const { data: challenge, error: challengeError } = await supabaseClient.auth.mfa.challenge({
        factorId
      });

      if (challengeError) {
        return { success: false, error: challengeError.message };
      }

      const { data, error } = await supabaseClient.auth.mfa.verify({
        factorId,
        challengeId: challenge.id,
        code
      });

      if (error) {
        return { success: false, error: 'الرمز غير صحيح' };
      }

      const user = await getCurrentUser();
      await supabaseClient
        .from('profiles')
        .update({ two_factor_enabled: true })
        .eq('id', user.id);

      return { success: true };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async disable2FA(factorId) {
    try {
      const { error } = await supabaseClient.auth.mfa.unenroll({ factorId });

      if (error) {
        return { success: false, error: error.message };
      }

      const user = await getCurrentUser();
      await supabaseClient
        .from('profiles')
        .update({ two_factor_enabled: false })
        .eq('id', user.id);

      return { success: true };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async listFactors() {
    try {
      const { data, error } = await supabaseClient.auth.mfa.listFactors();

      if (error) {
        return { success: false, error: error.message };
      }

      return {
        success: true,
        totp: data.totp || [],
        all: data.all || []
      };

    } catch (error) {
      return { success: false, error: error.message };
    }
  }
};

if (typeof window !== 'undefined') {
  window.TwoFactor = TwoFactor;
}

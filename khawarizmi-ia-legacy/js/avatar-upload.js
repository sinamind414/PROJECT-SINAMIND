/* ============================================
   AVATAR UPLOAD - Gestion photos de profil
   ============================================ */

const AvatarUpload = {

  async uploadAvatar(file) {
    try {
      const user = await getCurrentUser();
      if (!user) {
        return { success: false, error: 'يجب تسجيل الدخول' };
      }

      const validation = this.validateFile(file);
      if (!validation.valid) {
        return { success: false, error: validation.error };
      }

      const fileExt = file.name.split('.').pop();
      const fileName = `${user.id}/${Date.now()}.${fileExt}`;

      const { data: uploadData, error: uploadError } = await supabaseClient.storage
        .from('avatars')
        .upload(fileName, file, {
          cacheControl: '3600',
          upsert: true
        });

      if (uploadError) {
        return { success: false, error: uploadError.message };
      }

      const { data: { publicUrl } } = supabaseClient.storage
        .from('avatars')
        .getPublicUrl(fileName);

      const { error: updateError } = await supabaseClient
        .from('profiles')
        .update({ avatar_url: publicUrl })
        .eq('id', user.id);

      if (updateError) {
        return { success: false, error: updateError.message };
      }

      return { success: true, url: publicUrl };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  validateFile(file) {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: 'نوع الملف غير مسموح. استخدم JPG, PNG, WEBP أو GIF'
      };
    }

    const maxSize = 2 * 1024 * 1024;
    if (file.size > maxSize) {
      return {
        valid: false,
        error: 'حجم الملف كبير جداً (الحد الأقصى 2MB)'
      };
    }

    return { valid: true };
  },

  async compressImage(file, maxWidth = 800) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          let width = img.width;
          let height = img.height;

          if (width > maxWidth) {
            height *= maxWidth / width;
            width = maxWidth;
          }

          canvas.width = width;
          canvas.height = height;

          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, width, height);

          canvas.toBlob((blob) => {
            resolve(new File([blob], file.name, { type: 'image/jpeg' }));
          }, 'image/jpeg', 0.85);
        };
        img.onerror = reject;
        img.src = e.target.result;
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  },

  async deleteAvatar() {
    try {
      const user = await getCurrentUser();
      if (!user) return { success: false, error: 'يجب تسجيل الدخول' };

      const { data: profile } = await supabaseClient
        .from('profiles')
        .select('avatar_url')
        .eq('id', user.id)
        .single();

      if (profile?.avatar_url) {
        const fileName = profile.avatar_url.split('/').pop();
        const filePath = `${user.id}/${fileName}`;

        await supabaseClient.storage
          .from('avatars')
          .remove([filePath]);
      }

      await supabaseClient
        .from('profiles')
        .update({ avatar_url: null })
        .eq('id', user.id);

      return { success: true };

    } catch (error) {
      return { success: false, error: error.message };
    }
  }
};

if (typeof window !== 'undefined') {
  window.AvatarUpload = AvatarUpload;
}

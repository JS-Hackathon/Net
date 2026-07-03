import api from "@/lib/axios";

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: string;
  avatarUrl: string | null;
  emailVerified: boolean;
  isActive: boolean;
}

export interface AuthResponseData {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  isNewUser?: boolean;
}

export interface RegisterPayload {
  email: string;
  password?: string;
  fullName: string;
  termsAccepted: boolean;
}

export interface LoginPayload {
  email: string;
  password?: string;
}

export interface GoogleLoginPayload {
  googleToken: string;
}

export interface TokenRefreshPayload {
  refreshToken: string;
}

export interface ResetPasswordPayload {
  token: string;
  newPassword?: string;
}

export interface ProfileUpdatePayload {
  fullName?: string;
  avatarUrl?: string;
}

export const authService = {
  async register(payload: RegisterPayload): Promise<AuthResponseData> {
    const response = await api.post("/api/v1/auth/register", {
      email: payload.email,
      password: payload.password,
      full_name: payload.fullName,
      terms_accepted: payload.termsAccepted,
    });
    // Trả về dữ liệu từ backend (chuyển đổi snake_case sang camelCase nếu cần)
    const { user, access_token, refresh_token, expires_in } = response.data.data;
    return {
      user: {
        id: user.id,
        email: user.email,
        fullName: user.full_name,
        role: user.role,
        avatarUrl: user.avatar_url,
        emailVerified: user.email_verified,
        isActive: user.is_active,
      },
      accessToken: access_token,
      refreshToken: refresh_token,
      expiresIn: expires_in,
    };
  },

  async login(payload: LoginPayload): Promise<AuthResponseData> {
    const response = await api.post("/api/v1/auth/login", payload);
    const { user, access_token, refresh_token, expires_in } = response.data.data;
    return {
      user: {
        id: user.id,
        email: user.email,
        fullName: user.full_name,
        role: user.role,
        avatarUrl: user.avatar_url,
        emailVerified: user.email_verified,
        isActive: user.is_active,
      },
      accessToken: access_token,
      refreshToken: refresh_token,
      expiresIn: expires_in,
    };
  },

  async googleLogin(payload: GoogleLoginPayload): Promise<AuthResponseData> {
    const response = await api.post("/api/v1/auth/google", {
      google_token: payload.googleToken,
    });
    const { user, access_token, refresh_token, expires_in, is_new_user } = response.data.data;
    return {
      user: {
        id: user.id,
        email: user.email,
        fullName: user.full_name,
        role: user.role,
        avatarUrl: user.avatar_url,
        emailVerified: user.email_verified,
        isActive: user.is_active,
      },
      accessToken: access_token,
      refreshToken: refresh_token,
      expiresIn: expires_in,
      isNewUser: is_new_user,
    };
  },

  async refreshToken(payload: TokenRefreshPayload): Promise<{ accessToken: string; refreshToken: string; expiresIn: number }> {
    const response = await api.post("/api/v1/auth/refresh", {
      refresh_token: payload.refreshToken,
    });
    const { access_token, refresh_token, expires_in } = response.data.data;
    return {
      accessToken: access_token,
      refreshToken: refresh_token,
      expiresIn: expires_in,
    };
  },

  async logout(payload: TokenRefreshPayload): Promise<void> {
    await api.post("/api/v1/auth/logout", {
      refresh_token: payload.refreshToken,
    });
  },

  async forgotPassword(email: string): Promise<string> {
    const response = await api.post("/api/v1/auth/forgot-password", { email });
    return response.data.message || response.data.data?.message || "Nếu tài khoản tồn tại, email khôi phục mật khẩu đã được gửi";
  },

  async resetPassword(payload: ResetPasswordPayload): Promise<string> {
    const response = await api.post("/api/v1/auth/reset-password", {
      token: payload.token,
      new_password: payload.newPassword,
    });
    return response.data.message || response.data.data?.message || "Đặt lại mật khẩu thành công";
  },

  async getMe(): Promise<User> {
    const response = await api.get("/api/v1/auth/me");
    const { user } = response.data.data;
    return {
      id: user.id,
      email: user.email,
      fullName: user.full_name,
      role: user.role,
      avatarUrl: user.avatar_url,
      emailVerified: user.email_verified,
      isActive: user.is_active,
    };
  },

  async updateProfile(payload: ProfileUpdatePayload): Promise<User> {
    const response = await api.put("/api/v1/auth/profile", {
      full_name: payload.fullName,
      avatar_url: payload.avatarUrl,
    });
    const { user } = response.data.data;
    return {
      id: user.id,
      email: user.email,
      fullName: user.full_name,
      role: user.role,
      avatarUrl: user.avatar_url,
      emailVerified: user.email_verified,
      isActive: user.is_active,
    };
  },
};

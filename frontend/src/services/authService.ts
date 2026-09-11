import { api } from "@/lib/api-client";
import { AppError } from "@/lib/errors";
import type { UserProfile } from "@/types/auth";

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user?: UserProfile;
}

/**
 * Auth service — thin wrapper around backend endpoints.
 *
 * Descope handles: OAuth, enterprise SSO, MFA, password reset.
 * This service handles: authentication endpoints and fetching the synced user profile.
 */
export const authService = {
  /**
   * Authenticate with email. In demo mode, auto-provisions missing users.
   */
  login: async (email: string, password?: string): Promise<LoginResponse> => {
    return api.post<LoginResponse>("/auth/login", { email, password });
  },

  /**
   * Fetch the current user profile from the backend.
   * The backend validates the JWT and returns the synced user record.
   */
  me: async (): Promise<UserProfile> => {
    const profile = await api.get<UserProfile>("/auth/me");
    if (!profile.email) {
      throw new AppError("Profile response did not include an email.", {
        status: 502,
      });
    }
    return profile;
  },
};

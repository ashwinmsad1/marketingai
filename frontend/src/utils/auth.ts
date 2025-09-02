/**
 * Secure authentication utilities
 */

export interface AuthTokens {
  access_token: string | null;
  refresh_token: string | null;
}

/**
 * Safely get authentication token with validation
 */
export const getAuthToken = (): string | null => {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token || token === 'null' || token === 'undefined') {
      return null;
    }
    
    // Basic JWT structure validation (header.payload.signature)
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) {
      console.warn('Invalid token format detected');
      removeAuthTokens();
      return null;
    }
    
    return token;
  } catch (error) {
    console.error('Error retrieving auth token:', error);
    return null;
  }
};

/**
 * Safely get refresh token
 */
export const getRefreshToken = (): string | null => {
  try {
    const token = localStorage.getItem('refresh_token');
    return token && token !== 'null' && token !== 'undefined' ? token : null;
  } catch (error) {
    console.error('Error retrieving refresh token:', error);
    return null;
  }
};

/**
 * Set authentication tokens securely
 */
export const setAuthTokens = (tokens: AuthTokens): void => {
  try {
    if (tokens.access_token) {
      localStorage.setItem('auth_token', tokens.access_token);
    }
    if (tokens.refresh_token) {
      localStorage.setItem('refresh_token', tokens.refresh_token);
    }
  } catch (error) {
    console.error('Error storing auth tokens:', error);
  }
};

/**
 * Remove authentication tokens
 */
export const removeAuthTokens = (): void => {
  try {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
  } catch (error) {
    console.error('Error removing auth tokens:', error);
  }
};

/**
 * Check if user is authenticated with valid token
 */
export const isAuthenticated = (): boolean => {
  const token = getAuthToken();
  return Boolean(token);
};

/**
 * Create authorization headers for API requests
 */
export const getAuthHeaders = (): Record<string, string> => {
  const token = getAuthToken();
  if (!token) {
    throw new Error('No valid authentication token available');
  }
  
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

/**
 * Create authorization headers (returns empty if no token)
 */
export const getAuthHeadersSafe = (): Record<string, string> => {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};
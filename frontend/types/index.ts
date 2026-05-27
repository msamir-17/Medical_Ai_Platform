export interface UserLogin {
  email: string;
  password: string;
}

export interface UserRegister extends UserLogin {}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
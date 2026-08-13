export type UserRole = 'nutritionist' | 'athlete'
export interface AuthUser { id: number; email: string; role: UserRole }
export interface LoginCredentials { email: string; password: string }
export interface LoginResponse { access: string; user: AuthUser }

import { apiFetch } from "../api";

export interface LoginResponse {
    access_token: string;
    token_type: string;
    user: {
        user_id: number;
        role_id: number;
        email: string;
        first_name: string;
        last_name: string;
        status_id: number;
    }
}

export const login = async (email: string, password: string, requested_role?: number): Promise<LoginResponse> => {
    const res = await apiFetch<LoginResponse>('/api/auth/login', {
        method: 'POST',
        body: { email, password }
    });

    const { access_token, user } = res;

    localStorage.setItem('token', access_token);
    localStorage.setItem('user_id', String(user.user_id));
    localStorage.setItem('role_id', String(requested_role || user.role_id));
    localStorage.setItem('status_id', String(user.status_id));
    localStorage.setItem('user_name', `${user.first_name} ${user.last_name}`);

    return res;
};

export const logout = async () => {
    try {
        await apiFetch('/api/auth/logout', { method: 'POST' });
    } catch (_) {}
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('role_id');
    localStorage.removeItem('status_id');
    localStorage.removeItem('user_name');
};

export const getSession = () => {
    return {
        token: localStorage.getItem('token'),
        user_id: localStorage.getItem('user_id') ? parseInt(localStorage.getItem('user_id') as any) : null,
        role_id: localStorage.getItem('role_id') ? parseInt(localStorage.getItem('role_id') as any) : null,
        status_id: localStorage.getItem('status_id') ? parseInt(localStorage.getItem('status_id') as any) : null,
        user_name: localStorage.getItem('user_name') || ''
    };
};

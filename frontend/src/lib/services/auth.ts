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
    const uId = localStorage.getItem('user_id');
    const rId = localStorage.getItem('role_id');
    const sId = localStorage.getItem('status_id');
    
    return {
        token: localStorage.getItem('token'),
        user_id: (uId && uId !== 'null' && uId !== 'undefined') ? parseInt(uId) : null,
        role_id: (rId && rId !== 'null' && rId !== 'undefined') ? parseInt(rId) : null,
        status_id: (sId && sId !== 'null' && sId !== 'undefined') ? parseInt(sId) : 1,
        user_name: localStorage.getItem('user_name') || ''
    };
};

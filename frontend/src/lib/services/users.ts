
//LLAMADO DE LA API PARA USUARIOS
import { apiFetch } from "../api";

export interface User {
  user_id: number;
  identity_document: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  second_last_name?: string;
  email: string;
  password_hash: string;
  role_id: number;
  faculty_id?: number | null;
  status_id: number;
}

export type UserCreate = Omit<User, 'user_id'>;

type ApiResponse<T> = {
    resultado: T;
};


export const getUsuarios = async (): Promise<User[]> => {
    console.log("llamando getUsuarios...");
    const res = await apiFetch<ApiResponse<User[]>>('/api/get_usuarios');
    return res.resultado;
};

export const getUsuario = (id: number): Promise<User> =>
    apiFetch(`/api/get_usuario/${id}`);

export const createUsuario = (data: UserCreate) =>
    apiFetch('/api/create_usuario/', {
        method: 'POST',
        body: data,
    });

export const updateUsuario = (id: number, data: UserCreate) =>
    apiFetch(`/api/update_usuario/${id}`, {
        method: 'PUT',
        body: data,
    });

export const deleteUsuario = (id: number) =>
    apiFetch(`/api/delete_usuario/${id}`, {
        method: 'DELETE',
    });
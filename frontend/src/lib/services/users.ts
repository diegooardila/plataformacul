
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

// GET ALL
export const getUsuarios = () => {
  return apiFetch<User[]>("/get_usuarios");
};

// GET ONE
export const getUsuario = (id: number) => {
  return apiFetch<User>(`/get_usuario/${id}`);
};

// CREATE
export const createUsuario = (data: Partial<User>) => {
  return apiFetch<User>("/create_usuario/", {
    method: "POST",
    body: JSON.stringify(data),
  });
};

// UPDATE
export const updateUsuario = (id: number, data: Partial<User>) => {
  return apiFetch<User>(`/update_usuario/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
};

// DELETE
export const deleteUsuario = (id: number) => {
  return apiFetch(`/delete_usuario/${id}`, {
    method: "DELETE",
  });
};
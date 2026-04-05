
//LLAMADO DE LA API PARA USUARIOS
import { apiFetch } from "../lib/api";

export interface User {
  id_usuario: number;
  nombre: string;
  email: string;
}

export const getUsuarios = () => {
  return apiFetch<User[]>("/get_usuarios");
};

export const getUsuario = (id: number) => {
  return apiFetch<User>(`/get_usuario/${id}`);
};

export const createUsuario = (data: Omit<User, "id_usuario">) => {
  return apiFetch<User>("/create_usuario/", {
    method: "POST",
    body: JSON.stringify(data),
  });
};
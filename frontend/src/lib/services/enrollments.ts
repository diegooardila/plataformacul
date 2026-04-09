import { apiFetch } from "../api";

export interface Enrollment {
  enrollment_id: number;
  student_user_id: number;
  course_id: number;
  registration_date: string;
  status_id: number;
}

export type EnrollmentCreate = Omit<Enrollment, 'enrollment_id'>;

type ApiResponse<T> = {
    resultado: T;
};

export const getEnrollments = async (): Promise<Enrollment[]> => {
    try {
        const res = await apiFetch<ApiResponse<Enrollment[]>>('/api/get_enrollments');
        return res.resultado || [];
    } catch (error) {
        return [];
    }
};

export const getEnrollment = (id: number): Promise<Enrollment> =>
    apiFetch(`/api/get_enrollment/${id}`);

export const createEnrollment = (data: EnrollmentCreate) =>
    apiFetch('/api/create_enrollment/', {
        method: 'POST',
        body: data,
    });

export const updateEnrollment = (id: number, data: EnrollmentCreate) =>
    apiFetch(`/api/update_enrollment/${id}`, {
        method: 'PUT',
        body: data,
    });

export const deleteEnrollment = (id: number) =>
    apiFetch(`/api/delete_enrollment/${id}`, {
        method: 'DELETE',
    });

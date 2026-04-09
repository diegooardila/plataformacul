import { apiFetch } from "../api";

export interface Course {
  course_id: number;
  course_code: string;
  course_name: string;
  max_capacity: number;
  schedule: string;
  teacher_user_id: number;
  clasroom: number;
  period_id: number;
  status: number;
}

export type CourseCreate = Omit<Course, 'course_id'>;

type ApiResponse<T> = {
    resultado: T;
};

export const getCourses = async (): Promise<Course[]> => {
    try {
        const res = await apiFetch<ApiResponse<Course[]>>('/api/get_courses');
        return res.resultado || [];
    } catch (error) {
        // En caso de 404
        return [];
    }
};

export const getCourse = (id: number): Promise<Course> =>
    apiFetch(`/api/get_course/${id}`);

export const createCourse = (data: CourseCreate) =>
    apiFetch('/api/create_course/', {
        method: 'POST',
        body: data,
    });

export const updateCourse = (id: number, data: CourseCreate) =>
    apiFetch(`/api/update_course/${id}`, {
        method: 'PUT',
        body: data,
    });

export const deleteCourse = (id: number) =>
    apiFetch(`/api/delete_course/${id}`, {
        method: 'DELETE',
    });

-- Crear base de datos
CREATE DATABASE prueba;


-- Crear tabla
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL,
    apellido VARCHAR(20) NOT NULL,
    cedula VARCHAR(20) NOT NULL,
    edad INTEGER NOT NULL,
    usuario VARCHAR(20) NOT NULL,
    contrasena VARCHAR(20) NOT NULL
);



-- Insertar registro
INSERT INTO usuarios (nombre, apellido, cedula, edad, usuario, contrasena)
VALUES ('pedro', 'perez', '10102020', 30, 'pperez', '12345');

-- SCRIPT DE CREACION DE TABLAS PARA SISTEMA DE GESTION ACADEMICA


CREATE TABLE public.academic_periods (
  period_id integer NOT NULL DEFAULT nextval('periodo_academico_id_periodo_seq'::regclass),
  period_code character varying NOT NULL UNIQUE,
  start_date date NOT NULL,
  end_date date NOT NULL,
  CONSTRAINT academic_periods_pkey PRIMARY KEY (period_id)
);
CREATE TABLE public.certificates (
  certificate_id integer NOT NULL DEFAULT nextval('certificado_id_certificado_seq'::regclass),
  enrollment_id integer NOT NULL UNIQUE,
  verification_code character varying NOT NULL UNIQUE,
  issue_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT certificates_pkey PRIMARY KEY (certificate_id),
  CONSTRAINT fk_certificate_enrollment FOREIGN KEY (enrollment_id) REFERENCES public.enrollments(enrollment_id)
);
CREATE TABLE public.classrooms (
  classroom_id integer NOT NULL DEFAULT nextval('aula_id_aula_seq'::regclass),
  classroom_code character varying NOT NULL UNIQUE,
  max_capacity integer NOT NULL,
  status_id integer,
  CONSTRAINT classrooms_pkey PRIMARY KEY (classroom_id),
  CONSTRAINT fk_classroom_status FOREIGN KEY (status_id) REFERENCES public.statuses(status_id)
);
CREATE TABLE public.courses (
  course_id integer NOT NULL DEFAULT nextval('curso_id_curso_seq'::regclass),
  course_code character varying NOT NULL UNIQUE,
  course_name character varying NOT NULL,
  max_capacity integer NOT NULL,
  schedule character varying NOT NULL,
  teacher_user_id integer NOT NULL,
  classroom_id integer NOT NULL,
  period_id integer NOT NULL,
  status_id integer,
  CONSTRAINT courses_pkey PRIMARY KEY (course_id),
  CONSTRAINT fk_course_period FOREIGN KEY (period_id) REFERENCES public.academic_periods(period_id),
  CONSTRAINT fk_course_status FOREIGN KEY (status_id) REFERENCES public.statuses(status_id),
  CONSTRAINT fk_course_teacher FOREIGN KEY (teacher_user_id) REFERENCES public.users(user_id),
  CONSTRAINT fk_course_classroom FOREIGN KEY (classroom_id) REFERENCES public.classrooms(classroom_id)
);
CREATE TABLE public.enrollments (
  enrollment_id integer NOT NULL DEFAULT nextval('inscripcion_id_inscripcion_seq'::regclass),
  student_user_id integer NOT NULL,
  course_id integer NOT NULL,
  registration_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  status_id integer,
  CONSTRAINT enrollments_pkey PRIMARY KEY (enrollment_id),
  CONSTRAINT fk_enrollment_student FOREIGN KEY (student_user_id) REFERENCES public.users(user_id),
  CONSTRAINT fk_enrollment_course FOREIGN KEY (course_id) REFERENCES public.courses(course_id),
  CONSTRAINT fk_enrollment_status FOREIGN KEY (status_id) REFERENCES public.statuses(status_id)
);
CREATE TABLE public.faculties (
  faculty_id integer NOT NULL DEFAULT nextval('facultad_id_facultad_seq'::regclass),
  faculty_name character varying NOT NULL UNIQUE,
  CONSTRAINT faculties_pkey PRIMARY KEY (faculty_id)
);
CREATE TABLE public.grades (
  grade_id integer NOT NULL DEFAULT nextval('calificacion_id_calificacion_seq'::regclass),
  enrollment_id integer NOT NULL UNIQUE,
  final_grade numeric NOT NULL,
  observations text,
  CONSTRAINT grades_pkey PRIMARY KEY (grade_id),
  CONSTRAINT fk_grade_enrollment FOREIGN KEY (enrollment_id) REFERENCES public.enrollments(enrollment_id)
);
CREATE TABLE public.roles (
  role_id integer NOT NULL DEFAULT nextval('rol_id_rol_seq'::regclass),
  role_name character varying NOT NULL UNIQUE,
  CONSTRAINT roles_pkey PRIMARY KEY (role_id)
);
CREATE TABLE public.statuses (
  status_id integer NOT NULL DEFAULT nextval('estado_id_estado_seq'::regclass),
  status_name character varying NOT NULL UNIQUE,
  CONSTRAINT statuses_pkey PRIMARY KEY (status_id)
);
CREATE TABLE public.users (
  user_id integer NOT NULL DEFAULT nextval('usuario_id_usuario_seq'::regclass),
  identity_document character varying NOT NULL UNIQUE,
  first_name character varying NOT NULL,
  middle_name character varying,
  last_name character varying NOT NULL,
  second_last_name character varying,
  email character varying NOT NULL UNIQUE,
  password_hash character varying NOT NULL,
  role_id integer NOT NULL,
  faculty_id integer,
  status_id integer,
  CONSTRAINT users_pkey PRIMARY KEY (user_id),
  CONSTRAINT fk_user_role FOREIGN KEY (role_id) REFERENCES public.roles(role_id),
  CONSTRAINT fk_user_faculty FOREIGN KEY (faculty_id) REFERENCES public.faculties(faculty_id),
  CONSTRAINT fk_user_status FOREIGN KEY (status_id) REFERENCES public.statuses(status_id)
);
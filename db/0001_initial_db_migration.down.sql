-- Rollback script for initial database migration
DROP TABLE public.appointments;
DROP TABLE public.users;
DROP TABLE public.services;
DROP TABLE public.patients;
DROP EXTENSION IF EXISTS "pgcrypto";
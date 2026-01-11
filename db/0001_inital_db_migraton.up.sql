-- Activate UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
-- Patients
CREATE TABLE public.patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    phone TEXT,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
-- Services
CREATE TABLE public.services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    duration INTEGER NOT NULL,
    -- minutes
    price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
-- Appointments
CREATE TABLE public.appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES public.patients(id) ON DELETE CASCADE,
    service_id UUID REFERENCES public.services(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
-- Users (optional, for staff/admin)
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'staff', 'patient')),
    created_at TIMESTAMP DEFAULT NOW()
);
-- Inserts sample data into services table
-- Patients
INSERT INTO public.patients (full_name, phone, email)
VALUES (
        'Alice Johnson',
        '+34 600 123 456',
        'alice@example.com'
    ),
    (
        'Bob Smith',
        '+34 611 987 654',
        'bob@example.com'
    );
-- Services
INSERT INTO public.services (name, duration, price)
VALUES ('Physiotherapy Session', 60, 40.00),
    ('Sports Massage', 45, 35.00);
-- Appointments
INSERT INTO public.appointments (patient_id, service_id, scheduled_at, notes)
VALUES (
        (
            SELECT id
            FROM public.patients
            WHERE email = 'alice@example.com'
        ),
        (
            SELECT id
            FROM public.services
            WHERE name = 'Physiotherapy Session'
        ),
        '2026-01-15 10:00:00',
        'First consultation'
    ),
    (
        (
            SELECT id
            FROM public.patients
            WHERE email = 'bob@example.com'
        ),
        (
            SELECT id
            FROM public.services
            WHERE name = 'Sports Massage'
        ),
        '2026-01-16 18:30:00',
        'Post-training recovery'
    );
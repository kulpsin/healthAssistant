-- Create the database
CREATE DATABASE fhir;

-- Connect to the database
\c fhir;

-- Fetch desired username and password from environment variables
\set psqluser `echo "$POSTGRES_TOOL_USER"`
\set psqlpassword `echo "'$POSTGRES_TOOL_PASSWORD'"`

-- Create the custom user
CREATE ROLE :psqluser
    WITH PASSWORD :psqlpassword
    LOGIN;

-- Add privileges to all current tables
GRANT ALL PRIVILEGES
    ON ALL TABLES
    IN SCHEMA public
    TO :psqluser;

-- Add privileges to all future tables
ALTER DEFAULT PRIVILEGES
    IN SCHEMA public 
    GRANT ALL 
    ON TABLES
    TO :psqluser;

-- Add privileges to all future sequences
ALTER DEFAULT PRIVILEGES
    IN SCHEMA public
    GRANT USAGE
    ON SEQUENCES
    TO :psqluser;

-- Create the patients table
CREATE TABLE patients (
    id UUID PRIMARY KEY,
--  id UUID UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    deceased_at DATE DEFAULT NULL,
    gender TEXT CHECK (gender IN ('male', 'female', 'other', 'unknown')),
    email TEXT
);

-- Create the encounters table
CREATE TABLE encounters (
    id UUID PRIMARY KEY,
    patient_id UUID NOT NULL,
    status TEXT NOT NULL,   -- 'finished' 
    class TEXT NOT NULL,
    type TEXT NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    reason_display TEXT DEFAULT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- Create the observations table
CREATE TABLE observations (
    id UUID PRIMARY KEY,
    patient_id UUID NOT NULL,
    encounter_id UUID NOT NULL,
    observation_date TIMESTAMPTZ NOT NULL,
    status TEXT,     -- 'final'
    display TEXT[] NOT NULL,
    value NUMERIC(18,4)[],
    unit TEXT[],
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (encounter_id) REFERENCES encounters(id)
);

-- Create the conditions table
CREATE TABLE conditions (
    id UUID PRIMARY KEY,
    patient_id UUID NOT NULL,
    encounter_id UUID NOT NULL,
    clinical_status TEXT NOT NULL, -- 'active'
    verification_status TEXT NOT NULL, -- 'confirmed'
    onset_date TIMESTAMPTZ NOT NULL,
    abatement_data TIMESTAMPTZ DEFAULT NULL,
    code_display TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (encounter_id) REFERENCES encounters(id)
);

-- Create the procedures table
CREATE TABLE procedures (
    id serial PRIMARY KEY,
    patient_id UUID NOT NULL,
    encounter_id UUID NOT NULL,
    condition_id UUID DEFAULT NULL,  -- reason
    status TEXT NOT NULL, -- 'completed'
    performed_date TIMESTAMPTZ NOT NULL,
    performed_date_end TIMESTAMPTZ DEFAULT NULL,
    code_display TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (encounter_id) REFERENCES encounters(id),
    FOREIGN KEY (condition_id) REFERENCES conditions(id)
);

-- Create the immunizations table
CREATE TABLE immunizations (
    id serial PRIMARY KEY,
    patient_id UUID NOT NULL,
    encounter_id UUID NOT NULL,
    date TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL, -- 'completed'
    vaccine_display TEXT NOT NULL,
    was_given BOOLEAN NOT NULL, -- true/false
    primary_source BOOLEAN NOT NULL, -- true
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (encounter_id) REFERENCES encounters(id)
);

-- Create the care_plans table
CREATE TABLE care_plans (
    id serial PRIMARY KEY,
    patient_id UUID NOT NULL,
    encounter_id UUID NOT NULL,
    status TEXT NOT NULL, -- 'active'
    category_display TEXT NOT NULL, -- 'Self care'
    period_start_date TIMESTAMPTZ NOT NULL,
    period_end_date TIMESTAMPTZ DEFAULT NULL,
    details TEXT NOT NULL,  -- Quick'n'dirty concat: 'Food allergy diet and Allergy education'
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (encounter_id) REFERENCES encounters(id)
);

-- Create the medication_requests table
CREATE TABLE medication_requests (
    id serial PRIMARY KEY,
    patient_id UUID NOT NULL,
    encounter_id UUID NOT NULL,
    date_written TIMESTAMPTZ NOT NULL,
    medication_display TEXT NOT NULL,
    dosage_instruction TEXT,
    as_needed BOOLEAN NOT NULL DEFAULT FALSE, 
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (encounter_id) REFERENCES encounters(id)
);

-- Create the allergy_intolerances table
CREATE TABLE allergy_intolerances (
    id serial PRIMARY KEY,
    patient_id UUID NOT NULL,
    asserted_date TIMESTAMPTZ NOT NULL,
    clinical_status TEXT NOT NULL, -- 'active'
    type TEXT NOT NULL, -- 'allergy'
    category TEXT NOT NULL, -- 'food'
    criticality TEXT NOT NULL, -- 'high'
    display TEXT NOT NULL, -- 'Allergy to bee venom'
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);


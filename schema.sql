-- Family insurance SQLite schema (insurance.db)

CREATE TABLE IF NOT EXISTS family_members (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR NOT NULL,
    marital_status VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    state VARCHAR DEFAULT 'Utah',
    zip_code VARCHAR NOT NULL,
    license_years INTEGER DEFAULT 1,
    accidents INTEGER DEFAULT 0,
    violations INTEGER DEFAULT 0,
    coverage_type VARCHAR DEFAULT 'full',
    deductible INTEGER DEFAULT 500,
    liability_limit VARCHAR DEFAULT '100/300/100',
    created_at DATETIME
);

CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY,
    member_id INTEGER,
    year INTEGER NOT NULL,
    make VARCHAR NOT NULL,
    model VARCHAR NOT NULL,
    ownership VARCHAR DEFAULT 'owned',
    annual_mileage INTEGER DEFAULT 12000,
    primary_use VARCHAR DEFAULT 'commute',
    FOREIGN KEY(member_id) REFERENCES family_members(id)
);

CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY,
    member_id INTEGER,
    result TEXT NOT NULL,
    created_at DATETIME,
    FOREIGN KEY(member_id) REFERENCES family_members(id)
);

CREATE TABLE IF NOT EXISTS policies (
    id INTEGER PRIMARY KEY,
    member_id INTEGER,
    vehicle_id INTEGER,
    policy_type VARCHAR NOT NULL DEFAULT 'auto',
    carrier VARCHAR NOT NULL,
    policy_number VARCHAR DEFAULT '',
    status VARCHAR DEFAULT 'active',
    effective_date VARCHAR DEFAULT '',
    expiration_date VARCHAR DEFAULT '',
    billing_cycle VARCHAR DEFAULT 'monthly',
    premium_amount INTEGER DEFAULT 0,
    deductible INTEGER DEFAULT 500,
    liability_limit VARCHAR DEFAULT '',
    agent_name VARCHAR DEFAULT '',
    agent_phone VARCHAR DEFAULT '',
    agent_email VARCHAR DEFAULT '',
    notes TEXT DEFAULT '',
    created_at DATETIME,
    FOREIGN KEY(member_id) REFERENCES family_members(id),
    FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
);

CREATE TABLE IF NOT EXISTS policy_coverages (
    id INTEGER PRIMARY KEY,
    policy_id INTEGER,
    name VARCHAR NOT NULL,
    limit_amount VARCHAR DEFAULT '',
    deductible INTEGER DEFAULT 0,
    notes VARCHAR DEFAULT '',
    FOREIGN KEY(policy_id) REFERENCES policies(id)
);

-- schema.sql

DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS interventions;

CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name TEXT NOT NULL,
    city TEXT,
    address TEXT
);

CREATE TABLE interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER,
    reported_by TEXT,
    school_contact_person TEXT,
    problem_description TEXT,
    configuration_reviewed BOOLEAN,
    onsite_visit BOOLEAN,
    final_completed BOOLEAN,
    intervention_date DATE,
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

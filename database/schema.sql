create table locations (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    external_id VARCHAR(250) NOT NULL,
    name VARCHAR(250) NOT NULL,
    description VARCHAR(500) NULL,
    location_type VARCHAR(100) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
)

create table location_schedules (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    external_id VARCHAR(250) NOT NULL,
    name VARCHAR(250) NOT NULL,
    start_time TIME NOT NULL, 
    end_time TIME NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
)
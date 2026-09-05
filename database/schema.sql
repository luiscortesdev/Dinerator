CREATE TYPE meal_period AS ENUM ('breakfast', 'lunch', 'dinner', 'late_night');

CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    external_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500) NULL,
    location_type VARCHAR(100) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE location_schedules (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    external_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    start_time TIME NULL, 
    end_time TIME NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dishes (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    external_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500) NULL,
    ingredients VARCHAR(500) NULL,
    calories INT NULL,
    portion VARCHAR(255) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT dishes_name_location_unique UNIQUE (name, location_id) -- ensure each dish has a unique name
);

CREATE TABLE daily_menu_dishes (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    dish_id UUID NOT NULL REFERENCES dishes(id) ON DELETE CASCADE,
    served_date DATE NOT NULL,
    period meal_period NOT NULL,
    station VARCHAR(255) NOT NULL DEFAULT 'General',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_daily_serving UNIQUE (location_id, dish_id, served_date, period, station)
);

CREATE INDEX idx_daily_menu_lookup ON daily_menu_dishes(served_date, location_id, period);

CREATE TABLE ratings (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    daily_menu_dishes_id UUID NOT NULL REFERENCES daily_menu_dishes(id) ON DELETE CASCADE,
    score SMALLINT NOT NULL CHECK (score >= 1 AND score <= 10),
    client_id VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_daily_rating UNIQUE (daily_menu_dishes_id, client_id)
);

CREATE INDEX idx_ratings_menu_dish ON ratings(daily_menu_dishes_id);
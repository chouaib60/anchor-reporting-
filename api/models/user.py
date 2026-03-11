CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password TEXT        NOT NULL,
    role            VARCHAR(50) NOT NULL DEFAULT 'EDITOR',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""
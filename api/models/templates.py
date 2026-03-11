CREATE_TEMPLATES_TABLE = """
CREATE TABLE IF NOT EXISTS templates (
    id          UUID        PRIMARY_KEY default gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    description TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted         BOOLEAN     NOT NULL DEFAULT FALSE
);
"""

CREATE_TEMPLATES_VERSIONS= """
CREATE TABLE IF NOT EXISTS template_versions (
    id          UUID        PRIMARY_KEY DEFAULT gen_random_uuid(),
    template_id UUID        NOT NULL REFERENCES templates(id),
    version     INTEGER     NOT NULL,
    object_key   VARCHAR(255) NOT NULL, `
    is_active   BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(template_id, version)

);
"""
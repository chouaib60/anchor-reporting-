CREATE_TEMPLATES_TABLE = """
CREATE TABLE IF NOT EXISTS templates (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    created_by  UUID         NOT NULL REFERENCES users(id),
    deleted     BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
"""

CREATE_TEMPLATE_VERSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS template_versions (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID        NOT NULL REFERENCES templates(id),
    version     INTEGER     NOT NULL,
    object_key  TEXT        NOT NULL,
    is_active   BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(template_id, version)
);

CREATE INDEX IF NOT EXISTS idx_template_versions_template_id
    ON template_versions(template_id);
"""
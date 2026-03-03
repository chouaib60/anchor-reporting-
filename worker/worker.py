import asyncio
import logging
import json
import sys
from datetime import datetime, timezone
from config import get_settings

settings = get_settings()

# ── Logging ──────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "line": record.lineno,
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)

def setup_logging():
    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root.handlers.clear()
    root.addHandler(handler)

logger = logging.getLogger(__name__)

# ── Worker loop ───────────────────────────────────────────────

async def poll_jobs():
    """
    Boucle principale du worker.
    Sprint 2 : implémentation du poll PostgreSQL + SKIP LOCKED
    Sprint 3 : rendu DOCX + conversion PDF LibreOffice
    """
    logger.info("Worker démarré",)
    logger.info("Config : max_jobs=%d, poll=%ds, timeout=%ds",
        settings.worker_max_concurrent_jobs,
        settings.worker_poll_interval_seconds,
        settings.worker_job_timeout_seconds,
    )

    while True:
        logger.debug("En attente de jobs...")
        # TODO Sprint 2 : SELECT FOR UPDATE SKIP LOCKED
        await asyncio.sleep(settings.worker_poll_interval_seconds)


async def main():
    setup_logging()
    await poll_jobs()


if __name__ == "__main__":
    asyncio.run(main())
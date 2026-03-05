import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from core.config import get_settings

settings = get_settings()


def log(level, message):
    print(f"[{level}] {message}")


async def get_conn():
    return await asyncpg.connect(settings.database_url.replace("+asyncpg", ""))


#  Test 1 : Connexion --

async def test_connection() -> bool:
    log("INFO", "=== TEST 1 : Connexion PostgreSQL ===")
    try:
        conn = await get_conn()
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        log("INFO", f"TEST 1 PASSED - {version[:50]}")
        return True
    except Exception as e:
        log("ERROR", f"TEST 1 FAILED : {e}")
        return False


#  Test 2 : SELECT FOR UPDATE SKIP LOCKED --

async def test_skip_locked() -> bool:
    log("INFO", "=== TEST 2 : SELECT FOR UPDATE SKIP LOCKED ===")
    try:
        conn = await get_conn()

        # Table de test minimale
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS poc_jobs (
                id     SERIAL PRIMARY KEY,
                status VARCHAR(20) DEFAULT 'CREATED'
            )
        """)

        # Inserer deux lignes
        await conn.execute("INSERT INTO poc_jobs (status) VALUES ('CREATED'), ('CREATED')")

        picked = []

        async def worker_pick(worker_id: int):
            c = await get_conn()
            async with c.transaction():
                row = await c.fetchrow("""
                    SELECT id FROM poc_jobs
                    WHERE status = 'CREATED'
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                """)
                if row:
                    picked.append(row["id"])
                    log("INFO", f"Worker {worker_id} a pris la ligne id={row['id']}")
                    await asyncio.sleep(0.1)
            await c.close()

        await asyncio.gather(worker_pick(1), worker_pick(2))

        assert len(picked) == 2, f"Attendu 2 lignes prises, obtenu {len(picked)}"
        assert picked[0] != picked[1], "Les deux workers ont pris la meme ligne"
        log("INFO", "TEST 2 PASSED - SKIP LOCKED fonctionne, pas de conflit")

        # Nettoyage
        await conn.execute("DROP TABLE poc_jobs")
        await conn.close()
        return True
    except Exception as e:
        log("ERROR", f"TEST 2 FAILED : {e}")
        return False


#  Main 

async def main():
    results = {
        "connexion":   await test_connection(),
        "skip_locked": await test_skip_locked(),
    }

    passed = sum(v for v in results.values())
    total = len(results)
    print(f"\n{'='*40}")
    print(f"Resultat : {passed}/{total} tests passes")

    for name, ok in results.items():
        print(f"  {'PASSED' if ok else 'FAILED'}  {name}")

    print(f"{'='*40}")
    print("GO - PostgreSQL operationnel" if passed == total else "NO-GO - Verifier les erreurs")


if __name__ == "__main__":
    asyncio.run(main())
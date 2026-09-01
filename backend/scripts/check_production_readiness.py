import os
import sys
import logging
from sqlalchemy import create_engine
import redis

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ProdCheck")

def check_directory_permissions():
    """Verify that required directories exist and are writable."""
    directories = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/videos")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/evidence"))
    ]
    
    all_passed = True
    for d in directories:
        os.makedirs(d, exist_ok=True)
        if not os.access(d, os.W_OK):
            logger.error(f"Directory is not writable: {d}")
            all_passed = False
        else:
            logger.info(f"Directory OK: {d}")
    return all_passed

def check_database():
    """Verify PostgreSQL database connection."""
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        logger.error("DATABASE_URL is not set.")
        return False
        
    if "sqlite" in db_url:
        logger.error("DATABASE_URL indicates SQLite. SQLite is not permitted in production.")
        return False
        
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            pass
        logger.info("Database connection OK.")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def check_redis():
    """Verify Redis connection."""
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        r = redis.Redis.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
        logger.info("Redis connection OK.")
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False

def check_secrets():
    """Verify that critical secrets are explicitly configured and not using fallback defaults."""
    jwt_secret = os.environ.get("JWT_SECRET")
    if not jwt_secret or jwt_secret == "insecure_default_secret_do_not_use_in_prod":
        logger.error("JWT_SECRET is either missing or using an insecure default.")
        return False
        
    admin_pass = os.environ.get("ADMIN_PASSWORD")
    if not admin_pass or admin_pass == "admin123":
        logger.error("ADMIN_PASSWORD is using an insecure default.")
        return False
        
    logger.info("Secrets configuration OK.")
    return True

def main():
    logger.info("Starting Production Readiness Checks...")
    
    checks = [
        check_directory_permissions(),
        check_database(),
        check_redis(),
        check_secrets()
    ]
    
    if all(checks):
        logger.info("SUCCESS: Platform is ready for production deployment.")
        sys.exit(0)
    else:
        logger.error("FAILURE: One or more production readiness checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()

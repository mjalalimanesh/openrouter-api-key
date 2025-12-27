import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from database import DatabaseManager
from openrouter_client import OpenRouterClient
from utils import calculate_new_limit_increment

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_cycle(client, db):
    logger.info("Starting limit adjustment cycle...")
    try:
        keys = client.list_keys()
        logger.info(f"Found {len(keys)} keys to process.")
        
        for key in keys:
            key_hash = key.get("hash")
            if not key_hash:
                logger.warning("Found key without hash, skipping.")
                continue
                
            name = key.get("name", "Unnamed")
            current_limit = key.get("limit")
            total_usage = key.get("usage", 0)
            
            # Skip if key is unlimited (None)
            if current_limit is None:
                logger.info(f"Key {name} has no limit (unlimited), skipping.")
                continue
                
            usage_daily = key.get("usage_daily", 0)
            usage_weekly = key.get("usage_weekly", 0)
            
            logger.info(f"Processing key: {name} ({key_hash[:8]}...)")
            
            # 1. Log today's usage to DB
            db.log_usage(key_hash, usage_daily)
            
            # 2. Get last 7 days of usage (excluding today)
            usage_history = db.get_last_7_days_usage(key_hash, exclude_today=True)
            
            # 3. Calculate average excluding outliers
            # Warm start: If we have fewer than 7 days in DB, use usage_weekly/7 if it's higher
            avg_usage, days_count = calculate_new_limit_increment(usage_history)
            
            if days_count < 7:
                warm_avg = usage_weekly / 7.0
                if warm_avg > avg_usage:
                    logger.info(f"Key {name}: Warm starting with weekly average (DB has {days_count} days, weekly avg is {warm_avg:.2f})")
                    avg_usage = warm_avg
                    # We don't update days_count here as it still reflects DB records
            
            # 4. Update limit: Base it on total usage plus 1.3 * average usage plus $1 buffer
            new_limit = round(total_usage + (1.3 * avg_usage) + 1.0, 4)
            
            if avg_usage >= 0:
                logger.info(f"Key {name}: Total usage {total_usage:.2f}, Avg usage {avg_usage:.2f} (from {days_count} days, x1.3) + $1 buffer, New limit {new_limit:.2f}")
                client.update_key_limit(key_hash, new_limit)
                logger.info(f"Successfully updated limit for {name}.")
                
    except Exception as e:
        logger.error(f"Error during cycle: {str(e)}")

def main():
    load_dotenv()
    
    api_key = os.getenv("PROVISIONING_API_KEY")
    if not api_key:
        logger.error("PROVISIONING_API_KEY not found in environment variables.")
        return
        
    db_path = os.getenv("DB_PATH", "/data/usage.db")
    
    client = OpenRouterClient(api_key)
    db = DatabaseManager(db_path)
    
    logger.info("OpenRouter Key Manager started (single run for cron).")
    logger.info(f"DB Path: {db_path}")
    
    run_cycle(client, db)
    logger.info("Cycle completed successfully.")

if __name__ == "__main__":
    main()


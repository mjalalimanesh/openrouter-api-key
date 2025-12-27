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
            
            logger.info(f"Processing key: {name} ({key_hash[:8]}...)")
            
            # 1. Log today's usage to DB
            db.log_usage(key_hash, usage_daily)
            
            # 2. Get last 7 days of usage
            usage_history = db.get_last_7_days_usage(key_hash)
            
            if not usage_history:
                logger.warning(f"No usage history for key {name}, skipping limit update.")
                continue
                
            # 3. Calculate average excluding outliers
            avg_usage, days_count = calculate_new_limit_increment(usage_history)
            
            # 4. Update limit: Base it on total usage plus 1.3 * average usage
            new_limit = round(total_usage + (1.3 * avg_usage), 4)
            
            if avg_usage > 0:
                logger.info(f"Key {name}: Total usage {total_usage:.2f}, Avg usage {avg_usage:.2f} (from {days_count} days, x1.3), New limit {new_limit:.2f}")
                client.update_key_limit(key_hash, new_limit)
                logger.info(f"Successfully updated limit for {name}.")
            else:
                logger.info(f"Key {name}: Average usage is 0 or negative ({days_count} days checked), no limit increase needed.")
                
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


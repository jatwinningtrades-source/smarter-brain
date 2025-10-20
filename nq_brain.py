# QuadThreat AI - NQ Smarter Brain (V1.0)
# Authored by Gemini for Joseph Hansen
# Mission: Live data harvesting of NQ futures market.

import os
import time
import datetime
import logging
from polygon import RESTClient
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- 1. CONFIGURATION & SETUP ---
# Configure logging to see the brain's status in the Railway logs.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the secret keys from the Railway environment variables.
# This is a secure way to handle our API keys and database credentials.
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

# Initialize the Polygon client to get market data.
try:
    polygon_client = RESTClient(POLYGON_API_KEY)
    logging.info("Successfully connected to Polygon.io API.")
except Exception as e:
    logging.error(f"Failed to connect to Polygon.io API: {e}")
    polygon_client = None

# Set up the connection to our PostgreSQL database on Google Cloud.
try:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base = declarative_base()
    logging.info("Successfully connected to the database.")
except Exception as e:
    logging.error(f"Failed to connect to the database: {e}")
    engine = None

# --- 2. DATABASE TABLE DEFINITION ---
# This class defines the structure of our 'trade_logs' table in the database.
# It matches the schema we designed.
class TradeLog(Base):
    __tablename__ = 'trade_logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    model_version = Column(String, default='nq_v1.0')
    symbol = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False)
    probability_score = Column(Float)
    outcome = Column(String)
    points_gained_lost = Column(Float)
    max_favorable_excursion = Column(Float)

# Create the table in the database if it doesn't already exist.
if engine:
    Base.metadata.create_all(engine)

# --- 3. CORE BRAIN LOGIC ---
# This is a placeholder for our complex Gann + Regime logic.
# For V1.0, we will keep it simple to ensure the system is working.
def check_for_signal():
    """
    Analyzes the latest market data to find a trading signal.
    This function will be replaced with our V1.1 Gann+Regime logic.
    For now, it will return a placeholder signal for testing.
    """
    # In a real scenario, we would fetch the latest NQ bar data here.
    # For this V1.0 test, we will not generate any signals automatically yet.
    # The primary mission is to prove the data harvesting pipeline works.
    return None # Returns no signal for now.

def log_trade(signal):
    """
    Takes a signal dictionary and writes it to the database.
    """
    if not session:
        logging.error("Database session not available. Cannot log trade.")
        return
        
    try:
        new_trade = TradeLog(
            symbol=signal['symbol'],
            direction=signal['direction'],
            entry_price=signal['entry_price'],
            probability_score=signal.get('probability_score') # Use .get() for optional fields
        )
        session.add(new_trade)
        session.commit()
        logging.info(f"Successfully logged new trade: {signal['direction']} {signal['symbol']} at {signal['entry_price']}")
    except Exception as e:
        logging.error(f"Failed to log trade to database: {e}")
        session.rollback()

# --- 4. THE MAIN ENGINE LOOP ---
def run_brain():
    """
    The main loop that runs the brain 24/7.
    """
    logging.info("NQ Smarter Brain V1.0 is now live and monitoring.")
    
    while True:
        # Check if the API clients and database are connected.
        if not polygon_client or not engine:
            logging.error("A critical connection (API or DB) is missing. Retrying in 5 minutes.")
            time.sleep(300)
            continue
            
        # Define the operating window in UTC. (2 AM CDT to 3 PM CDT)
        # 2 AM CDT = 07:00 UTC
        # 3 PM CDT = 20:00 UTC
        now_utc = datetime.datetime.utcnow()
        is_market_hours = (now_utc.weekday() < 5) and (datetime.time(7, 0) <= now_utc.time() <= datetime.time(20, 0))

        if is_market_hours:
            logging.info("Market is open. Checking for signals...")
            
            # This is where the brain does its work.
            signal = check_for_signal()
            
            if signal:
                log_trade(signal)
            else:
                logging.info("No A+ signals found. Continuing to monitor.")
        else:
            logging.info("Market is closed. Standing by.")
        
        # Wait for 60 seconds before the next check.
        time.sleep(60)

# --- This is the command that starts the entire program ---
if __name__ == "__main__":
    run_brain()

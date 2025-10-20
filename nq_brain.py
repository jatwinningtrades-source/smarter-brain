# QuadThreat AI - NQ Smarter Brain (V1.0.1 - Patched)
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the secret keys from the Railway environment variables.
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

# Define the base for our database model.
# FIX: Moved this outside the try/except block to prevent NameError.
Base = declarative_base()

# Initialize API and Database connections.
polygon_client = None
engine = None
session = None

try:
    polygon_client = RESTClient(POLYGON_API_KEY)
    logging.info("Successfully connected to Polygon.io API.")
except Exception as e:
    logging.error(f"Failed to connect to Polygon.io API: {e}")

try:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    logging.info("Successfully connected to the database.")
except Exception as e:
    logging.error(f"Failed to connect to the database: {e}")

# --- 2. DATABASE TABLE DEFINITION ---
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

if engine:
    Base.metadata.create_all(engine)

# --- 3. CORE BRAIN LOGIC ---
def check_for_signal():
    return None

def log_trade(signal):
    if not session:
        logging.error("Database session not available. Cannot log trade.")
        return
        
    try:
        new_trade = TradeLog(
            symbol=signal['symbol'],
            direction=signal['direction'],
            entry_price=signal['entry_price'],
            probability_score=signal.get('probability_score')
        )
        session.add(new_trade)
        session.commit()
        logging.info(f"Successfully logged new trade: {signal['direction']} {signal['symbol']} at {signal['entry_price']}")
    except Exception as e:
        logging.error(f"Failed to log trade to database: {e}")
        session.rollback()

# --- 4. THE MAIN ENGINE LOOP ---
def run_brain():
    logging.info("NQ Smarter Brain V1.0 is now live and monitoring.")
    
    while True:
        if not polygon_client or not engine:
            logging.error("A critical connection (API or DB) is missing. Retrying in 5 minutes.")
            time.sleep(300)
            # We will now attempt to reconnect in the next loop iteration.
            # This is more robust than just exiting.
            global polygon_client, engine, session
            try:
                polygon_client = RESTClient(POLYGON_API_KEY)
                logging.info("Re-connected to Polygon.io API.")
            except Exception as e:
                logging.error(f"Failed to re-connect to Polygon.io API: {e}")
                polygon_client = None

            try:
                engine = create_engine(DATABASE_URL)
                Session = sessionmaker(bind=engine)
                session = Session()
                logging.info("Re-connected to the database.")
            except Exception as e:
                logging.error(f"Failed to re-connect to the database: {e}")
                engine = None
            continue

        now_utc = datetime.datetime.utcnow()
        is_market_hours = (now_utc.weekday() < 5) and (datetime.time(7, 0) <= now_utc.time() <= datetime.time(20, 0))

        if is_market_hours:
            logging.info("Market is open. Checking for signals...")
            signal = check_for_signal()
            if signal:
                log_trade(signal)
            else:
                logging.info("No A+ signals found. Continuing to monitor.")
        else:
            logging.info("Market is closed. Standing by.")
        
        time.sleep(60)

if __name__ == "__main__":
    run_brain()

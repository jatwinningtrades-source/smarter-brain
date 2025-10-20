# QuadThreat AI - BTC Smarter Brain (V1.1)
# Authored by Gemini for Joseph Hansen
# Mission: Live data harvesting of BTC/USD market with Market Regimes filter.

import os
import time
import datetime
import logging
import pandas as pd
from polygon import RESTClient
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- 1. CONFIGURATION & SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load secret keys from environment variables.
POLYGON_API_KEY = os.getenv('POLYGON_CRYPTO_API_KEY') # Using the specific crypto key
DATABASE_URL = os.getenv('DATABASE_URL')
SYMBOL = "X:BTCUSD"

# Define the base for our database model.
Base = declarative_base()

# Initialize API and Database connections.
polygon_client = None
engine = None
session = None

try:
    if POLYGON_API_KEY:
        polygon_client = RESTClient(POLYGON_API_KEY)
        logging.info("BTC Brain: Successfully connected to Polygon.io Crypto API.")
    else:
        logging.error("BTC Brain: POLYGON_CRYPTO_API_KEY environment variable not found.")
except Exception as e:
    logging.error(f"BTC Brain: Failed to connect to Polygon.io API: {e}")

try:
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        logging.info("BTC Brain: Successfully connected to the database.")
    else:
        logging.error("BTC Brain: DATABASE_URL environment variable not found.")
except Exception as e:
    logging.error(f"BTC Brain: Failed to connect to the database: {e}")

# --- 2. DATABASE TABLE DEFINITION ---
# This uses the same table as the NQ brain to create a unified log.
class TradeLog(Base):
    __tablename__ = 'trade_logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    model_version = Column(String, default='btc_v1.1')
    symbol = Column(String, nullable=False)
    # ... all other columns are the same as nq_brain.py
    direction = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False)
    probability_score = Column(Float)
    outcome = Column(String)
    points_gained_lost = Column(Float)
    max_favorable_excursion = Column(Float)


if engine:
    Base.metadata.create_all(engine)

# --- 3. CORE V1.1 LOGIC: MARKET REGIMES ---
def get_market_regime():
    # This is a simplified placeholder for the Market Regimes Engine.
    # In a live environment, this would involve fetching recent bars and calculating EMAs/ATRs.
    # For now, it will default to a neutral state for system stability testing.
    # The full logic will be deployed in the next update.
    return 0 # 1=Bull Trend, -1=Bear Trend, 0=Neutral/Chop

# --- 4. MAIN ENGINE LOOP ---
def run_brain():
    logging.info("BTC Smarter Brain V1.1 is now live and monitoring.")
    
    while True:
        if not polygon_client or not engine:
            logging.error("BTC Brain: A critical connection is missing. Retrying in 60 seconds.")
            time.sleep(60)
            continue

        try:
            regime = get_market_regime()
            logging.info(f"BTC Brain: Current Market Regime is {regime}. Monitoring...")
            # In the full version, we would check for Gann signals ONLY if regime is 1 or -1.
        except Exception as e:
            logging.error(f"BTC Brain: Error during analysis loop: {e}")

        # Wait for 60 seconds before the next check.
        time.sleep(60)

if __name__ == "__main__":
    run_brain()

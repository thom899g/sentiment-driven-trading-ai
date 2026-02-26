"""
Central configuration management for the Sentiment Trading AI.
Uses environment variables with Firebase as primary state store.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TradingMode(Enum):
    """Trading operation modes"""
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"

class SentimentSource(Enum):
    """Approved sentiment data sources"""
    TWITTER = "twitter"
    NEWS = "news"
    REDDIT = "reddit"
    INSTAGRAM = "instagram"

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation"""
    project_id: str
    credentials_path: str
    collection_name: str = "sentiment_trading"
    
    def __post_init__(self):
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Firebase credentials not found at: {self.credentials_path}"
            )
        if not self.project_id:
            raise ValueError("Firebase project_id cannot be empty")

@dataclass
class TradingConfig:
    """Trading-specific configuration"""
    mode: TradingMode = TradingMode.PAPER
    max_position_size: float = 10000.0  # USD
    stop_loss_pct: float = 0.02  # 2%
    take_profit_pct: float = 0.05  # 5%
    sentiment_threshold: float = 0.7  # Confidence threshold
    cooloff_period: int = 300  # Seconds between trades
    
    def validate(self) -> None:
        """Validate trading parameters"""
        if self.stop_loss_pct <= 0 or self.stop_loss_pct >= 1:
            raise ValueError("stop_loss_pct must be between 0 and 1")
        if self.take_profit_pct <= 0:
            raise ValueError("take_profit_pct must be positive")
        if self.max_position_size <= 0:
            raise ValueError("max_position_size must be positive")

@dataclass
class APIConfig:
    """API configuration with rate limiting"""
    twitter_bearer_token: Optional[str] = None
    news_api_key: Optional[str] = None
    rate_limit_per_minute: int = 60
    retry_attempts: int = 3
    timeout_seconds: int = 30
    
    @property
    def has_twitter_access(self) -> bool:
        return bool(self.twitter_bearer_token)
    
    @property
    def has_news_access(self) -> bool:
        return bool(self.news_api_key)

class SentimentTradingConfig:
    """Main configuration class"""
    
    def __init__(self):
        # Firebase configuration
        self.firebase = FirebaseConfig(
            project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
            credentials_path=os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase_credentials.json")
        )
        
        # Trading configuration
        self.trading = TradingConfig(
            mode=TradingMode[os.getenv("TRADING_MODE", "PAPER")],
            max_position_size=float(os.getenv("MAX_POSITION_SIZE", "10000")),
            stop_loss_pct=float(os.getenv("STOP_LOSS_PCT", "0.02")),
            take_profit_pct=float(os.getenv("TAKE_PROFIT_PCT", "0.05")),
            sentiment_threshold=float(os.getenv("SENTIMENT_THRESHOLD", "0.7")),
            cooloff_period=int(os.getenv("COOLOFF_PERIOD", "300"))
        )
        
        # API configuration
        self.api = APIConfig(
            twitter_bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            news_api_key=os.getenv("NEWS_API_KEY"),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
            retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "30"))
        )
        
        # Sentiment sources
        self.enabled
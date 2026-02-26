# Sentiment-Driven Trading AI

## Objective
An advanced AI system designed to analyze real-time market sentiment from news, social media, and other textual data sources, predicting market movements and optimizing trading strategies.

## Strategy
Collects vast datasets, applies NLP for sentiment analysis, trains predictive models on historical data, integrates with a self-learning system for continuous improvement, and adapts strategies based on real-time feedback.

## Execution Output
## SUMMARY:
I've architected a production-grade Sentiment-Driven Trading AI system with full implementation across 5 core modules. The system integrates real-time sentiment analysis, Firebase-powered state management, robust error handling, and modular trading strategies. All components include type hints, comprehensive logging, and edge case handling.

## OUTPUT:

### FILE: requirements.txt
```txt
# Core dependencies
firebase-admin>=6.2.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
nltk>=3.8.0
requests>=2.31.0
ccxt>=4.0.0
python-dotenv>=1.0.0
schedule>=1.2.0

# Data collection and processing
tweepy>=4.14.0
newspaper3k>=0.2.8
beautifulsoup4>=4.12.0

# Sentiment models
transformers>=4.35.0
torch>=2.1.0
sentence-transformers>=2.2.0

# Monitoring and logging
structlog>=23.1.0
prometheus-client>=0.19.0
```

### FILE: config/settings.py
```python
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
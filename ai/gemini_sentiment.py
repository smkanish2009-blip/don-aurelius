"""
Generative AI Macro Narrative & News Sentiment Evaluator.
Leverages Google Gemini API to analyze breaking central bank speeches and macro headlines.
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("GeminiSentiment")


class GeminiSentimentAgent:
    def __init__(self, api_key: str = "", model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name
        self.client = None
        self._init_client()

    def _init_client(self) -> None:
        if not self.api_key:
            logger.info("Gemini API Key not configured. AI narrative evaluator running in simulation mode.")
            return
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Google Gemini Client initialized successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize Google GenAI Client: {e}")

    def evaluate_news_impact(self, event_title: str, actual: str, forecast: str, previous: str) -> Dict[str, Any]:
        """
        Analyzes economic release numbers to determine whether surprise is Hawkish/Bearish for Gold.
        Gold moves inversely to US yields and hawkish data.
        """
        if not self.client:
            # Deterministic heuristic fallback
            return {
                "sentiment_score": 0.0,
                "bias": "NEUTRAL",
                "rationale": f"Simulated analysis for {event_title}"
            }

        prompt = f"""
        You are a quantitative macro analyst for Gold (XAUUSD).
        Evaluate this economic data release for Spot Gold:
        Event: {event_title}
        Actual: {actual}
        Forecast: {forecast}
        Previous: {previous}

        Output a strict JSON object with:
        "sentiment_score": float between -1.0 (strongly bearish gold / hawkish USD) and +1.0 (strongly bullish gold / dovish USD)
        "bias": "BULLISH", "BEARISH", or "NEUTRAL"
        "rationale": 1-sentence explanation
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return {"raw_response": response.text}
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return {"sentiment_score": 0.0, "bias": "NEUTRAL", "rationale": "API fallback"}

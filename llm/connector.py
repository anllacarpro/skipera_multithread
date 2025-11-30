# https://github.com/serv0id/skipera
import json
import re
import requests
from config import PERPLEXITY_API_URL, PERPLEXITY_API_KEY, PERPLEXITY_MODEL
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_API_URL
from pydantic import BaseModel
from typing import List, Literal
from loguru import logger


class ResponseFormat(BaseModel):
    question_id: str
    option_id: List[str]
    type: Literal["Single", "Multi"]


class ResponseList(BaseModel):
    responses: List[ResponseFormat]


class PerplexityConnector(object):
    def __init__(self):
        self.API_URL: str = PERPLEXITY_API_URL
        self.API_KEY: str = PERPLEXITY_API_KEY

    def get_response(self, questions: dict) -> dict:
        """
        Sends the questions to Perplexity and asks for the answers
        in a JSON format.
        """
        if not self.API_KEY or self.API_KEY == "":
            logger.error("Perplexity API Key is not configured in config.py!")
            return None
            
        logger.debug("Making an API Request to Perplexity..")
        
        try:
            response = requests.post(url=self.API_URL, headers={
                "Authorization": f"Bearer {self.API_KEY}"
            }, json={
                "model": PERPLEXITY_MODEL,
                "messages": [
                    {"role": "system", "content": 
                        "You are an expert assistant that answers multiple choice questions accurately. "
                        "You will receive questions in JSON format with question text and answer options. "
                        "Each option has an 'option_id' (which you MUST return) and a 'value' (the answer text). "
                        "Your task:\n"
                        "1. Read each question carefully, ignoring any HTML tags in the text\n"
                        "2. Analyze all available options\n"
                        "3. Select the CORRECT option(s) based on your knowledge\n"
                        "4. For 'Single-Choice' questions: return ONLY ONE option_id in an array\n"
                        "5. For 'Multi-Choice' questions: return ALL correct option_ids in an array\n"
                        "6. CRITICAL: You MUST return the 'option_id' value exactly as provided, NOT the answer text\n"
                        "7. Think step by step and choose the most accurate answer(s)\n"
                        "8. If unsure, use logical reasoning and domain knowledge to make the best choice"
                    },
                    {"role": "user", "content": 
                        "Answer these questions. Return the response in the exact JSON schema format specified.\n\n"
                        "IMPORTANT: In your response, 'option_id' must be the ID from the options provided, "
                        "NOT a number or the answer text itself.\n\n"
                        f"Questions:\n{json.dumps(questions, indent=2)}"
                    },
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {"schema": ResponseList.model_json_schema()}
                },
                "temperature": 0.2  # Lower temperature for more consistent/accurate responses
            })
            
            if response.status_code == 401:
                logger.error("Perplexity API Key is invalid or unauthorized (401). Please check your API key in config.py")
                return None
            elif response.status_code != 200:
                logger.error(f"Perplexity API error: Status {response.status_code} - {response.text}")
                return None
                
            response_json = response.json()
            return json.loads(response_json["choices"][0]["message"]["content"])
            
        except Exception as e:
            logger.error(f"Error connecting to Perplexity API: {e}")
            return None


class GeminiConnector(object):
    """Simple Gemini/Generative API connector that sends a prompt and
    attempts to parse a JSON response from the returned text.

    Note: Gemini / Google Generative API may accept different payloads
    depending on account configuration. This implementation uses the
    `generate` REST endpoint with an API key in the query string and a
    simple `prompt.text` payload. If your account requires OAuth or a
    different endpoint, adjust `GEMINI_API_URL` accordingly in
    `config.py`.
    """

    def __init__(self):
        self.API_KEY = GEMINI_API_KEY
        self.MODEL = GEMINI_MODEL
        # Construct the model generate URL
        self.BASE = f"{GEMINI_API_URL}/{self.MODEL}:generate"

    def _extract_json(self, text: str):
        """Try to extract the first JSON object from text."""
        try:
            # Greedy attempt to find the first balanced JSON object
            m = re.search(r"\{(?:[^{}]|(?R))*\}", text, re.DOTALL)
        except re.error:
            # Fallback: find first { and last }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return text[start:end+1]
            return None

        if not m:
            # Fallback simple extraction
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return text[start:end+1]
            return None
        return m.group(0)

    def get_response(self, questions: dict) -> dict:
        if not self.API_KEY:
            logger.error("Gemini API Key is not configured (GEMINI_API_KEY).")
            return None

        logger.debug("Making an API Request to Gemini/Generative API..")

        # Build an instruction similar to the Perplexity prompt
        prompt = (
            "You are an expert assistant that answers multiple choice questions accurately.\n"
            "You will receive questions in JSON format with question text and answer options. "
            "Each option has an 'option_id' (which you MUST return) and a 'value' (the answer text).\n"
            "Return ONLY valid JSON that conforms to the schema: { \"responses\": [ {\"question_id\": str, \"option_id\": [str], \"type\": \"Single\"|\"Multi\" } ] }\n"
            "For Single-Choice questions return a single option_id in the array. For Multi-Choice return all correct option_ids.\n"
            "Answer using the option_id values exactly as provided.\n\n"
            f"Questions:\n{json.dumps(questions)}"
        )

        payload = {
            "prompt": {"text": prompt},
            "temperature": 0.2,
            "maxOutputTokens": 1200
        }

        try:
            url = f"{self.BASE}?key={self.API_KEY}"
            resp = requests.post(url, json=payload)
            if resp.status_code != 200:
                logger.error(f"Gemini API error: Status {resp.status_code} - {resp.text}")
                return None

            data = resp.json()
            # Typical response contains 'candidates' with 'output'
            output = None
            if "candidates" in data and len(data["candidates"]) > 0:
                output = data["candidates"][0].get("output") or data["candidates"][0].get("content")
            elif "output" in data:
                output = data.get("output")

            if not output:
                logger.error("No output returned from Gemini API")
                return None

            # Extract JSON substring and parse it
            json_text = self._extract_json(output)
            if not json_text:
                logger.error("Could not extract JSON from Gemini response")
                return None

            return json.loads(json_text)

        except Exception as e:
            logger.error(f"Error connecting to Gemini API: {e}")
            return None

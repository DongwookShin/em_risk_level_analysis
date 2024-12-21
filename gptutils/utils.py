import json
import re
import time
import logging
import os
from typing import List, Dict, Any, Optional
from openai import BadRequestError, AzureOpenAI

logger = logging.getLogger(__name__)

class GPTResponseHelper:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version="2024-02-01",
        )
    
    def get_gpt_response(self, messages: List[Dict], max_tries: int = 3) -> Any:
        for attempt in range(max_tries):
            try:
                response = self.client.chat.completions.create(
                    model="Nsight_deployment_02",
                    messages=messages,
                    max_tokens=4096,
                    temperature=0,
                    n=1,
                    seed=42,
                )

                #print(response.choices[0].message.content)

                message_content = GPTResponseHelper._fix_json_string(
                    response.choices[0].message.content
                )
                parsed_data = GPTResponseHelper._validate_and_parse_json(
                    message_content
                )
                if parsed_data is not None:
                    return parsed_data
                logger.warning(
                    f"Attempt {attempt + 1}/{max_tries} for JSON parsing failed."
                )
            except (BadRequestError, TypeError) as e:
                logger.error(
                    f"Error during GPT response generation (Attempt {attempt + 1}/{max_tries}): {e}"
                )
            time.sleep(3)
        return None

    @staticmethod
    def _fix_json_string(json_string: str) -> str:
        new_string = GPTResponseHelper._remove_trailing_commas(json_string)
        new_string = GPTResponseHelper._wrap_quote_around_int_range(new_string)
        return new_string

    @staticmethod
    def _validate_and_parse_json(json_str: str) -> Optional[dict]:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            return None

    @staticmethod
    def _wrap_quote_around_int_range(json_string: str) -> str:
        return re.sub(r", (\d+)-(\d+)]", r', "\1-\2"]', json_string)

    @staticmethod
    def _remove_trailing_commas(json_string: str) -> str:
        """
        Sometimes the JSON string from GPT returns a trailing comma at the end of a list. If so, remove the comma.
        """
        # Regex pattern to match trailing commas before closing curly braces or square brackets
        pattern = r",\s*(\}|\])"
        # Replace the pattern with only the closing character
        return re.sub(pattern, r"\1", json_string)

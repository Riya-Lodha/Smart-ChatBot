import json
from pathlib import Path
import random
from fuzzywuzzy import fuzz


class ChatBot:
    def __init__(self):
        self.intents = self._load_intents()
        self.patterns_dict = self._create_patterns_dict()

    def _load_intents(self):
        intents_file = Path("model/intents.json")
        with open(intents_file, "r") as f:
            return json.load(f)["intents"]

    def _create_patterns_dict(self):
        patterns_dict = {}
        for intent in self.intents:
            for pattern in intent["patterns"]:
                patterns_dict[pattern.lower()] = intent
        return patterns_dict

    def get_response(self, text):
        text = text.lower()
        best_match = {
            "intent": "unknown",
            "response": "I'm not sure how to respond to that.",
            "confidence": 0.0
        }
        highest_ratio = 0
        best_pattern = None

        for pattern in self.patterns_dict.keys():
            simple_ratio = fuzz.ratio(text, pattern) / 100
            partial_ratio = fuzz.partial_ratio(text, pattern) / 100
            token_sort_ratio = fuzz.token_sort_ratio(text, pattern) / 100
            token_set_ratio = fuzz.token_set_ratio(text, pattern) / 100

            max_ratio = max(simple_ratio, partial_ratio, token_sort_ratio, token_set_ratio)

            if max_ratio > highest_ratio:
                highest_ratio = max_ratio
                best_pattern = pattern

        if highest_ratio > 0.8:
            matched_intent = self.patterns_dict[best_pattern]
            best_match = {
                "intent": matched_intent["tag"],
                "response": random.choice(matched_intent["responses"]),
                "confidence": highest_ratio,
                "matched_pattern": best_pattern
            }

        return best_match

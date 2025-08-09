import os

MODEL_REGISTRY = {
    "PLANNER": [
        os.getenv("MODEL_PLANNER_PRIMARY", "google/gemini-flash-1.5"),
        os.getenv("MODEL_PLANNER_FALLBACK", "mistralai/mistral-7b-instruct:free")
    ],
    "TEXT_TO_SQL": [
        os.getenv("MODEL_SQL_PRIMARY", "google/gemini-flash-1.5"),
        os.getenv("MODEL_SQL_FALLBACK", "mistralai/mistral-7b-instruct:free")
    ],
    "REASONER": [
        os.getenv("MODEL_REASONER_PRIMARY", "mistralai/mistral-7b-instruct:free"),
        os.getenv("MODEL_REASONER_FALLBACK", "google/gemini-flash-1.5")
    ],
    "SYNTHESIZER": [
        os.getenv("MODEL_SYNTHESIZER_PRIMARY", "mistralai/mistral-7b-instruct:free"),
        os.getenv("MODEL_SYNTHESIZER_FALLBACK", "google/gemini-flash-1.5")
    ],
    "GENERIC": [
        os.getenv("MODEL_GENERIC_PRIMARY", "google/gemini-flash-1.5"),
        os.getenv("MODEL_GENERIC_FALLBACK", "mistralai/mistral-7b-instruct:free")
    ]
}

def get_model_chain(role: str):
    return [m for m in MODEL_REGISTRY.get(role, MODEL_REGISTRY["GENERIC"]) if m]
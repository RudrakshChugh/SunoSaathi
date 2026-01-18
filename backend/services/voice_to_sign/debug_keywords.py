
import spacy
import re

# Mock the setup from app.py
nlp = spacy.load("en_core_web_sm")

SIGN_DICT = {
    "me": "me",
    "you": "you",
    "your": "you",
    "doctor": "doctor",
    "hospital": "hospital",
    "help": "help",
    "water": "water",
    "meet": "meet",
    "need": "need",
    "thank": "thankyou",
    "right": "right",
    "left": "left",
    "stop": "stop",
    "go": "go",
    "bus": "bus",
    "train": "train",
    "food": "food",
    "home": "home",
    "lawyer": "lawyer",
    "toilet": "toilet",
    "washroom": "toilet",
    "house": "home",
    # New additions
    "fever": "fever",
    "pain": "pain",
    "medicine": "medicine",
    "emergency": "emergency",
    "call": "call",
    "family": "family",
    "please": "please",
    "yes": "yes",
    "no": "no",
    "where": "where",
    "when": "when",
    "why": "why",
    "name": "name",
    "good": "good",
    "bad": "bad",
    "stomach": "stomach",
    "head": "head",
    "leg": "leg",
    "hand": "hand",
    "wait": "wait"
}

IMPORTANT_WORDS = set(SIGN_DICT.keys())

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()

def process_text(text):
    clean = clean_text(text)
    print(f"Clean text: '{clean}'")

    keywords = []
    if "i" in clean or "me" in clean:
        keywords.append("me")

    doc = nlp(clean)
    for token in doc:
        lemma = token.lemma_
        print(f"Token: {token.text}, Lemma: {lemma}, In Dict: {lemma in IMPORTANT_WORDS}")
        
        if lemma in IMPORTANT_WORDS and lemma not in keywords:
            keywords.append(lemma)
            
    print(f"Extracted Keywords: {keywords}")

# Test the failing sentence
process_text("I have fever and have pain")

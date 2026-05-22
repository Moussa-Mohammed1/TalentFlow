from typing import Dict, List
from transformers import pipeline

LABELS = [
    "experience",
    "education",
    "competence",
    "projects",
    "languages",
    "certifications",
    "profile",
    "contact",
    "interests",
]

# Lazy-loaded classifier to avoid heavy model download at import time.
classifier = None


def get_classifier():
    """Return a cached zero-shot classifier, creating it on first use."""
    global classifier
    if classifier is None:
        classifier = pipeline(
            task="zero-shot-classification",
            model="facebook/bart-large-mnli",
        )
    return classifier

def classify_chunk(text: str) -> Dict:
    
    if not text or len(text.strip()) < 2:
        return {
            "text": text,
            "label": "unknown",
            "score": 0.0,
            "all_scores": [],
        }
    
    try:
        clf = get_classifier()
        result = clf(
            sequences=text,
            candidate_labels=LABELS,
            multi_label=False,
        )
    except Exception:
        return {
            "text": text,
            "label": "unknown",
            "score": 0.0,
            "all_scores": [],
        }
    
    return {
        "text": text,
        "label": result["labels"][0],
        "score": float(result["scores"][0]),
        "all_scores": [
            {
                "label": label,
                "score": float(score),
            }
            for label, score in zip(
                result["labels"],
                result["scores"],
            )
        ]
    }
    
    
def classify_chunks(chunks: List[str]) -> List[Dict]:
    results = []
    for chunk in chunks:
        classification = classify_chunk(chunk)
        results.append(classification)
        
    return results

def group_by_category(classified_chunks: List[Dict]) -> Dict[str, List[Dict]]:
    grouped = {}
    
    for item in classified_chunks:
        category = item["label"]
        
        if category not in grouped:
            grouped[category] = []
            
        grouped[category].append(item)
        
    return grouped
    
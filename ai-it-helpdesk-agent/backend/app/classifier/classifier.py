import re
from typing import Dict, List, Optional, Tuple
from app.classifier.rules import CATEGORIES, PRIORITY_KEYWORDS


class IssueClassifier:
    def __init__(self):
        self.categories = CATEGORIES
        self.priority_keywords = PRIORITY_KEYWORDS

    def normalize_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _calculate_confidence(
        self, text: str, matched_keywords: List[str]
    ) -> float:
        if not matched_keywords:
            return 0.25

        total_words = len(text.split())
        if total_words == 0:
            return 0.25

        unique_matches = len(set(matched_keywords))
        match_ratio = unique_matches / max(total_words, 1)

        if unique_matches >= 3 or match_ratio >= 0.3:
            return min(0.95, 0.85 + (unique_matches * 0.03))
        elif unique_matches == 2 or match_ratio >= 0.15:
            return min(0.85, 0.70 + (unique_matches * 0.05))
        elif unique_matches == 1:
            return 0.55
        return 0.35

    def _detect_priority(self, text: str) -> Tuple[str, int]:
        scores = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for level, (weight, keywords_str) in self.priority_keywords.items():
            keywords = [k.strip() for k in keywords_str.split(",")]
            for keyword in keywords:
                if keyword in text:
                    scores[level] += weight

        best_level = "medium"
        best_score = scores["medium"]

        for level in ["critical", "high", "low"]:
            if scores[level] > best_score:
                best_score = scores[level]
                best_level = level

        if best_score == 0:
            return "Medium", 2

        return best_level.title(), best_score

    def _generate_reason(
        self, category: str, subcategory: str, confidence: float, text: str
    ) -> str:
        if confidence >= 0.85:
            return (
                f"The query strongly indicates a {subcategory.lower()} "
                f"issue under the {category} category."
            )
        elif confidence >= 0.70:
            return (
                f"The query suggests a {subcategory.lower()} issue, "
                f"classified under {category}."
            )
        elif confidence >= 0.55:
            return (
                f"The query appears to be related to {category}, "
                f"specifically {subcategory.lower()}."
            )
        else:
            return (
                "The query could not be confidently classified and has been "
                "categorized as Other."
            )

    def classify(self, text: str) -> Dict:
        normalized = self.normalize_text(text)
        words = normalized.split()

        best_category = "Other"
        best_subcategory = "Unknown Issue"
        best_matches: List[str] = []
        best_score = 0

        for category, subcategories in self.categories.items():
            for subcategory, keywords in subcategories.items():
                matches: List[str] = []
                score = 0
                for keyword in keywords:
                    keyword_parts = keyword.split()
                    if len(keyword_parts) == 1:
                        if keyword in words:
                            matches.append(keyword)
                            score += 1
                    else:
                        if all(part in words for part in keyword_parts):
                            matches.append(keyword)
                            score += 3

                if score > best_score:
                    best_matches = matches
                    best_category = category
                    best_subcategory = subcategory
                    best_score = score

        if best_category == "Other":
            confidence = 0.25
        else:
            confidence = self._calculate_confidence(normalized, best_matches)

        priority, priority_score = self._detect_priority(normalized)
        reason = self._generate_reason(
            best_category, best_subcategory, confidence, normalized
        )

        return {
            "success": True,
            "category": best_category,
            "subcategory": best_subcategory,
            "priority": priority,
            "confidence": round(confidence, 2),
            "reason": reason,
        }


issue_classifier = IssueClassifier()

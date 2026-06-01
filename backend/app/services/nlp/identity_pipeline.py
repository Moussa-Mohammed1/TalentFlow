from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
import json
import re
import unicodedata
from typing import Any

import spacy


NAME_BLACKLIST = {
    "developer",
    "Développeur",
    "engineer",
    "student",
    "intern",
    "experience",
    "summary",
    "profile",
    "contact",
    "formation",
    "education",
    "skills",
    "competences",
    "compétences",
    "responsible",
    "full stack developer",
    "software engineer",
    "computer science student",
}

NORMALIZED_NAME_BLACKLIST = {
    "developer",
    "developpeur",
    "engineer",
    "student",
    "intern",
    "experience",
    "summary",
    "profile",
    "contact",
    "formation",
    "education",
    "skills",
    "competences",
    "responsible",
    "full stack developer",
    "full stack",
    "software engineer",
    "computer science student",
}

LOCATION_HINTS = {
    "rabat",
    "casablanca",
    "marrakech",
    "fes",
    "fès",
    "tanger",
    "agadir",
    "sale",
    "salé",
    "kenitra",
    "kénitra",
    "meknes",
    "meknès",
    "paris",
    "lyon",
    "london",
    "montreal",
    "montréal",
    "brussels",
    "casablanca, morocco",
    "maroc",
    "morocco",
}

CONTACT_HINTS = {
    "email",
    "e-mail",
    "mail",
    "phone",
    "tel",
    "tél",
    "telephone",
    "telephone",
    "contact",
    "coordonnees",
    "coordonnées",
    "linkedin",
    "github",
}

EMAIL_PATTERN = re.compile(
    r"(?<![A-Z0-9._%+-])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})(?![A-Z0-9._%+-])",
    re.IGNORECASE,
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+\d[\d\s().-]{6,}\d|0\d[\d\s().-]{7,}\d)(?!\d)"
)

URL_PATTERN = re.compile(
    r"(?i)\b(?:https?://|www\.)\S+"
)

LINKEDIN_PATTERN = re.compile(r"(?i)\blinkedin\.com/\S+")
GITHUB_PATTERN = re.compile(r"(?i)\bgithub\.com/\S+")


@dataclass(frozen=True)
class CandidateScore:
    value: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    signals: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "confidence": round(self.confidence, 4),
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class IdentityExtractionResult:
    name: CandidateScore
    email: CandidateScore
    phone: CandidateScore
    stats: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name.to_dict(),
            "email": self.email.to_dict(),
            "phone": self.phone.to_dict(),
            "stats": self.stats,
        }


class IdentityPreprocessor:
    @staticmethod
    def _normalize_unicode(text: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        text = text.replace("\u00a0", " ").replace("\u200b", " ").replace("\ufeff", " ")
        return text

    @staticmethod
    def _merge_spaced_letters(text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            letters = re.sub(r"\s+", "", match.group(0))
            if len(letters) <= 1:
                return match.group(0)
            if letters.isupper():
                return letters
            if letters[0].isupper():
                return letters[0].upper() + letters[1:].lower()
            return letters

        return re.sub(r"(?:\b[A-Za-zÀ-ÿ]\b(?:\s+|[-·•])?){3,}", replace, text)

    @staticmethod
    def _fix_broken_lines(text: str) -> str:
        text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)
        text = re.sub(r"\r\n", "\n", text)
        return text

    @staticmethod
    def _collapse_whitespace(text: str) -> str:
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def clean(self, text: str) -> tuple[str, list[str], list[str]]:
        text = self._normalize_unicode(text or "")
        text = self._fix_broken_lines(text)
        text = self._merge_spaced_letters(text)
        lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        clean_text = self._collapse_whitespace(text)
        return clean_text, lines, clean_text.splitlines()


class IdentityValidation:
    @staticmethod
    def validate_email(candidate: str) -> bool:
        match = EMAIL_PATTERN.fullmatch(candidate.strip())
        if not match:
            return False
        local_part, domain_part = candidate.rsplit("@", 1)
        if not local_part or not domain_part or "." not in domain_part:
            return False
        if domain_part.startswith(".") or domain_part.endswith("."):
            return False
        return True

    @staticmethod
    def normalize_email(candidate: str) -> str:
        return candidate.strip().lower()

    @staticmethod
    def _digits_only(candidate: str) -> str:
        return re.sub(r"\D", "", candidate)

    @classmethod
    def validate_phone(cls, candidate: str) -> bool:
        digits = cls._digits_only(candidate)
        if len(digits) < 8 or len(digits) > 15:
            return False
        if digits in {"0" * len(digits)}:
            return False
        if re.fullmatch(r"20\d{2}20\d{2}", digits):
            return False
        if re.fullmatch(r"20\d{2}202\d", digits):
            return False
        return True

    @classmethod
    def normalize_phone(cls, candidate: str, text: str) -> str:
        raw = candidate.strip()
        digits = cls._digits_only(raw)
        if not digits:
            return raw

        text_lower = text.casefold()
        if digits.startswith("212"):
            local = digits[3:]
            if len(local) == 9 and local.startswith("0"):
                local = local[1:]
            if len(local) == 9:
                grouped = f"+212 {local[0]} {local[1:3]} {local[3:5]} {local[5:7]} {local[7:9]}"
                return grouped

        if raw.startswith("+") and 8 <= len(digits) <= 15:
            return "+" + digits

        if digits.startswith("0") and len(digits) == 10 and ("morocco" in text_lower or "maroc" in text_lower or "+212" in text):
            local = digits[1:]
            return f"+212 {local[0]} {local[1:3]} {local[3:5]} {local[5:7]} {local[7:9]}"

        return "+" + digits if len(digits) >= 8 else raw


class IdentityCandidateExtractor:
    def __init__(self) -> None:
        self.validation = IdentityValidation()
        self._nlp = self._load_spacy_model()

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_spacy_model():
        try:
            return spacy.load("fr_core_news_md")
        except Exception:
            try:
                return spacy.load("fr_core_news_sm")
            except Exception:
                return spacy.blank("fr")

    @staticmethod
    def _line_score(index: int, total: int) -> float:
        if total <= 0:
            return 0.0
        return max(0.05, 1.0 - (index / max(total - 1, 1)) * 0.8)

    @staticmethod
    def _format_score(line: str) -> float:
        stripped = line.strip()
        if not stripped:
            return 0.0
        if stripped.isupper() and 2 <= len(stripped.split()) <= 5:
            return 0.95
        words = stripped.split()
        if 2 <= len(words) <= 4 and all(word[:1].isupper() for word in words if word):
            return 0.9
        return 0.45

    @staticmethod
    def _tokenize_name(candidate: str) -> list[str]:
        return [token for token in re.split(r"\s+", candidate.strip()) if token]

    @staticmethod
    def _looks_like_name(candidate: str) -> bool:
        cleaned = re.sub(r"[^A-Za-zÀ-ÿ'\-\s]", " ", candidate).strip()
        if not cleaned:
            return False
        normalized = IdentityCandidateExtractor._normalize_name_key(cleaned)
        if any(term in normalized for term in NORMALIZED_NAME_BLACKLIST):
            return False
        if any(term in normalized for term in LOCATION_HINTS):
            return False
        if any(char.isdigit() for char in cleaned):
            return False
        words = [word for word in cleaned.split() if word]
        if not (2 <= len(words) <= 4):
            return False
        if not all(len(word) > 1 for word in words):
            return False
        if any("@" in word or "." in word for word in words):
            return False
        if any(token.casefold() in {"developer", "engineer", "student", "intern", "profile", "skills", "contact"} for token in words):
            return False
        return True

    @staticmethod
    def _normalize_name_key(candidate: str) -> str:
        normalized = unicodedata.normalize("NFKD", candidate).encode("ascii", "ignore").decode("ascii")
        normalized = normalized.casefold()
        normalized = re.sub(r"[^a-z0-9\s-]", " ", normalized)
        normalized = re.sub(r"[-–—]+", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    @staticmethod
    def _title_case_name(candidate: str) -> str:
        parts = []
        for word in re.split(r"(\s+)", candidate.strip()):
            if not word or word.isspace():
                parts.append(word)
                continue
            if "-" in word:
                parts.append("-".join(piece[:1].upper() + piece[1:].lower() for piece in word.split("-")))
            else:
                parts.append(word[:1].upper() + word[1:].lower())
        return "".join(parts).strip()

    @staticmethod
    def _contact_window(lines: list[str]) -> int:
        for index, line in enumerate(lines[:12]):
            lower = line.casefold()
            if any(hint in lower for hint in CONTACT_HINTS):
                return index
        return min(4, max(0, len(lines) - 1))

    def _extract_email_candidates(self, text: str) -> list[CandidateScore]:
        candidates: list[CandidateScore] = []
        for match in EMAIL_PATTERN.finditer(text):
            email = self.validation.normalize_email(match.group(1))
            if self.validation.validate_email(email):
                position_bonus = max(0.5, 1.0 - (match.start() / max(len(text), 1)) * 0.4)
                candidates.append(CandidateScore(email, min(0.99, 0.72 + position_bonus * 0.25), [match.group(1)], {"position": position_bonus, "pattern": 1.0, "validation": 1.0}))
        return candidates

    def _extract_phone_candidates(self, text: str) -> list[CandidateScore]:
        candidates: list[CandidateScore] = []
        for match in PHONE_PATTERN.finditer(text):
            raw_phone = match.group(0).strip()
            if re.fullmatch(r"20\d{2}\s*-\s*20\d{2}", raw_phone):
                continue
            if re.fullmatch(r"\d{4}\s*-\s*\d{4}", raw_phone):
                continue
            if not self.validation.validate_phone(raw_phone):
                continue
            normalized = self.validation.normalize_phone(raw_phone, text)
            position_bonus = max(0.4, 1.0 - (match.start() / max(len(text), 1)) * 0.4)
            digits = re.sub(r"\D", "", raw_phone)
            pattern_score = 1.0 if raw_phone.startswith("+") else 0.78
            validation_score = 1.0 if len(digits) >= 8 else 0.0
            candidates.append(CandidateScore(normalized, min(0.98, 0.66 + position_bonus * 0.25), [raw_phone], {"position": position_bonus, "pattern": pattern_score, "validation": validation_score}))
        return candidates

    def _extract_name_candidates(self, lines: list[str], text: str) -> list[CandidateScore]:
        candidates: list[CandidateScore] = []
        contact_window = self._contact_window(lines)

        for index, line in enumerate(lines[: min(len(lines), 12)]):
            if not self._looks_like_name(line):
                continue
            lower = line.casefold()
            if any(hint in lower for hint in CONTACT_HINTS):
                continue
            if any(term in lower for term in NAME_BLACKLIST):
                continue

            line_score = self._line_score(index, len(lines))
            format_score = self._format_score(line)
            proximity_score = 1.0 if index <= contact_window else 0.55
            value = self._title_case_name(line)
            candidates.append(
                CandidateScore(
                    value=value,
                    confidence=min(0.98, 0.42 + line_score * 0.32 + format_score * 0.18 + proximity_score * 0.12),
                    evidence=[line],
                    signals={"position": line_score, "format": format_score, "contact": proximity_score, "validation": 1.0},
                )
            )

        doc = self._nlp(text)
        for ent in getattr(doc, "ents", []):
            if ent.label_ != "PER":
                continue
            candidate = ent.text.strip()
            if not self._looks_like_name(candidate):
                continue
            line_index = next((i for i, line in enumerate(lines) if candidate.casefold() in line.casefold()), 0)
            line_score = self._line_score(line_index, len(lines))
            ner_score = 0.95 if len(candidate.split()) >= 2 else 0.65
            value = self._title_case_name(candidate)
            candidates.append(
                CandidateScore(
                    value=value,
                    confidence=min(0.96, 0.34 + line_score * 0.26 + ner_score * 0.28 + self._format_score(lines[line_index] if lines else candidate) * 0.12),
                    evidence=[candidate],
                    signals={"position": line_score, "format": self._format_score(lines[line_index] if lines else candidate), "ner": ner_score, "validation": 1.0},
                )
            )

        filtered: list[CandidateScore] = []
        for item in candidates:
            normalized = self._normalize_name_key(item.value)
            if any(term in normalized for term in NORMALIZED_NAME_BLACKLIST):
                continue
            filtered.append(item)

        return filtered

    @staticmethod
    def _best_candidate(candidates: list[CandidateScore]) -> CandidateScore:
        if not candidates:
            return CandidateScore(value="", confidence=0.0, evidence=[])
        ranked = sorted(candidates, key=lambda item: (-item.confidence, item.value.casefold()))
        best = ranked[0]
        merged_evidence = []
        seen = set()
        for candidate in ranked[:3]:
            for evidence in candidate.evidence:
                if evidence not in seen:
                    merged_evidence.append(evidence)
                    seen.add(evidence)
        return CandidateScore(value=best.value, confidence=best.confidence, evidence=merged_evidence, signals=best.signals)

    def extract(self, text: str) -> IdentityExtractionResult:
        preprocessor = IdentityPreprocessor()
        clean_text, lines, _ = preprocessor.clean(text)
        email_candidates = self._extract_email_candidates(clean_text)
        phone_candidates = self._extract_phone_candidates(clean_text)
        name_candidates = self._extract_name_candidates(lines, clean_text)

        email = self._best_candidate(email_candidates)
        phone = self._best_candidate(phone_candidates)
        name = self._best_candidate(name_candidates)

        stats = {
            "line_count": len(lines),
            "email_candidates": len(email_candidates),
            "phone_candidates": len(phone_candidates),
            "name_candidates": len(name_candidates),
            "spacy_model": self._nlp.meta.get("name", "unknown") if hasattr(self._nlp, "meta") else "unknown",
        }

        return IdentityExtractionResult(name=name, email=email, phone=phone, stats=stats)


class ResumeIdentityExtractionPipeline:
    def __init__(self) -> None:
        self.extractor = IdentityCandidateExtractor()

    def analyze(self, text: str) -> dict[str, Any]:
        return self.extractor.extract(text).to_dict()


class ResumeIdentityExtractor:
    def __init__(self) -> None:
        self.pipeline = ResumeIdentityExtractionPipeline()

    def extract_identity(self, text: str) -> dict[str, Any]:
        return self.pipeline.analyze(text)

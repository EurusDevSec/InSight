"""
Strict RAG grounding validator.

Task 3.3 — Validates that LLM-generated responses are grounded
in the retrieved knowledge chunks (anti-hallucination).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from knowledge_base.schemas import SearchResult


@dataclass
class GroundingResult:
    """Outcome of a grounding validation check."""

    is_grounded: bool
    grounding_score: float  # 0.0 - 1.0
    matched_sources: list[str]
    ungrounded_claims: list[str]
    explanation: str


# Key medical terms that MUST be sourced from guidelines
_MEDICAL_CLAIMS_PATTERN = re.compile(
    r"(?:recommend|should|must|administer|take|inject|dose|unit)"
    r".*?(?:\d+\.?\d*\s*(?:U|unit|mg|g|ml|IU))",
    re.IGNORECASE,
)


class GroundingValidator:
    """Validates LLM output against retrieved knowledge chunks.

    Strategy:
        1. Extract factual claims from the LLM response.
        2. For each claim, check if key terms appear in retrieved chunks.
        3. Flag claims that have no supporting chunk.
    """

    def __init__(self, min_grounding_score: float = 0.5) -> None:
        self.min_grounding_score = min_grounding_score

    def validate(
        self,
        llm_response: str,
        retrieved_chunks: list[SearchResult],
    ) -> GroundingResult:
        """Check if the LLM response is grounded in retrieved chunks.

        Args:
            llm_response: Raw text from LLM.
            retrieved_chunks: Chunks used to build the prompt.

        Returns:
            GroundingResult with score and details.
        """
        if not llm_response or not retrieved_chunks:
            return GroundingResult(
                is_grounded=False,
                grounding_score=0.0,
                matched_sources=[],
                ungrounded_claims=[],
                explanation=(
                    "Cannot validate: empty response or no retrieved chunks."
                ),
            )

        # Combine all chunk text for matching
        chunk_corpus = " ".join(c.content.lower() for c in retrieved_chunks)
        chunk_sources = {c.source for c in retrieved_chunks}

        # Extract sentences with medical claims
        claims = self._extract_claims(llm_response)
        if not claims:
            # If no specific medical claims, check for general overlap
            score = self._text_overlap_score(llm_response, chunk_corpus)
            return GroundingResult(
                is_grounded=score >= self.min_grounding_score,
                grounding_score=round(score, 2),
                matched_sources=list(chunk_sources),
                ungrounded_claims=[],
                explanation="No specific medical claims detected; "
                "general text overlap used.",
            )

        # Check each claim against chunks
        grounded: list[str] = []
        ungrounded: list[str] = []
        matched_sources: set[str] = set()

        for claim in claims:
            is_supported, matching_src = self._check_claim(
                claim, retrieved_chunks, chunk_corpus
            )
            if is_supported:
                grounded.append(claim)
                matched_sources.update(matching_src)
            else:
                ungrounded.append(claim)

        total = len(claims)
        score = len(grounded) / total if total else 0.0

        return GroundingResult(
            is_grounded=score >= self.min_grounding_score,
            grounding_score=round(score, 2),
            matched_sources=sorted(matched_sources),
            ungrounded_claims=ungrounded,
            explanation=(
                f"{len(grounded)}/{total} claims grounded in retrieved sources."
            ),
        )

    # ── Internal ───────────────────────────────────────────────────

    def _extract_claims(self, text: str) -> list[str]:
        """Extract sentences that contain medical claims/dosing info."""
        claims: list[str] = []
        sentences = re.split(r"[.!?\n]", text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            if _MEDICAL_CLAIMS_PATTERN.search(sent):
                claims.append(sent)
        return claims

    @staticmethod
    def _check_claim(
        claim: str,
        chunks: list[SearchResult],
        corpus: str,
    ) -> tuple[bool, list[str]]:
        """Check if a single claim is supported by any retrieved chunk.

        Uses keyword overlap: if ≥40% of significant words in the claim
        also appear in the chunk corpus, consider it grounded.
        """
        words = _extract_significant_words(claim)
        if not words:
            return True, []  # trivial claim

        matched_count = sum(1 for w in words if w in corpus)
        ratio = matched_count / len(words)

        if ratio >= 0.4:
            # Find which source(s) supported
            sources = []
            claim_lower = claim.lower()
            for chunk in chunks:
                chunk_words = set(chunk.content.lower().split())
                overlap = sum(1 for w in words if w in chunk_words)
                if overlap >= len(words) * 0.3:
                    sources.append(chunk.source)
            return True, sources

        return False, []

    @staticmethod
    def _text_overlap_score(text: str, corpus: str) -> float:
        """Compute a simple word-overlap score between text and corpus."""
        words = _extract_significant_words(text)
        if not words:
            return 0.0
        matched = sum(1 for w in words if w in corpus)
        return matched / len(words)


# ── Helpers ────────────────────────────────────────────────────────

_STOP_WORDS = frozenset(
    "a an the is are was were be been being have has had do does did "
    "will would shall should may might can could and or but if then else "
    "for of to in on at by from with as this that it its they them their "
    "he she we you i my your his her our not no".split()
)


def _extract_significant_words(text: str) -> list[str]:
    """Extract lowercase words that are not stop words or very short."""
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    return [w for w in words if w not in _STOP_WORDS]

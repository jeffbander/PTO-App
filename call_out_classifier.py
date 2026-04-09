"""
Call-out classification logic.

Decides whether a call-out request should be counted as 'sick' or 'fmla'
for statistics purposes, based on the free-text message the employee wrote.

Rules (case-insensitive):
  - The standalone word "fmla" (word boundary) -> 'fmla'
  - The phrase "family medical leave" -> 'fmla'
  - The phrase "family and medical leave" -> 'fmla'
  - Everything else (including None/empty, and phrases like "family emergency") -> 'sick'

"family" alone does NOT trigger FMLA.
"""
import re

_FMLA_WORD = re.compile(r'\bfmla\b', re.IGNORECASE)
_FMLA_PHRASES = (
    'family medical leave',
    'family and medical leave',
)


def classify_call_out(message_text):
    """Return 'fmla' or 'sick' based on call-out message content."""
    if not message_text:
        return 'sick'

    lowered = message_text.lower()

    if _FMLA_WORD.search(lowered):
        return 'fmla'

    for phrase in _FMLA_PHRASES:
        if phrase in lowered:
            return 'fmla'

    return 'sick'

from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from .config import settings
from .models import ClassificationResult

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """Sei un assistente che classifica le email aziendali.

Categorie disponibili: {categories}

Analizza l'email seguente e rispondi SOLO con un JSON valido con questa struttura:
{{
  "category": "<categoria>",
  "confidence": <float 0-1>,
  "summary": "<riassunto breve in italiano>",
  "suggested_reply": "<bozza di risposta professionale in italiano>"
}}

--- EMAIL ---
Da: {sender}
Oggetto: {subject}
Corpo:
{body}
--- FINE EMAIL ---
"""


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


async def classify_email(
    sender: str, subject: str, body: str
) -> ClassificationResult:
    """Classify an email using OpenAI-compatible API."""
    client = _get_client()

    categories_str = ", ".join(settings.categories)
    prompt = CLASSIFICATION_PROMPT.format(
        categories=categories_str,
        sender=sender,
        subject=subject,
        body=body[:3000],  # limit body length
    )

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000,
    )

    content = response.choices[0].message.content or "{}"

    # Extract JSON from response (handle markdown code blocks)
    if "```" in content:
        start = content.find("{")
        end = content.rfind("}") + 1
        content = content[start:end]

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM response: %s", content)
        data = {
            "category": "altro",
            "confidence": 0.0,
            "summary": "Classificazione fallita",
            "suggested_reply": "",
        }

    # Validate category
    if data.get("category") not in settings.categories:
        data["category"] = "altro"

    return ClassificationResult(**data)


async def generate_custom_reply(
    sender: str, subject: str, body: str, instructions: str
) -> str:
    """Generate a custom reply based on user instructions."""
    client = _get_client()

    prompt = f"""Genera una risposta professionale in italiano per questa email.

Istruzioni aggiuntive: {instructions}

--- EMAIL ---
Da: {sender}
Oggetto: {subject}
Corpo:
{body[:3000]}
--- FINE EMAIL ---

Scrivi solo il testo della risposta, senza intestazioni o firme."""

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=1000,
    )

    return response.choices[0].message.content or ""

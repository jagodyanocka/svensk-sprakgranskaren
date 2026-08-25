import logging

from app.db.models import Interaction
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


def save_interaction(*, language: str, input_text: str, output_text: str) -> None:
    if not input_text.strip() or not output_text.strip():
        return

    try:
        with SessionLocal() as session:
            session.add(
                Interaction(
                    language=language,
                    input_text=input_text,
                    output_text=output_text,
                )
            )
            session.commit()
    except Exception:
        logger.exception("Failed to save interaction")

from .fastapi import instrument_fastapi
from .flask import instrument_flask

__all__ = ['instrument_fastapi', 'instrument_flask']
__name__ = "sre_metrics"  # Should be underscore
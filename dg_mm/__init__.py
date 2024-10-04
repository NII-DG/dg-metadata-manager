from logging import getLogger, NullHandler

from dg_mm.models.metadata_manager import MetadataManger

logger = getLogger(__name__)
logger.addHandler(NullHandler())


__version__ = '1.0.0'

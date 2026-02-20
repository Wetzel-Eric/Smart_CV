import pytest
from unittest.mock import AsyncMock, MagicMock
from core.bootstrap_core import BootstrapCore, BootstrapError
from core.dependencies import Container

@pytest.mark.asyncio
async def test_bootstrap_success(mocker):
    # Mock des dépendances
    mock_reader = AsyncMock()
    mock_reader.load.return_value = [MagicMock()]

    mock_chunker = AsyncMock()
    mock_chunker.chunk.return_value = [MagicMock()]

    mock_retriever = AsyncMock()

    container = Container()
    container.reader.override(mock_reader)
    container.chunker.override(mock_chunker)
    container.retriever.override(mock_retriever)

    # Test
    core = BootstrapCore(container)
    pipeline = await core.initialize()
    assert pipeline is not None

@pytest.mark.asyncio
async def test_bootstrap_pdf_missing(mocker):
    container = Container()
    container.config.pdf_path.override("inexistant.pdf")

    core = BootstrapCore(container)
    with pytest.raises(BootstrapError):
        await core.initialize()

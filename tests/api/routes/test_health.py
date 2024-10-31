import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_healthcheck(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

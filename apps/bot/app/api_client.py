from typing import Any

import aiohttp


class TrainingApiClient:
    def __init__(self, api_url: str) -> None:
        self.api_url = api_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "TrainingApiClient":
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._session is not None:
            await self._session.close()

    async def get_today_workout(self) -> dict[str, Any]:
        if self._session is None:
            raise RuntimeError("TrainingApiClient must be used as an async context manager")
        async with self._session.get(f"{self.api_url}/workouts/today") as response:
            response.raise_for_status()
            return await response.json()

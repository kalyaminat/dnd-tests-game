# tests/conftest.py
import pytest
from tests.dnd_client import DnDGameClient


@pytest.fixture
def api_client():
    """Фикстура: создает HTTP клиента для API запросов"""
    return DnDGameClient()


@pytest.fixture
def logged_in_client(api_client):
    """Фикстура: клиент с уже выполненным логином"""
    # Логинимся с тестовыми данными
    api_client.login(
        username="mark123",
        password="Resolution2026!",
        email="mark123@example.com"  # ← теперь не gmail
    )
    return api_client


@pytest.fixture
def client_with_battle_map(logged_in_client):
    """Фикстура: клиент с загруженной картой"""
    logged_in_client.get_battle_map()
    return logged_in_client


@pytest.fixture
def client_with_monsters(client_with_battle_map):
    """Фикстура: клиент с загруженными монстрами"""
    client_with_battle_map.get_game_monsters()
    return client_with_battle_map


@pytest.fixture
def client_with_scenario(client_with_monsters):
    """Фикстура: клиент с созданным сценарием (есть lobby_id)"""
    client_with_monsters.create_game_scenario()
    return client_with_monsters
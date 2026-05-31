# tests/dnd_client.py
import requests
import os
import time
from typing import Dict, Any, Optional


class DnDGameClient:
    """Клиент для работы с API D&D игры"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or "https://api.test.dnd.ktsf.ru/api/v1"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.context: Dict[str, Any] = {}

    def set_auth_token(self, token: str):
        """Установить токен авторизации"""
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    # ============ Шаг 1: Логин ============
    def login(self, username: str = "mark123", password: str = "Resolution2026!", email: str = None) -> Dict[str, Any]:
        """POST /auth/login/ - аутентификация"""
        # Если email не указан, формируем из username
        if email is None:
            email = f"{username}@example.com"

        response = self.session.post(
            f"{self.base_url}/auth/login/",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        response.raise_for_status()
        data = response.json()

        # Сохраняем токены в контекст
        self.context["access_token"] = data["access"]
        self.context["refresh_token"] = data["refresh"]
        self.context["user_id"] = data["user"]["pk"]
        self.context["username"] = data["user"]["username"]
        self.context["email"] = email

        # Автоматически устанавливаем токен для следующих запросов
        self.set_auth_token(data["access"])

        return data

    # ============ Шаг 2: Получение карты ============
    def get_battle_map(self, map_index: int = 0) -> Dict[str, Any]:
        """GET /battle-maps/battle-maps/ - получение списка карт"""
        response = self.session.get(f"{self.base_url}/battle-maps/battle-maps/")
        response.raise_for_status()

        data = response.json()
        if data.get("results"):
            self.context["map_id"] = data["results"][map_index]["id"]
            self.context["map_name"] = data["results"][map_index]["name"]

        return data

    # ============ Шаг 3: Получение монстров ============
    def get_game_monsters(self, limit: int = 4) -> Dict[str, Any]:
        """GET /creatures/game-monsters/ - получение списка монстров"""
        response = self.session.get(f"{self.base_url}/creatures/game-monsters/")
        response.raise_for_status()

        data = response.json()
        if data.get("results"):
            self.context["monster_ids"] = [m["id"] for m in data["results"][:limit]]

        return data

    # ============ Шаг 4: Создание сценария (POST) ============
    def create_game_scenario(self, name: str = None) -> Dict[str, Any]:
        """POST /game-scenario/game-scenarios/ - создание сценария"""
        if not name:
            name = f"AutoTest_{os.getpid()}_{int(time.time())}"

        payload = {
            "name": name,
            "map": self.context.get("map_id", 1),
            "monsters": self.context.get("monster_ids", [1, 2, 6, 7])[:4]
        }

        response = self.session.post(
            f"{self.base_url}/game-scenario/game-scenarios/",
            json=payload
        )
        response.raise_for_status()

        data = response.json()

        # ИЗВЛЕКАЕМ lobby_id из ответа
        if "lobby_id" in data:
            self.context["lobby_id"] = data["lobby_id"]
        elif "id" in data:
            self.context["lobby_id"] = data["id"]

        self.context["scenario_name"] = name

        return data

    # ============ Шаг 5: Получение лобби (GET по ID) ============
    def get_lobby_details(self, lobby_id: int = None) -> Dict[str, Any]:
        """GET /game-scenario/game-lobbies/{id} - получение лобби"""
        if lobby_id is None:
            lobby_id = self.context.get("lobby_id")

        response = self.session.get(
            f"{self.base_url}/game-scenario/game-lobbies/{lobby_id}"
        )
        response.raise_for_status()

        data = response.json()

        # ИЗВЛЕКАЕМ game_scenario_id из ответа
        if "game_scenario" in data:
            self.context["game_scenario_id"] = data["game_scenario"]
        elif "game_scenario_id" in data:
            self.context["game_scenario_id"] = data["game_scenario_id"]

        self.context["host_id"] = data.get("host")
        self.context["max_slots"] = data.get("max_slots")
        self.context["players_count"] = data.get("players_count", 0)

        return data

    # ============ Шаг 6: Получение сценария (GET по ID) ============
    def get_scenario_details(self, scenario_id: int = None) -> Dict[str, Any]:
        """GET /game-scenario/game-scenarios/{id} - получение сценария"""
        if scenario_id is None:
            scenario_id = self.context.get("game_scenario_id")

        response = self.session.get(
            f"{self.base_url}/game-scenario/game-scenarios/{scenario_id}"
        )
        response.raise_for_status()

        data = response.json()

        self.context["scenario_map_id"] = data["battle_map"]["id"]
        self.context["scenario_map_name"] = data["battle_map"]["name"]
        self.context["scenario_created_at"] = data["created_at"]

        return data

    # ============ Геттеры ============
    def get_access_token(self) -> Optional[str]:
        return self.context.get("access_token")

    def get_lobby_id(self) -> Optional[int]:
        return self.context.get("lobby_id")

    def get_game_scenario_id(self) -> Optional[int]:
        return self.context.get("game_scenario_id")

    def get_context(self) -> Dict[str, Any]:
        return self.context.copy()
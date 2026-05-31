# tests/test_dnd_game.py
import pytest
import requests
import time
from tests.dnd_client import DnDGameClient


class TestDnDGameFlow:
    """
    Тесты игрового процесса D&D
    """

    # ============ Тест 1: Полный сценарий ============
    def test_full_game_flow(self, logged_in_client):
        """
        E2E тест: все 6 шагов последовательно
        Проверяет создание игры, лобби, сценария
        """
        client = logged_in_client

        # Выполняем все шаги
        client.get_battle_map()
        client.get_game_monsters()
        client.create_game_scenario()
        client.get_lobby_details()
        client.get_scenario_details()

        # Проверяем результаты
        context = client.get_context()
        assert context.get("access_token") is not None, "Access token не получен"
        assert context.get("lobby_id") is not None, "lobby_id не извлечен"
        assert context.get("game_scenario_id") is not None, "game_scenario_id не извлечен"
        assert context["map_id"] == context["scenario_map_id"], "ID карт не совпадают"

        print(f"\n✅ Полный сценарий пройден!")
        print(f"   Lobby ID: {context['lobby_id']}")
        print(f"   Game Scenario ID: {context['game_scenario_id']}")

    # ============ Тест 2: Только логин ============
    def test_login_only(self, api_client):
        """
        Проверка аутентификации
        """
        result = api_client.login()

        assert "access" in result, "Нет поля access в ответе"
        assert "refresh" in result, "Нет поля refresh в ответе"
        assert len(result["access"]) > 50, "Токен слишком короткий"
        assert result["user"]["username"] is not None, "Нет username в ответе"

        print(f"\n✅ Логин пользователя верный: {result['user']['username']}")

    # ============ Тест 3: Создание сценария ============
    def test_create_scenario_only(self, client_with_monsters):
        """
        Проверка создания игрового сценария
        """
        client = client_with_monsters
        result = client.create_game_scenario()

        # Проверяем, что lobby_id извлечен
        assert "lobby_id" in result or "id" in result, "lobby_id не получен"
        assert client.get_lobby_id() is not None, "lobby_id не сохранен в контекст"
        assert isinstance(client.get_lobby_id(), int), "lobby_id должен быть числом"

        print(f"\n✅ Сценарий создан, lobby_id: {client.get_lobby_id()}")

    # ============ Тест 4: Цепочка извлечения переменных ============
    def test_variable_extraction_chain(self, client_with_scenario):
        """
        Проверка извлечения lobby_id и game_scenario_id через GET запросы
        """
        client = client_with_scenario

        # Проверяем, что lobby_id уже извлечен из POST /game-scenarios/
        lobby_id = client.get_lobby_id()
        assert lobby_id is not None, "lobby_id не извлечен из POST ответа"
        assert isinstance(lobby_id, int), f"lobby_id должен быть int, получен {type(lobby_id)}"
        print(f"\n✅ lobby_id извлечен из POST: {lobby_id}")

        # Извлекаем game_scenario_id из GET /game-lobbies/{id}
        client.get_lobby_details()
        game_scenario_id = client.get_game_scenario_id()
        assert game_scenario_id is not None, "game_scenario_id не извлечен из GET лобби"
        assert isinstance(game_scenario_id, int), f"game_scenario_id должен быть int, получен {type(game_scenario_id)}"
        print(f"✅ game_scenario_id извлечен из GET лобби: {game_scenario_id}")

        # Финальная проверка
        assert game_scenario_id > 0, "game_scenario_id должен быть положительным числом"

    # ============ Тест 5: Негативный сценарий ============
    def test_login_with_wrong_password_fails(self, api_client):
        """
        Проверка ошибки при неверном пароле
        """
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            api_client.login(
                username="mark123",
                password="wrong_password!"
            )

        assert exc_info.value.response.status_code in [400, 401, 403], \
            f"Ожидался статус 400/401/403, получен {exc_info.value.response.status_code}"

        print("\n✅ Неверный пароль корректно отклонен")
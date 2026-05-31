# D&D API Autotests

Автотесты для тестирования игрового API D&D.

# Установка


### 1. Клонировать репозиторий
git clone https://github.com/kalyaminat/dnd-tests-game.git
cd dnd-tests-game

### 2. Создать виртуальное окружение
python -m venv .venv

### 3. Активировать
.venv\Scripts\activate  # Windows
 source .venv/bin/activate   (Mac/Linux}

### 4. Установить зависимости
pip install -r requirements.txt

### 5. Настроить переменные окружения
cp .env.example .env
Отредактируй .env, укажи свои TEST_USERNAME и TEST_PASSWORD
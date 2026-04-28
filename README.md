# File Manager

Учебный файловый менеджер на Python с обязательным интерфейсом командной строки и дополнительным псевдографическим интерфейсом на `Textual`. Проект построен модульно: команды вынесены по областям, логика файловых операций живет в `core`, а конфигурация, пользователи и квоты отделены от UI.

## Что умеет проект

- Навигация по файловой системе внутри разрешенной рабочей области.
- Работа с файлами: создание, чтение, запись, копирование, перемещение, переименование и удаление.
- Работа с директориями: просмотр содержимого, создание папок, удаление и переходы между каталогами.
- Архивация и распаковка файлов.
- Регистрация пользователей, автоматическое создание домашней папки и переключение между пользователями.
- Проверка путей для защиты от выхода за пределы рабочей директории.
- Поддержка конфигурации через `config/config.json`.
- Квотирование дискового пространства и ограничение размера файлов для чтения.
- Дополнительный двухпанельный TUI-интерфейс.

## Структура проекта

```text
lk5-6_file_manager/
├── config/
│   └── config.json
├── examples/
│   └── demo_commands.txt
├── src/
│   └── file_manager/
│       ├── main.py
│       ├── commands/
│       │   ├── archive_commands.py
│       │   ├── command_parser.py
│       │   ├── directory_commands.py
│       │   ├── file_commands.py
│       │   ├── navigation_commands.py
│       │   └── user_commands.py
│       ├── core/
│       │   ├── config_loader.py
│       │   ├── exceptions.py
│       │   ├── file_manager.py
│       │   ├── path_guard.py
│       │   └── path_quard.py
│       ├── ui/
│       │   ├── app.py
│       │   ├── css/
│       │   └── widgets/
│       ├── users/
│       │   ├── user_manager.py
│       │   └── users.json
│       └── utils/
│           ├── disk_quota.py
│           ├── helpers.py
│           └── validators.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone <repository-url>
cd lk5-6_file_manager
```

### 2. Создать виртуальное окружение

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Для Windows:

```bash
.venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Запустить файловый менеджер в режиме командной строки

```bash
PYTHONPATH=src python -m file_manager.main
```

Можно также использовать интерпретатор из локального окружения проекта:

```bash
PYTHONPATH=src ./venv/bin/python -m file_manager.main
```

### 5. Запустить дополнительный псевдографический интерфейс

```bash
PYTHONPATH=src python -m file_manager.main --tui
```

Если модуль `textual` недоступен в системном Python, используйте локальное окружение:

```bash
PYTHONPATH=src ./venv/bin/python -m file_manager.main --tui
```

## Пример конфигурации

Файл `config/config.json` может хранить базовые настройки приложения:

```json
{
  "root_dir": "workspace",
  "users_file": "src/file_manager/users/users.json",
  "default_user": "default",
  "max_file_size_mb": 5,
  "disk_quota_mb": 50,
  "allow_archives": true
}
```

Возможные параметры:

| Параметр | Описание |
| --- | --- |
| `root_dir` | Корневая папка, внутри которой создаются домашние каталоги пользователей. |
| `users_file` | JSON-файл со списком пользователей. |
| `default_user` | Пользователь, под которым CLI запускается по умолчанию. |
| `max_file_size_mb` | Максимальный размер файла для операций чтения и копирования. |
| `disk_quota_mb` | Общая квота на пользовательские файлы. |
| `allow_archives` | Разрешает или запрещает операции с архивами. |

## Примеры команд

```text
help
pwd
ls
cd documents
mkdir reports
touch notes.txt
write notes.txt "demo text"
read notes.txt
copy notes.txt reports/notes_backup.txt
move reports/notes_backup.txt archive/notes_backup.txt
rename notes.txt todo.txt
delete todo.txt
zip reports reports.zip
unzip reports.zip extracted_reports
register student2
login student2
whoami
quota
exit
```

Список демонстрационных команд можно хранить в `examples/demo_commands.txt`.

## Архитектура

Проект разделен на несколько независимых слоев:

| Слой | Назначение |
| --- | --- |
| `commands` | Обработка пользовательских команд и маршрутизация действий. |
| `core` | Основная бизнес-логика файлового менеджера, конфигурация, исключения и защита путей. |
| `users` | Регистрация пользователей и создание персональных директорий. |
| `utils` | Вспомогательные функции: валидация, квоты, форматирование и прочие утилиты. |
| `ui` | Дополнительный псевдографический интерфейс поверх того же ядра. |

Такое разделение упрощает развитие проекта: новые команды можно добавлять в `commands`, не смешивая пользовательский интерфейс с логикой работы файловой системы.

## Идеи для развития

- Реализовать роли пользователей и разные уровни доступа.
- Добавить журналирование операций.
- Поддержать поиск файлов по имени, расширению и содержимому.
- Добавить тесты для команд, валидаторов и защиты путей.
- Сделать цветной вывод в терминале.

## Разработка

Перед изменениями удобно запускать проект из корня репозитория:

```bash
PYTHONPATH=src python -m file_manager.main
```

Рекомендуемая структура новых команд:

1. Добавить обработчик в подходящий файл внутри `src/file_manager/commands/`.
2. Зарегистрировать команду в `command_parser.py`.
3. Вынести общую логику в `core` или `utils`, если она используется в нескольких местах.
4. Добавить пример использования в `examples/demo_commands.txt`.

## Лицензия

Проект создан в учебных целях. Лицензию можно добавить отдельно, если проект будет опубликован или использоваться за пределами учебной работы.

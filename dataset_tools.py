"""
Инструменты для работы с датасетом лабораторной работы №2.

Модуль содержит функции для формирования CSV-аннотаций, преобразования
имён файлов и работы с экземплярами классов как через функцию, так и
через итераторы.
"""
import json
import os
import random
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

import pandas as pd

IMAGE_EXTENSIONS = {".jpg", ".jpeg"}
RANDOM_NUMBER_MIN = 0
RANDOM_NUMBER_MAX = 10000

_ITERATORS: dict[str, Iterator[Path]] = {}


def get_dataset_files(dataset_dir: Path) -> list[Path]:
    """Возвращает список изображений исходного датасета."""
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Исходный датасет не найден: {dataset_dir}")

    files = [
        path
        for path in dataset_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return sorted(files)


def get_class_from_path(path: Path, dataset_dir: Path) -> str:
    """Возвращает метку класса по имени подпапки датасета."""
    relative_path = path.relative_to(dataset_dir)
    if len(relative_path.parts) < 2:
        raise ValueError(f"Не удалось определить класс для файла: {path}")
    return relative_path.parts[0]


def _normalise_relative_path(path: Path, project_dir: Path) -> str:
    """Преобразует путь в строку относительно корня Python-проекта."""
    relative = os.path.relpath(path.resolve(), project_dir.resolve())
    return Path(relative).as_posix()


def load_manifest(manifest_path: Path) -> dict[str, dict]:
    """Загружает manifest лабораторной работы 1 по относительному пути."""
    if not manifest_path.exists():
        return {}

    records = {}
    with manifest_path.open("r", encoding="utf-8") as manifest:
        for line in manifest:
            if not line.strip():
                continue
            record = json.loads(line)
            file_path = record.get("file")
            if file_path:
                records[Path(file_path).as_posix()] = record
    return records


def get_source_url(
    path: Path,
    dataset_dir: Path,
    manifest: dict[str, dict],
) -> str:
    """Возвращает URL исходного изображения из manifest лабораторной работы 1."""
    relative = path.relative_to(dataset_dir).as_posix()
    record = manifest.get(f"dataset/{relative}", {})
    return record.get("source_url", "")


def get_file_date_iso(path: Path) -> str:
    """Возвращает дату изменения файла в формате ISO 8601."""
    timestamp = path.stat().st_mtime
    return datetime.fromtimestamp(timestamp).astimezone().isoformat(
        timespec="seconds"
    )


def build_source_files_table(
    dataset_dir: Path,
    project_dir: Path,
    manifest_path: Path,
) -> pd.DataFrame:
    """Создаёт таблицу файлов с датами, ссылками, путями и классами."""
    manifest = load_manifest(manifest_path)
    rows = []

    for path in get_dataset_files(dataset_dir):
        class_name = get_class_from_path(path, dataset_dir)
        rows.append(
            {
                "date": get_file_date_iso(path),
                "source_url": get_source_url(path, dataset_dir, manifest),
                "file_name": path.name,
                "absolute_path": str(path.resolve()),
                "relative_path": _normalise_relative_path(path, project_dir),
                "output_class": class_name,
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "date",
            "source_url",
            "file_name",
            "absolute_path",
            "relative_path",
            "output_class",
        ],
    )


def save_dataframe(dataframe: pd.DataFrame, output_path: Path) -> None:
    """Сохраняет DataFrame в CSV с кодировкой UTF-8."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False, encoding="utf-8-sig")


def build_annotation_table(
    files: list[Path],
    project_dir: Path,
    class_getter: Callable[[Path], str],
) -> pd.DataFrame:
    """Создаёт CSV-аннотацию из списка файлов."""
    rows = []
    for path in files:
        rows.append(
            {
                "absolute_path": str(path.resolve()),
                "relative_path": _normalise_relative_path(path, project_dir),
                "output_class": class_getter(path),
            }
        )

    return pd.DataFrame(
        rows,
        columns=["absolute_path", "relative_path", "output_class"],
    )


def copy_with_class_names(
    source_dataset: Path,
    output_dir: Path,
    project_dir: Path,
    annotation_path: Path,
) -> pd.DataFrame:
    """
    Копирует датасет в плоскую папку и добавляет имя класса к имени файла.

    Пример: dataset/cat/0000.jpg -> output_dir/cat_0000.jpg
    """
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for source_path in get_dataset_files(source_dataset):
        class_name = get_class_from_path(source_path, source_dataset)
        target_path = output_dir / f"{class_name}_{source_path.name}"
        shutil.copy2(source_path, target_path)
        rows.append(
            {
                "absolute_path": str(target_path.resolve()),
                "relative_path": _normalise_relative_path(
                    target_path, project_dir
                ),
                "output_class": class_name,
            }
        )

    dataframe = pd.DataFrame(
        rows,
        columns=["absolute_path", "relative_path", "output_class"],
    )
    save_dataframe(dataframe, annotation_path)
    return dataframe


def copy_with_random_names(
    source_dataset: Path,
    output_dir: Path,
    project_dir: Path,
    annotation_path: Path,
) -> pd.DataFrame:
    """Копирует файлы с уникальными случайными номерами от 0 до 10000."""
    files = get_dataset_files(source_dataset)
    available_numbers = RANDOM_NUMBER_MAX - RANDOM_NUMBER_MIN + 1
    if len(files) > available_numbers:
        raise ValueError(
            "Количество изображений превышает размер диапазона "
            "случайных номеров 0..10000."
        )

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    random_numbers = random.sample(
        range(RANDOM_NUMBER_MIN, RANDOM_NUMBER_MAX + 1),
        len(files),
    )

    rows = []
    for source_path, number in zip(files, random_numbers):
        class_name = get_class_from_path(source_path, source_dataset)
        target_path = output_dir / f"{number}.jpg"
        shutil.copy2(source_path, target_path)
        rows.append(
            {
                "absolute_path": str(target_path.resolve()),
                "relative_path": _normalise_relative_path(
                    target_path, project_dir
                ),
                "output_class": class_name,
            }
        )

    dataframe = pd.DataFrame(
        rows,
        columns=["absolute_path", "relative_path", "output_class"],
    )
    save_dataframe(dataframe, annotation_path)
    return dataframe


def _create_class_iterator(
    class_label: str,
    dataset_dir: Path,
) -> Iterator[Path]:
    """Создаёт итератор по изображениям одного класса."""
    class_dir = dataset_dir / class_label
    if not class_dir.exists():
        raise ValueError(f"Класс не найден: {class_label}")

    files = [
        path
        for path in class_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return iter(sorted(files))


def reset_instance_iterators() -> None:
    """Сбрасывает состояние функции get_next_instance."""
    _ITERATORS.clear()


def get_next_instance(
    class_label: str,
    dataset_dir: Path,
) -> Path | None:
    """
    Возвращает следующий путь к экземпляру указанного класса.

    Один и тот же экземпляр не возвращается повторно. После окончания
    последовательности функция возвращает None.
    """
    if class_label not in _ITERATORS:
        _ITERATORS[class_label] = _create_class_iterator(
            class_label, dataset_dir
        )
    return next(_ITERATORS[class_label], None)


class ClassIterator:
    """Итератор по изображениям одного класса."""

    def __init__(self, class_label: str, dataset_dir: Path) -> None:
        """Инициализирует итератор для указанного класса."""
        self.class_label = class_label
        self.dataset_dir = dataset_dir
        self._iterator = _create_class_iterator(class_label, dataset_dir)

    def __iter__(self) -> "ClassIterator":
        """Возвращает сам объект итератора."""
        return self

    def __next__(self) -> Path:
        """Возвращает следующий путь или завершает итерацию."""
        return next(self._iterator)


class DatasetIterator:
    """Итератор по всему датасету с сохранением метки класса."""

    def __init__(self, dataset_dir: Path) -> None:
        """Создаёт итератор по всем изображениям датасета."""
        files = get_dataset_files(dataset_dir)
        self._files = iter(
            (get_class_from_path(path, dataset_dir), path) for path in files
        )

    def __iter__(self) -> "DatasetIterator":
        """Возвращает сам объект итератора."""
        return self

    def __next__(self) -> tuple[str, Path]:
        """Возвращает пару (класс, путь) для следующего экземпляра."""
        return next(self._files)

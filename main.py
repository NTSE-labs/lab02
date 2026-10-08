"""
Точка входа лабораторной работы №2.

Исходный датасет берётся напрямую из соседнего проекта lab01.
"""

from pathlib import Path

from dataset_tools import (
    build_annotation_table,
    build_source_files_table,
    copy_with_class_names,
    copy_with_random_names,
    get_class_from_path,
    get_dataset_files,
)

PROJECT_DIR = Path(__file__).resolve().parent
LAB01_DIR = PROJECT_DIR.parent / "lab01"

SOURCE_DATASET_DIR = LAB01_DIR / "dataset"
SOURCE_MANIFEST_PATH = LAB01_DIR / "manifest.jsonl"

ANNOTATIONS_DIR = PROJECT_DIR / "annotations"
OUTPUT_DIR = PROJECT_DIR / "output"

SOURCE_FILES_CSV = ANNOTATIONS_DIR / "source_files.csv"
SOURCE_ANNOTATION_CSV = ANNOTATIONS_DIR / "annotations.csv"
CLASS_NAMED_ANNOTATION_CSV = (
    ANNOTATIONS_DIR / "class_named_annotations.csv"
)
RANDOM_ANNOTATION_CSV = ANNOTATIONS_DIR / "random_annotations.csv"

CLASS_NAMED_DIR = OUTPUT_DIR / "class_named_dataset"
RANDOM_DIR = OUTPUT_DIR / "random_dataset"


def create_source_csv() -> None:
    """Формирует CSV со списком исходных файлов, датами и ссылками."""
    dataframe = build_source_files_table(
        SOURCE_DATASET_DIR,
        PROJECT_DIR,
        SOURCE_MANIFEST_PATH,
    )
    dataframe.to_csv(
        SOURCE_FILES_CSV,
        index=False,
        encoding="utf-8-sig",
    )
    print(f"Создан {SOURCE_FILES_CSV}")
    print(f"Количество записей: {len(dataframe)}")


def create_source_annotation() -> None:
    """Формирует аннотацию исходного датасета."""
    files = get_dataset_files(SOURCE_DATASET_DIR)
    dataframe = build_annotation_table(
        files,
        PROJECT_DIR,
        lambda path: get_class_from_path(path, SOURCE_DATASET_DIR),
    )
    dataframe.to_csv(
        SOURCE_ANNOTATION_CSV,
        index=False,
        encoding="utf-8-sig",
    )
    print(f"Создан {SOURCE_ANNOTATION_CSV}")
    print(f"Количество записей: {len(dataframe)}")


def create_class_named_copy() -> None:
    """Создаёт копию с именами вида class_0000.jpg."""
    dataframe = copy_with_class_names(
        SOURCE_DATASET_DIR,
        CLASS_NAMED_DIR,
        PROJECT_DIR,
        CLASS_NAMED_ANNOTATION_CSV,
    )
    print(f"Создана папка {CLASS_NAMED_DIR}")
    print(f"Скопировано файлов: {len(dataframe)}")


def create_random_copy() -> None:
    """Создаёт копию с уникальными случайными именами 0..10000."""
    dataframe = copy_with_random_names(
        SOURCE_DATASET_DIR,
        RANDOM_DIR,
        PROJECT_DIR,
        RANDOM_ANNOTATION_CSV,
    )
    print(f"Создана папка {RANDOM_DIR}")
    print(f"Скопировано файлов: {len(dataframe)}")


def main() -> None:
    """Запускает все этапы лабораторной работы."""
    if not SOURCE_DATASET_DIR.exists():
        raise FileNotFoundError(
            "Не найден dataset лабораторной работы 1. "
            f"Ожидался путь: {SOURCE_DATASET_DIR}"
        )

    ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    create_source_csv()
    create_source_annotation()
    create_class_named_copy()
    create_random_copy()


if __name__ == "__main__":
    main()

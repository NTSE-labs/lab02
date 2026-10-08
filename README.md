# Лабораторная работа 2

## Цель

Преобразовать решение лабораторной работы 1 в модульную структуру и
научиться работать с датасетом средствами Python и `pandas`.

Исходный датасет **не копируется** из `lab01` в `lab02`. Скрипт использует исходный датасет из `lab01`

Производные копии и CSV создаются уже внутри `lab02`.

## Реализованные пункты

| Пункт | Реализация |
|---|---|
| Шаг 0 | `annotations/source_files.csv` со списком файлов, датой ISO 8601 и ссылкой |
| 1 | `annotations/annotations.csv`: абсолютный путь, относительный путь, класс |
| 2 | `output/class_named_dataset/`, например `cat_0000.jpg` |
| 3 | `output/random_dataset/`, уникальные номера в диапазоне 0..10000 |
| 4 | `get_next_instance()` |
| 5 | `ClassIterator` и `DatasetIterator` |

## Структура проекта

```text
lab02/
├── main.py
├── dataset_tools.py
├── notebook.ipynb
├── requirements.txt
├── README.md
├── annotations/
│   ├── source_files.csv
│   ├── annotations.csv
│   ├── class_named_annotations.csv
│   └── random_annotations.csv
└── output/
    ├── class_named_dataset/
    └── random_dataset/
```

## Запуск

Из каталога `lab02`:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

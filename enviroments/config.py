import pandas as pd

BASE_BENCH_PATH = "/home/piawsa6000/nas192/videos/huggingface_benchmarks_dataset/Leaderboard_bench"

EXCLUDE_DIRS = {"@eaDir", 'temp'}

TYPES = [
    "markdown",
    "markdown",
    "number",
    "number",
    "number",
    "number",
    "number",
    "number",
    "number",
    "str",
    "str",
    "str",
    "str",
    "bool",
    "str",
    "number",
    "number",
    "bool",
    "str",
    "bool",
    "bool",
    "str",
]

ON_LOAD_COLUMNS = [
    "TASK",
    "Model",
    "PIA"            # 모델 이름
]

OFF_LOAD_COLUMNS = ["Model link", "PIA", "PIA * 100" , "Model name" ]

HIDE_COLUMNS = ["PIA * 100"]

FILTER_COLUMNS = ["T"]

NUMERIC_COLUMNS = ["PIA"]

NUMERIC_INTERVALS = {
    "?": pd.Interval(-1, 0, closed="right"),
    "~1.5": pd.Interval(0, 2, closed="right"),
    "~3": pd.Interval(2, 4, closed="right"),
    "~7": pd.Interval(4, 9, closed="right"),
    "~13": pd.Interval(9, 20, closed="right"),
    "~35": pd.Interval(20, 45, closed="right"),
    "~60": pd.Interval(45, 70, closed="right"),
    "70+": pd.Interval(70, 10000, closed="right"),
}
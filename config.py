import pandas as pd

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
    "Model",            # 모델 이름
    "Average F1",       # 평균 F1 Score
    "군중밀집",          # 특정 벤치마크 성능
    "배회",              # 특정 벤치마크 성능
    "쓰러짐",            # 특정 벤치마크 성능
    "화재"              # 특정 벤치마크 성능
]

OFF_LOAD_COLUMNS = [ "Model", "TASK"]


FILTER_COLUMNS = ["T",
                  "Precision",
                  "Model Size"]


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
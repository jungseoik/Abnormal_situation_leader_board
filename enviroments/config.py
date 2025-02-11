BASE_BENCH_PATH = "/home/piawsa6000/nas192/videos/huggingface_benchmarks_dataset/Leaderboard_bench"
EXCLUDE_DIRS = {"@eaDir", 'temp'}
ALL_METRICS = ['accuracy', 'precision', 'recall', 'specificity', 'f1', 'balanced_accuracy', 'g_mean', 'mcc', 'npv', 'far']
DATA_OPTIONS = ["video_duration", "duration_seconds", "total_frames", "file_size_mb", "aspect_ratio", "fps", "file_format"]

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
    "PIA"           
]

OFF_LOAD_COLUMNS = ["Model link", "PIA", "PIA * 100" , "Model name" ]

HIDE_COLUMNS = ["PIA * 100"]

FILTER_COLUMNS = ["T"]

NUMERIC_COLUMNS = ["PIA"]

import sys
# print(sys.path)
import os
# print(os.path.exists("/home/jungseoik/data/Abnormal_situation_leader_board/DevMACS-AI-solution-devmacs/DevMACS-AI-solution-devmacs-core/devmacs_core/utils/common/cal.py"))
# sys.pat.append("/home/jungseoik/data/Abnormal_situation_leader_board/DevMACS-AI-solution-devmacs/DevMACS-AI-solution-devmacs-core")
from sheet_manager.sheet_crud.sheet_crud import SheetManager
from pia_bench.pipe_line.piepline import PipeLineBenchMark
from sheet_manager.sheet_monitor.sheet_sync import SheetMonitor, MainLoop
import time

def my_custom_function(huggingface_id, benchmark_name, prompt_cfg_name):
    piabenchmark = PipeLineBenchMark(huggingface_id, benchmark_name, prompt_cfg_name)
    piabenchmark.bench_start()

# Initialize components
sheet_manager = SheetManager()
monitor = SheetMonitor(sheet_manager, check_interval=10.0)
main_loop = MainLoop(sheet_manager, monitor, callback_function=my_custom_function)

try:
    main_loop.start()
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    main_loop.stop()
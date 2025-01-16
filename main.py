
import sys
import os
from sheet_manager.sheet_crud.sheet_crud import SheetManager
from sheet_manager.sheet_monitor.sheet_sync import SheetMonitor, MainLoop
import time
from pia_bench.pipe_line.piepline import BenchmarkPipeline, PipelineConfig

def calculate_total_accuracy(metrics: dict) -> float:
    overall_metrics = metrics.get("overall_metrics", {})
    total_accuracy = 0
    total_count = 0
    for event_type, values in overall_metrics.items():
        if "accuracy" in values:
            total_accuracy += values["accuracy"]
            total_count += 1
            
    if total_count == 0:
        raise ValueError("No accuracy values found in the provided metrics dictionary.")

    return total_accuracy / total_count

def my_custom_function(huggingface_id, benchmark_name, prompt_cfg_name):
    model_name = huggingface_id.split("/")[-1]
    config = PipelineConfig(
        model_name=model_name,
        benchmark_name=benchmark_name,
        cfg_target_path=f"/home/jungseoik/data/Abnormal_situation_leader_board/assets/PIA/CFG/{prompt_cfg_name}.json",
        base_path="assets"
)
    pipeline = BenchmarkPipeline(config)
    pipeline.run()
    result = pipeline.bench_result_dict
    value = calculate_total_accuracy(result)
    print("---"*50)
    sheet = SheetManager()
    sheet.change_worksheet("model")
    sheet.update_cell_by_condition(condition_column="Model name",
                                    condition_value=model_name ,
                                    target_column=benchmark_name,
                                    target_value=value)
    print(f"\n파이프라인 실행 결과:")

sheet_manager = SheetManager()
monitor = SheetMonitor(sheet_manager, check_interval=10.0)
main_loop = MainLoop(sheet_manager, monitor, callback_function=my_custom_function)

try:
    main_loop.start()
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    main_loop.stop()
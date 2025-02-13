from sheet_manager.sheet_crud.sheet_crud import SheetManager
from sheet_manager.sheet_monitor.sheet_sync import SheetMonitor, MainLoop
import time
from pia_bench.pipe_line.piepline import BenchmarkPipeline, PipelineConfig
from sheet_manager.sheet_convert.json2sheet import update_benchmark_json
import os
from enviroments.config import BASE_BENCH_PATH
from utils.calcul import calculate_total_accuracy

def callback_custom_funciton(huggingface_id, benchmark_name, prompt_cfg_name):
    """
    벤치마크 파이프라인을 실행하고 결과를 시트에 업데이트하는 콜백 함수입니다.

    Args:
        huggingface_id (str): Hugging Face 모델 ID
        benchmark_name (str): 벤치마크 이름
        prompt_cfg_name (str): 프롬프트 설정 파일 이름

    """
    model_name = huggingface_id.split("/")[-1]
    config = PipelineConfig(
        model_name=model_name,
        benchmark_name=benchmark_name,
        cfg_target_path=f"{BASE_BENCH_PATH}/{benchmark_name}/CFG/{prompt_cfg_name}.json",
        base_path=BASE_BENCH_PATH
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
    
    update_benchmark_json(
    model_name = model_name, 
    benchmark_data = result, 
    target_column = benchmark_name  # 타겟 칼럼 파라미터 추가
)
    
    print(f"\n파이프라인 실행 결과:")

if __name__ == "__main__":
    sheet_manager = SheetManager()
    monitor = SheetMonitor(sheet_manager, check_interval=15.0)
    main_loop = MainLoop(sheet_manager, monitor, callback_function=callback_custom_funciton)

    try:
        main_loop.start()
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        main_loop.stop()
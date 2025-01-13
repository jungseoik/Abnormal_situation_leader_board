from pia_bench.checker.bench_checker import BenchChecker
from pia_bench.checker.sheet_checker import SheetChecker ,get_model_info, process_benchmarks, process_model_benchmarks
from pia_bench.event_alarm import EventDetector
from pia_bench.metric import MetricsEvaluator
from sheet_manager.sheet_crud.sheet_crud import SheetManager
from pia_bench.bench import PiaBenchMark
from dotenv import load_dotenv
from typing import Optional, List , Dict
from pia_bench.bench import PiaBenchMark
import os
load_dotenv()
import numpy as np
from typing import Dict, Tuple

def calculate_overall_metrics(result: Dict) -> Tuple[float, float, float, float, float]:
    """
    전체 f1, accuracy, precision, recall, specificity의 평균값을 계산하여 반환.

    :param result: 평가 함수의 반환값 (카테고리별 메트릭 데이터)
    :return: (f1 평균, accuracy 평균, precision 평균, recall 평균, specificity 평균)
    """
    # 각 메트릭의 값을 저장할 리스트
    f1_values, accuracy_values, precision_values, recall_values, specificity_values = [], [], [], [], []

    # 카테고리별 메트릭 데이터 순회
    for category, metrics in result.items():
        for key, value in metrics.items():
            if key.endswith('_f1'):
                f1_values.append(value)
            elif key.endswith('_accuracy'):
                accuracy_values.append(value)
            elif key.endswith('_precision'):
                precision_values.append(value)
            elif key.endswith('_recall'):
                recall_values.append(value)
            elif key.endswith('_specificity'):
                specificity_values.append(value)

    # 각 메트릭의 평균값 계산
    f1_mean = np.mean(f1_values)
    accuracy_mean = np.mean(accuracy_values)
    precision_mean = np.mean(precision_values)
    recall_mean = np.mean(recall_values)
    specificity_mean = np.mean(specificity_values)

    return f1_mean, accuracy_mean, precision_mean, recall_mean, specificity_mean

class PipeLineBenchMark:
    def __init__(self , huggingface_id, benchmark_name, prompt_cfg_name):
        self.huggingface_id = huggingface_id
        self.benchmark_name = benchmark_name
        self.prompt_cfg_name = prompt_cfg_name
        self.model_name = self.huggingface_id.split("/")[-1]

        self.access_token = os.getenv("ACCESS_TOKEN")
        self.cfg_target_path= "topk.json"
        self.benchmark_path = "assets/PIA"

        self.sheet_manager = SheetManager()
        self.bench_checker = BenchChecker("assets")
        self.sheet_checker = SheetChecker(self.sheet_manager)
        self.evnet_detector = EventDetector(config_path=self.cfg_target_path, 
                                            model_name=self.model_name, 
                                            token=self.access_token)
        self.metric_evaluator = None
        self.pia_benchmark = PiaBenchMark(self.benchmark_path , 
                                           model_name= self.model_name,
                                           cfg_target_path=self.cfg_target_path,
                                           token=self.access_token)
        self.eval_result = None

    def _process_benchmarks(self,
        model_name: str,
        empty_benchmarks: List[str],
        cfg_prompt: str
    ) -> Dict[str, str]:
        """
        Measure benchmark scores for given model with specific configuration.
        
        Args:
            model_name: Name of the model to evaluate
            empty_benchmarks: List of benchmarks to measure
            cfg_prompt: Prompt configuration for evaluation
            
        Returns:
            Dict[str, str]: Dictionary mapping benchmark names to their scores
        """
        status = self.bench_checker.check_benchmark(
            benchmark_name=self.benchmark_name,
            model_name=self.model_name,
            cfg_prompt=self.prompt_cfg_name
        )
        execution_path = self.bench_checker.determine_execution_path(status)

        result = {}
        for benchmark in empty_benchmarks:
            # score = measure_benchmark(model_name, benchmark, cfg_prompt)
            if execution_path:
                self._do_bench(False)
                self.eval_result = self._after_bench()
                score = calculate_overall_metrics(self.eval_result)
            else:
                self._do_bench(True)
                self.eval_result = self._after_bench()
                score = calculate_overall_metrics(self.eval_result)

            result[benchmark] = str(score[0])
        return result

    def bench_start(self):
        process_model_benchmarks(
            self.model_name,
            self.sheet_checker,
            get_model_info,
            self._process_benchmarks,
            [self.benchmark_name],
            self.prompt_cfg_name
        )


    def _do_bench(self, extract_vector_excute = False):
        self.pia_benchmark.preprocess_structure()
        if extract_vector_excute:
            self.pia_benchmark.extract_visual_vector()
        
        self.evnet_detector.process_and_save_predictions(
            self.pia_benchmark.vector_video_path, 
            self.pia_benchmark.dataset_path, 
            self.pia_benchmark.alram_path)

    def _after_bench(self):
        self.metric_evaluator = MetricsEvaluator(
            pred_dir=self.pia_benchmark.alram_path, 
            label_dir=self.pia_benchmark.dataset_path, 
            save_dir=self.pia_benchmark.metric_path)
        return self.metric_evaluator.evaluate()
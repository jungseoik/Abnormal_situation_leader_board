from typing import List, Dict, Optional, Set, Tuple
import logging
import gspread
from dotenv import load_dotenv
from typing import Optional, List
from sheet_manager.sheet_crud.sheet_crud import SheetManager

load_dotenv()

class SheetChecker:
    def __init__(self, sheet_manager):
        """SheetChecker 초기화"""
        self.sheet_manager = sheet_manager
        self.bench_sheet_manager = None
        self.logger = logging.getLogger(__name__)
        self._init_bench_sheet()

    def _init_bench_sheet(self):
        """model 시트용 시트 매니저 초기화"""
        self.bench_sheet_manager = type(self.sheet_manager)(
            spreadsheet_url=self.sheet_manager.spreadsheet_url,
            worksheet_name="model",
            column_name="Model name"
        )

    def add_benchmark_column(self, column_name: str):
        """새로운 벤치마크 컬럼 추가"""
        try:
            headers = self.bench_sheet_manager.get_available_columns()
            
            if column_name in headers:
                return
            
            new_col_index = len(headers) + 1
            cell = gspread.utils.rowcol_to_a1(1, new_col_index)
            self.bench_sheet_manager.sheet.update(cell, [[column_name]])
            self.logger.info(f"새로운 벤치마크 컬럼 추가됨: {column_name}")
            
            self.bench_sheet_manager._connect_to_sheet(validate_column=False)
            
        except Exception as e:
            self.logger.error(f"벤치마크 컬럼 {column_name} 추가 중 오류 발생: {str(e)}")
            raise

    def validate_benchmark_columns(self, benchmark_columns: List[str]) -> Tuple[List[str], List[str]]:
        """벤치마크 컬럼 유효성 검사 및 누락된 컬럼 추가"""
        available_columns = self.bench_sheet_manager.get_available_columns()
        valid_columns = []
        invalid_columns = []
        
        for col in benchmark_columns:
            if col in available_columns:
                valid_columns.append(col)
            else:
                try:
                    self.add_benchmark_column(col)
                    valid_columns.append(col)
                    self.logger.info(f"새로운 벤치마크 컬럼 추가됨: {col}")
                except Exception as e:
                    invalid_columns.append(col)
                    self.logger.error(f"벤치마크 컬럼 '{col}' 추가 실패: {str(e)}")
        
        return valid_columns, invalid_columns
    def check_model_and_benchmarks(self, model_name: str, benchmark_name: str) -> Dict[str, str]:
        """
        모델 존재 여부와 단일 벤치마크 상태 확인
        
        Args:
            model_name: 확인할 모델 이름
            benchmark_name: 확인할 벤치마크 이름
            
        Returns:
            Dict with keys:
                'status': 'model_not_found' or 'model_exists'
                'benchmark_status': 'empty', 'filled', or 'invalid'
        """
        result = {
            'status': '',
            'benchmark_status': ''
        }

        # 모델 존재 확인
        exists = self.check_model_exists(model_name)
        if not exists:
            result['status'] = 'model_not_found'
            return result

        result['status'] = 'model_exists'
        
        # 벤치마크 컬럼 유효성 확인
        available_columns = self.bench_sheet_manager.get_available_columns()
        if benchmark_name not in available_columns:
            try:
                self.add_benchmark_column(benchmark_name)
                self.logger.info(f"새로운 벤치마크 컬럼 추가됨: {benchmark_name}")
            except Exception as e:
                self.logger.error(f"벤치마크 컬럼 '{benchmark_name}' 추가 실패: {str(e)}")
                result['benchmark_status'] = 'invalid'
                return result

        # 벤치마크 값 확인
        try:
            self.bench_sheet_manager.change_column("Model name")
            all_values = self.bench_sheet_manager.get_all_values()
            row_index = all_values.index(model_name) + 2

            self.bench_sheet_manager.change_column(benchmark_name)
            value = self.bench_sheet_manager.sheet.cell(row_index, self.bench_sheet_manager.col_index).value
            
            if not value or not value.strip():
                result['benchmark_status'] = 'empty'
            else:
                result['benchmark_status'] = 'filled'
        except Exception as e:
            self.logger.error(f"컬럼 {benchmark_name} 확인 중 오류 발생: {str(e)}")
            result['benchmark_status'] = 'empty'

        return result

    def update_model_info(self, model_name: str, model_info: Dict[str, str]):
        """모델 기본 정보 업데이트"""
        try:
            for column_name, value in model_info.items():
                self.bench_sheet_manager.change_column(column_name)
                self.bench_sheet_manager.push(value)
            self.logger.info(f"새로운 모델 추가 완료: {model_name}")
        except Exception as e:
            self.logger.error(f"모델 정보 업데이트 중 오류 발생: {str(e)}")
            raise

    def update_benchmarks(self, model_name: str, benchmark_values: Dict[str, str]):
        """벤치마크 값 업데이트"""
        try:
            self.bench_sheet_manager.change_column("Model name")
            all_values = self.bench_sheet_manager.get_all_values()
            row_index = all_values.index(model_name) + 2

            for column, value in benchmark_values.items():
                self.bench_sheet_manager.change_column(column)
                self.bench_sheet_manager.sheet.update_cell(row_index, self.bench_sheet_manager.col_index, value)
                self.logger.info(f"벤치마크 {column} 업데이트 완료 (모델: {model_name})")

        except Exception as e:
            self.logger.error(f"벤치마크 업데이트 중 오류 발생: {str(e)}")
            raise

    def check_model_exists(self, model_name: str) -> bool:
        """모델 존재 여부 확인"""
        try:
            self.bench_sheet_manager.change_column("Model name")
            values = self.bench_sheet_manager.get_all_values()
            return model_name in values
        except Exception as e:
            self.logger.error(f"모델 존재 여부 확인 중 오류 발생: {str(e)}")
            return False

    def process_model_benchmarks(
        self,
        model_name: str,
        benchmark_name: str,
        cfg_prompt: str,
        processor_func: callable = None
    ) -> None:
        """
        단일 모델 벤치마크 처리 워크플로우 실행
        
        Args:
            model_name: 처리할 모델 이름
            benchmark_name: 처리할 벤치마크 이름
            cfg_prompt: 설정 프롬프트
            processor_func: 벤치마크 처리를 위한 콜백 함수 (기본값: None)
        """
        try:
            # 벤치마크 상태 확인
            check_result = self.check_model_and_benchmarks(model_name, benchmark_name)
            
            # 모델이 없으면 추가
            if check_result['status'] == 'model_not_found':
                model_info = {
                    "Model name": model_name,
                    "Model link": f"https://huggingface.co/PIA-SPACE-LAB/{model_name}",
                    "Model": f'<a target="_blank" href="https://huggingface.co/PIA-SPACE-LAB/{model_name}" style="color: var(--link-text-color); text-decoration: underline;text-decoration-style: dotted;">{model_name}</a>'
                }
                self.update_model_info(model_name, model_info)
                self.logger.info(f"새로운 모델 추가됨: {model_name}")
                # 모델 추가 후 벤치마크 상태 재확인
                check_result = self.check_model_and_benchmarks(model_name, benchmark_name)

            if check_result['benchmark_status'] == 'invalid':
                self.logger.warning(f"유효하지 않은 벤치마크: {benchmark_name}")
                return
                
            if check_result['benchmark_status'] == 'filled':
                self.logger.info(f"이미 측정된 벤치마크: {benchmark_name}")
                return

            if check_result['benchmark_status'] == 'empty':
                self.logger.info(f"벤치마크 처리 중: {benchmark_name}")
                
                if processor_func is None:
                    def default_processor(model_name: str, benchmark_name: str, cfg_prompt: str) -> str:
                        if benchmark_name == "COCO":
                            return "0.5"
                        elif benchmark_name == "ImageNet":
                            return "15.0"
                        return "0.0"
                    processor_func = default_processor
                
                # 벤치마크 값 측정 및 업데이트
                score = processor_func(model_name, benchmark_name, cfg_prompt)
                self.update_benchmarks(model_name, {benchmark_name: score})
                self.logger.info(f"벤치마크 {benchmark_name} 측정 완료: {score}")
            
        except Exception as e:
            self.logger.error(f"모델 {model_name} 처리 중 오류 발생: {str(e)}")
            raise

# 사용 예시
if __name__ == "__main__":
    sheet_manager = SheetManager()
    checker = SheetChecker(sheet_manager)
    
    # 기본 프로세서로 벤치마크 처리
    checker.process_model_benchmarks(
        model_name="test-model",
        benchmark_name="COCO",
        cfg_prompt="cfg_prompt_value"
    )
    
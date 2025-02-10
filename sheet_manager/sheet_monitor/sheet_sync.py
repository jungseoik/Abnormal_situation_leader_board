import threading
import time
from typing import Optional, Callable, Tuple, Union, Any
import logging

class SheetMonitor:
    """
    구글 시트의 변경사항을 지속적으로 모니터링하는 클래스입니다.
    
    스레드 기반으로 동작하며, 시트의 데이터 변경을 감지하고 이벤트를 통해 
    상태를 관리합니다. 모니터링의 일시 중지/재개 및 완전한 중단이 가능합니다.

    Attributes:
        sheet_manager: 구글 시트 작업을 처리하는 매니저 인스턴스
        check_interval (float): 시트 확인 간격 (초)
        monitor_thread (threading.Thread): 모니터링 작업을 수행하는 스레드
        is_running (threading.Event): 모니터링 스레드의 실행 상태
        pause_monitoring (threading.Event): 모니터링 일시 중지 상태
        monitor_paused (threading.Event): 모니터링이 일시 중지되었음을 나타내는 상태
        has_data (threading.Event): 시트에 데이터가 있는지 여부
        logger (logging.Logger): 로깅을 위한 로거 인스턴스

    Example:
        >>> monitor = SheetMonitor(sheet_manager, check_interval=1.0)
        >>> monitor.start_monitoring()
        >>> # ... 작업 수행 ...
        >>> monitor.pause()  # 모니터링 일시 중지
        >>> monitor.resume()  # 모니터링 재개
        >>> monitor.stop_monitoring()  # 모니터링 완전 중단
    """

    def __init__(self, sheet_manager: Any, check_interval: float = 1.0):
        """
        SheetMonitor 인스턴스를 초기화합니다.

        Args:
            sheet_manager: 구글 시트 작업을 처리하는 매니저 인스턴스
            check_interval (float): 시트 확인 간격 (초 단위). 기본값은 1.0초

        Note:
            check_interval이 너무 작으면 구글 시트 API 할당량을 빨리 소진할 수 있으므로 주의가 필요합니다.
        """
        self.sheet_manager = sheet_manager
        self.check_interval = check_interval
        
        self.monitor_thread = None
        self.is_running = threading.Event()
        self.pause_monitoring = threading.Event()
        self.monitor_paused = threading.Event()
        self.has_data = threading.Event()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start_monitoring(self) -> None:
        """
        모니터링 스레드를 시작합니다.
        
        이미 모니터링이 실행 중인 경우 경고 메시지를 출력하고 함수를 종료합니다.
        
        Note:
            스레드는 데몬 스레드로 생성되어 메인 프로그램 종료 시 자동으로 종료됩니다.
        """
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            self.logger.warning("Monitoring thread is already running")
            return

        self.is_running.set()
        self.pause_monitoring.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("Started monitoring thread")

    def stop_monitoring(self) -> None:
        """
        모니터링 스레드를 중지합니다.
        
        현재 실행 중인 스레드가 완전히 종료될 때까지 대기합니다.
        """
        self.is_running.clear()
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("Stopped monitoring thread")

    def pause(self) -> None:
        """
        모니터링을 일시 중지합니다.
        
        모니터링이 실제로 일시 중지 상태가 될 때까지 대기합니다.
        """
        self.pause_monitoring.set()
        self.monitor_paused.wait()
        self.logger.info("Monitoring paused")

    def resume(self) -> None:
        """
        일시 중지된 모니터링을 재개합니다.
        
        재개 즉시 시트의 데이터를 확인하고, 데이터가 있는 경우 has_data 이벤트를 설정합니다.
        """
        self.pause_monitoring.clear()
        self.monitor_paused.clear()
        self.logger.info("Monitoring resumed, checking for new data...")
        values = self.sheet_manager.get_all_values()
        if values:
            self.has_data.set()
            self.logger.info(f"Found data after resume: {values}")

    def _monitor_loop(self) -> None:
        """
        시트 데이터를 주기적으로 확인하는 메인 모니터링 루프입니다.
        
        지정된 check_interval 간격으로 시트의 데이터를 확인하고,
        데이터 존재 여부에 따라 has_data 이벤트를 설정/해제합니다.
        
        예외가 발생하면 로그를 기록하고 다음 주기에 다시 시도합니다.
        """
        while self.is_running.is_set():
            if self.pause_monitoring.is_set():
                self.monitor_paused.set()
                self.pause_monitoring.wait()
                self.monitor_paused.clear()

            try:
                values = self.sheet_manager.get_all_values()
                self.logger.info(f"Monitoring: Current column={self.sheet_manager.column_name}, "
                            f"Values found={len(values)}, "
                            f"Has data={self.has_data.is_set()}")
                
                if values:
                    self.has_data.set()
                    self.logger.info(f"Data detected: {values}")
                else:
                    self.has_data.clear()
                    self.logger.info("No data in sheet, waiting...")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(self.check_interval)


class MainLoop:
    """
    SheetMonitor와 연동하여 시트 데이터를 처리하는 메인 루프를 관리하는 클래스입니다.
    
    시트에서 데이터가 감지되면 지정된 콜백 함수를 호출하여 처리합니다.
    데이터 처리 중에는 모니터링을 일시 중지하여 데이터 일관성을 유지합니다.

    Attributes:
        sheet_manager: 구글 시트 작업을 처리하는 매니저 인스턴스
        monitor (SheetMonitor): 시트 모니터링을 담당하는 인스턴스
        callback (Callable): 데이터 처리를 위한 콜백 함수
        is_running (threading.Event): 메인 루프의 실행 상태
        logger (logging.Logger): 로깅을 위한 로거 인스턴스

    Example:
        >>> def process_data(model_id, benchmark_name, cfg_name):
        ...     print(f"Processing: {model_id}, {benchmark_name}, {cfg_name}")
        >>> 
        >>> main_loop = MainLoop(sheet_manager, monitor, callback_function=process_data)
        >>> main_loop.start()
        >>> # ... 작업 수행 ...
        >>> main_loop.stop()
    """

    def __init__(self, sheet_manager: Any, sheet_monitor: SheetMonitor, 
                 callback_function: Optional[Callable[[str, str, str], None]] = None):
        """
        MainLoop 인스턴스를 초기화합니다.

        Args:
            sheet_manager: 구글 시트 작업을 처리하는 매니저 인스턴스
            sheet_monitor (SheetMonitor): 시트 모니터링을 담당하는 인스턴스
            callback_function (Optional[Callable]): 데이터 처리를 위한 콜백 함수.
                함수는 (model_id: str, benchmark_name: str, prompt_cfg_name: str) 
                형태의 파라미터를 받아야 합니다.
        """
        self.sheet_manager = sheet_manager
        self.monitor = sheet_monitor
        self.callback = callback_function
        self.is_running = threading.Event()
        self.logger = logging.getLogger(__name__)

    def start(self) -> None:
        """
        메인 처리 루프를 시작합니다.
        
        모니터링을 시작하고 메인 루프를 실행합니다.
        """
        self.is_running.set()
        self.monitor.start_monitoring()
        self._main_loop()

    def stop(self) -> None:
        """
        메인 처리 루프를 중지합니다.
        
        모니터링도 함께 중지됩니다.
        """
        self.is_running.clear()
        self.monitor.stop_monitoring()

    def process_new_value(self) -> Optional[Tuple[str, str, str]]:
        """
        시트에서 새로운 데이터를 처리합니다.
        
        여러 열에서 순차적으로 데이터를 가져와서 처리하고,
        콜백 함수가 지정되어 있다면 이를 호출합니다.

        Returns:
            Optional[Tuple[str, str, str]]: 
                처리된 (model_id, benchmark_name, prompt_cfg_name) 튜플
                실패 시 None 반환

        Note:
            처리 중 예외가 발생하면 원래 열로 돌아가려고 시도합니다.
        """
        try:
            original_column = self.sheet_manager.column_name
            
            model_id = self.sheet_manager.pop()
            
            if model_id:
                self.sheet_manager.change_column("benchmark_name")
                benchmark_name = self.sheet_manager.pop()
                
                self.sheet_manager.change_column("prompt_cfg_name")
                prompt_cfg_name = self.sheet_manager.pop()
                
                self.sheet_manager.change_column(original_column)
                
                self.logger.info(f"Processed values - model_id: {model_id}, "
                            f"benchmark_name: {benchmark_name}, "
                            f"prompt_cfg_name: {prompt_cfg_name}")
                
                if self.callback:
                    self.callback(model_id, benchmark_name, prompt_cfg_name)
                    
                return model_id, benchmark_name, prompt_cfg_name
                
        except Exception as e:
            self.logger.error(f"Error processing values: {str(e)}")
            try:
                self.sheet_manager.change_column(original_column)
            except:
                pass
            return None

    def _main_loop(self) -> None:
        """
        메인 처리 루프를 실행합니다.
        
        시트에 데이터가 있을 때까지 대기하다가, 데이터가 감지되면
        모니터링을 일시 중지하고 데이터를 처리한 후 다시 모니터링을 재개합니다.
        
        모든 데이터가 처리되면 has_data 플래그를 해제합니다.
        """
        while self.is_running.is_set():
            if self.monitor.has_data.wait(timeout=1.0):
                self.monitor.pause()
                
                self.process_new_value()
                
                values = self.sheet_manager.get_all_values()
                self.logger.info(f"After processing: Current column={self.sheet_manager.column_name}, "
                            f"Values remaining={len(values)}")
                
                if not values:
                    self.monitor.has_data.clear()
                    self.logger.info("All data processed, clearing has_data flag")
                else:
                    self.logger.info(f"Remaining data: {values}")
                
                self.monitor.resume()
## TODO
# API 분당 호출 문제로 만약에 참조하다가 실패할 경우 대기했다가 다시 시도하게끔 설계

# Example usage
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from sheet_manager.sheet_crud.sheet_crud import SheetManager
    from pia_bench.pipe_line.piepline import PiaBenchMark
    def my_custom_function(huggingface_id, benchmark_name, prompt_cfg_name):
        piabenchmark = PiaBenchMark(huggingface_id, benchmark_name, prompt_cfg_name)
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
import os
import shutil
from devmacs_core.devmacs_core import DevMACSCore
import json
from typing import Dict, List, Tuple
from pathlib import Path
import pandas as pd

def load_config(config_path: str) -> Dict:
    """JSON 설정 파일을 읽어서 딕셔너리로 반환"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
DATA_SET = "dataset"
CFG = "CFG"
VECTOR = "vector"
TEXT = "text"
VIDEO = "video"
EXECPT = ["@eaDir", "README.md"]
ALRAM = "alarm"
METRIC = "metric"
MSRVTT = "MSRVTT"
MODEL = "models"

class PiaBenchMark:
    def __init__(self, benchmark_path , cfg_target_path : str = None , model_name : str = MSRVTT , token:str =None):
        self.benchmark_path = benchmark_path
        self.token = token
        self.model_name = model_name
        self.devmacs_core = None
        self.cfg_target_path = cfg_target_path
        self.cfg_name = Path(cfg_target_path).stem
        self.cfg_dict = load_config(self.cfg_target_path)

        self.dataset_path = os.path.join(benchmark_path, DATA_SET)
        self.cfg_path = os.path.join(benchmark_path , CFG)

        self.model_path = os.path.join(self.benchmark_path , MODEL)
        self.model_name_path = os.path.join(self.model_path ,self.model_name)
        self.model_name_cfg_path = os.path.join(self.model_name_path , CFG)
        self.model_name_cfg_name_path = os.path.join(self.model_name_cfg_path , self.cfg_name)
        self.alram_path = os.path.join(self.model_name_cfg_name_path , ALRAM)
        self.metric_path = os.path.join(self.model_name_cfg_name_path , METRIC)

        self.vector_path = os.path.join(self.model_name_path , VECTOR)
        self.vector_text_path = os.path.join(self.vector_path , TEXT)
        self.vector_video_path = os.path.join(self.vector_path , VIDEO)

        self.categories = []

    def _create_frame_labels(self, label_data: Dict, total_frames: int) -> pd.DataFrame:
        """프레임 기반의 레이블 데이터프레임 생성"""
        colmuns = ['frame'] + sorted(self.categories)
        df = pd.DataFrame(0, index=range(total_frames), columns=colmuns)
        df['frame'] = range(total_frames)
        
        for clip_info in label_data['clips'].values():
            category = clip_info['category']
            if category in self.categories:  # 해당 카테고리가 목록에 있는 경우만 처리
                start_frame, end_frame = clip_info['timestamp']
                df.loc[start_frame:end_frame, category] = 1
                
        return df

    def preprocess_label_to_csv(self):
        """데이터셋의 모든 JSON 라벨을 프레임 기반 CSV로 변환"""
        json_files = []
        csv_files = []
        for cate in os.listdir(self.dataset_path):
            self.categories.append(cate)

        for category in self.categories:
            category_path = os.path.join(self.dataset_path, category)
            category_jsons = [os.path.join(category, f) for f in os.listdir(category_path) if f.endswith('.json')]
            json_files.extend(category_jsons)
            category_csvs = [os.path.join(category, f) for f in os.listdir(category_path) if f.endswith('.csv')]
            csv_files.extend(category_csvs)

        if not json_files:
            raise ValueError("No JSON files found in any category directory")
        
        if len(json_files) == len(csv_files):
            print("All JSON files have already been processed to CSV. No further processing needed.")
            return

        for json_file in json_files:
            json_path = os.path.join(self.dataset_path, json_file)
            video_name = os.path.splitext(json_file)[0] 
            
            label_info = load_config(json_path)
            video_info = label_info['video_info']
            total_frames = video_info['total_frame']
            
            df = self._create_frame_labels( label_info, total_frames)
            
            output_path = os.path.join(self.dataset_path, f"{video_name}.csv")
            df.to_csv(output_path , index=False)
        print("Complete !")

    def preprocess_structure(self):
        os.makedirs(self.dataset_path, exist_ok=True)
        os.makedirs(self.cfg_path, exist_ok=True)
        os.makedirs(self.vector_text_path, exist_ok=True)
        os.makedirs(self.vector_video_path, exist_ok=True)
        os.makedirs(self.alram_path, exist_ok=True)
        os.makedirs(self.metric_path, exist_ok=True)
        os.makedirs(self.model_name_cfg_name_path , exist_ok=True)

        for item in os.listdir(self.benchmark_path):
            item_path = os.path.join(self.benchmark_path, item)
            
            if item.startswith("@") or item in [METRIC ,"README.md",MODEL,  CFG, DATA_SET, VECTOR, ALRAM] or not os.path.isdir(item_path):
                continue
            target_path = os.path.join(self.dataset_path, item)
            if not os.path.exists(target_path):
                shutil.move(item_path, target_path)
                self.categories.append(item)
        for category in self.categories:
            category_path = os.path.join(self.vector_video_path, category)
            os.makedirs(category_path, exist_ok=True)

        print("Folder preprocessing completed.")
    
    def extract_visual_vector(self):
        self.devmacs_core = DevMACSCore.from_huggingface(token=self.token, repo_id=f"PIA-SPACE-LAB/{self.model_name}")
        self.devmacs_core.save_visual_results(
            vid_dir = self.dataset_path,
            result_dir = self.vector_video_path
        )

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()

    access_token = os.getenv("ACCESS_TOKEN")
    model_name = "T2V_CLIP4CLIP_MSRVTT"

    benchmark_path = "/home/jungseoik/data/Abnormal_situation_leader_board/assets/PIA"
    cfg_target_path= "/home/jungseoik/data/Abnormal_situation_leader_board/assets/PIA/CFG/topk.json"

    pia_benchmark = PiaBenchMark(benchmark_path ,model_name=model_name, cfg_target_path= cfg_target_path , token=access_token )
    pia_benchmark.preprocess_structure()
    pia_benchmark.preprocess_label_to_csv()  
    print("Categories identified:", pia_benchmark.categories)
import os
import shutil
from devmacs_core.devmacs_core import DevMACSCore
import json
from typing import Dict, List, Tuple
from pathlib import Path

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




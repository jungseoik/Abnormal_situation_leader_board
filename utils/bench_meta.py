import os
import cv2
import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt
from utils.except_dir import cust_listdir

def get_video_metadata(video_path, category, benchmark):
    """
    비디오 파일로부터 메타데이터를 추출합니다.
    이 함수는 OpenCV를 사용하여 비디오 파일의 다양한 메타데이터를 추출하고,
    추출된 정보를 딕셔너리 형태로 반환합니다.

    Parameters
    ----------
    video_path : str
        비디오 파일의 전체 경로
    category : str
        비디오가 속한 카테고리명
    benchmark : str
        비디오가 속한 벤치마크명

    Returns
    -------
    Optional[Dict[str, Union[str, float, int]]]
        비디오 메타데이터를 포함하는 딕셔너리. 비디오 파일을 열 수 없는 경우 None 반환.
        딕셔너리는 다음 키들을 포함:
        - video_name (str): 비디오 파일명
        - resolution (str): 해상도 (예: "1920x1080")
        - video_duration (str): 재생 시간 (분:초 형식)
        - category (str): 비디오 카테고리
        - benchmark (str): 벤치마크명
        - duration_seconds (float): 재생 시간(초)
        - total_frames (int): 총 프레임 수
        - file_format (str): 파일 확장자
        - file_size_mb (float): 파일 크기(MB)
        - aspect_ratio (float): 화면 비율
        - fps (float): 초당 프레임 수

    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return None
    # Extract metadata
    video_name = os.path.basename(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    resolution = f"{frame_width}x{frame_height}"
    duration_seconds = frame_count / fps if fps > 0 else 0
    aspect_ratio = round(frame_width / frame_height, 2) if frame_height > 0 else 0
    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
    file_format = os.path.splitext(video_name)[1].lower()
    cap.release()
    
    return {
        "video_name": video_name,
        "resolution": resolution,
        "video_duration": f"{duration_seconds // 60:.0f}:{duration_seconds % 60:.0f}",
        "category": category,
        "benchmark": benchmark,
        "duration_seconds": duration_seconds,
        "total_frames": frame_count,
        "file_format": file_format,
        "file_size_mb": round(file_size, 2),
        "aspect_ratio": aspect_ratio,
        "fps": fps
    }

def process_videos_in_directory(root_dir: str = "root"):
    """
    주어진 루트 디렉토리 내의 모든 비디오 파일들의 메타데이터를 수집하여 DataFrame으로 반환합니다.
    이 함수는 다음과 같은 특정 디렉토리 구조를 전제로 합니다:

    root_dir/
    ├── benchmark_A/
    │   └── dataset/
    │       ├── category1/
    │       │   ├── video1.mp4
    │       │   └── video2.avi
    │       └── category2/
    │           └── video3.mkv
    ├── benchmark_B/
    │   └── dataset/
    │       └── category1/
    │           └── video4.mp4
    
    Parameters
    ----------
    root_dir : str
        비디오 데이터셋이 저장된 최상위 디렉토리 경로
        
    Returns
    -------
    pandas.DataFrame
        다음 컬럼들을 포함하는 DataFrame:
        - video_name: 비디오 파일명
        - resolution: 비디오 해상도 (예: "1920x1080")
        - video_duration: 비디오 길이 (분:초 형식)
        - category: 비디오가 속한 카테고리
        - benchmark: 비디오가 속한 벤치마크
        - duration_seconds: 비디오 길이 (초 단위)
        - total_frames: 총 프레임 수
        - file_format: 파일 확장자
        - file_size_mb: 파일 크기 (MB)
        - aspect_ratio: 화면 비율
        - fps: 초당 프레임 수
        
    Notes
    -----
    1. 디렉토리 구조 요구사항:
        - root_dir 아래에는 여러 벤치마크 폴더들이 있어야 함
        - 각 벤치마크 폴더 안에는 반드시 'dataset' 폴더가 있어야 함 
        - dataset 폴더 안에는 카테고리별 폴더들이 있어야 함
        - 카테고리 폴더 안에 실제 비디오 파일들이 위치
    
    2. 지원하는 비디오 포맷:
        - .mp4
        - .avi
        - .mkv
        - .mov
        - .MOV
    
        
    Examples
    --------
    >>> df = process_videos_in_directory("path/to/dataset")
    >>> print(df.columns)
    Index(['video_name', 'resolution', 'video_duration', 'category', 'benchmark',
           'duration_seconds', 'total_frames', 'file_format', 'file_size_mb',
           'aspect_ratio', 'fps'], dtype='object')
    
    >>> print(df.head())
       video_name resolution video_duration category benchmark  ...
    0  video1.mp4  1920x1080         1:30    cat1    bench_A  ...
    """
    video_metadata_list = []
    
    # 벤치마크 폴더들을 순회
    for benchmark in cust_listdir(root_dir):
        benchmark_path = os.path.join(root_dir, benchmark)
        if not os.path.isdir(benchmark_path):
            continue
        
        # dataset 폴더 경로
        dataset_path = os.path.join(benchmark_path, "dataset")
        if not os.path.isdir(dataset_path):
            continue
            
        # dataset 폴더 안의 카테고리 폴더들을 순회
        for category in cust_listdir(dataset_path):
            category_path = os.path.join(dataset_path, category)
            if not os.path.isdir(category_path):
                continue
                
            # 각 카테고리 폴더 안의 비디오 파일들을 처리
            for file in cust_listdir(category_path):
                file_path = os.path.join(category_path, file)
                
                if file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', 'MOV')):
                    metadata = get_video_metadata(file_path, category, benchmark)
                    if metadata:
                        video_metadata_list.append(metadata)
    # df = pd.DataFrame(video_metadata_list)
    # df.to_csv('sample.csv', index=False)
    return pd.DataFrame(video_metadata_list)


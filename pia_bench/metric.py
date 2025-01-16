import os
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score
from typing import Dict, List
import json

class MetricsEvaluator:
    def __init__(self, pred_dir: str, label_dir: str, save_dir: str):
        """
        Args:
            pred_dir: 예측 csv 파일들이 있는 디렉토리 경로
            label_dir: 정답 csv 파일들이 있는 디렉토리 경로 
            save_dir: 결과를 저장할 디렉토리 경로
        """
        self.pred_dir = pred_dir
        self.label_dir = label_dir
        self.save_dir = save_dir
        
    def evaluate(self) -> Dict:
        """전체 평가 수행"""
        category_metrics = {}  # 카테고리별 평균 성능 저장
        all_metrics = {  # 모든 카테고리 통합 메트릭
            'falldown': {'f1': [], 'accuracy': [], 'precision': [], 'recall': [], 'specificity': []},
            'violence': {'f1': [], 'accuracy': [], 'precision': [], 'recall': [], 'specificity': []},
            'fire': {'f1': [], 'accuracy': [], 'precision': [], 'recall': [], 'specificity': []}
        }
        
        for category in os.listdir(self.pred_dir):
            if not os.path.isdir(os.path.join(self.pred_dir, category)):
                continue
                
            pred_category_path = os.path.join(self.pred_dir, category)
            label_category_path = os.path.join(self.label_dir, category)
            save_category_path = os.path.join(self.save_dir, category)
            os.makedirs(save_category_path, exist_ok=True)
            
            # 결과 저장을 위한 데이터프레임 생성
            metrics_df = self._evaluate_category(category, pred_category_path, label_category_path)
            metrics_df.to_csv(os.path.join(save_category_path, f"{category}_metrics.csv"), index=False)
            
            # 카테고리별 평균 성능 저장
            category_metrics[category] = metrics_df.iloc[-1].to_dict()  # 마지막 row(평균)
            
            # 전체 평균을 위한 메트릭 수집
            # for col in metrics_df.columns:
            #     if col != 'video_name':
            #         event_type, metric_type = col.split('_')
            #         all_metrics[event_type][metric_type].append(category_metrics[category][col])

            for col in metrics_df.columns:
                if col != 'video_name':
                    try:
                        # 첫 번째 언더스코어를 기준으로 이벤트 타입과 메트릭 타입 분리
                        parts = col.split('_', 1)  # maxsplit=1로 첫 번째 언더스코어에서만 분리
                        if len(parts) == 2:
                            event_type, metric_type = parts
                            if event_type in all_metrics and metric_type in all_metrics[event_type]:
                                all_metrics[event_type][metric_type].append(category_metrics[category][col])
                    except Exception as e:
                        print(f"Warning: Could not process column {col}: {str(e)}")
                        continue
        
        # 결과 출력
        print("\nCategory-wise Average Metrics:")
        for category, metrics in category_metrics.items():
            print(f"\n{category}:")
            for metric_name, value in metrics.items():
                if metric_name != "video_name":
                    print(f"{metric_name}: {value:.3f}")
        
        # 전체 평균 계산 및 출력
        print("\n" + "="*50)
        print("Overall Average Metrics Across All Categories:")
        print("="*50)
        
        for event_type in all_metrics:
            print(f"\n{event_type}:")
            for metric_type, values in all_metrics[event_type].items():
                avg_value = np.mean(values)
                print(f"{metric_type}: {avg_value:.3f}")
        ##################################################################################################        
                # 최종 결과를 저장할 딕셔너리
        final_results = {
            "category_metrics": {},
            "overall_metrics": {}
        }
        # 카테고리별 메트릭 저장

        for category, metrics in category_metrics.items():
            final_results["category_metrics"][category] = {}
            for metric_name, value in metrics.items():
                if metric_name != "video_name":
                    if isinstance(value, (int, float)):
                        final_results["category_metrics"][category][metric_name] = float(value)
        
        # 전체 평균 계산 및 저장
        for event_type in all_metrics:
            print(f"\n{event_type}:")
            final_results["overall_metrics"][event_type] = {}
            for metric_type, values in all_metrics[event_type].items():
                avg_value = float(np.mean(values))
                print(f"{metric_type}: {avg_value:.3f}")
                final_results["overall_metrics"][event_type][metric_type] = avg_value
        
        # JSON 파일로 저장
        json_path = os.path.join(self.save_dir, "overall_metrics.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=4)

        # return category_metrics
        return final_results

    def _evaluate_category(self, category: str, pred_path: str, label_path: str) -> pd.DataFrame:
        """카테고리별 평가 수행"""
        results = []
        metrics_columns = ['video_name']
        
        for pred_file in os.listdir(pred_path):
            if not pred_file.endswith('.csv'):
                continue
                
            video_name = os.path.splitext(pred_file)[0]
            pred_df = pd.read_csv(os.path.join(pred_path, pred_file))
            
            # 해당 비디오의 정답 CSV 파일 로드
            label_file = f"{video_name}.csv"
            label_path_full = os.path.join(label_path, label_file)
            
            if not os.path.exists(label_path_full):
                print(f"Warning: Label file not found for {video_name}")
                continue
                
            label_df = pd.read_csv(label_path_full)
            
            # 각 카테고리별 메트릭 계산
            video_metrics = {'video_name': video_name}
            categories = [col for col in pred_df.columns if col != 'frame']
            
            for cat in categories:
                # 정답값과 예측값
                y_true = label_df[cat].values
                y_pred = pred_df[cat].values
                
                # 메트릭 계산
                metrics = self._calculate_metrics(y_true, y_pred)
                
                # 결과 저장
                for metric_name, value in metrics.items():
                    col_name = f"{cat}_{metric_name}"
                    video_metrics[col_name] = value
                    if col_name not in metrics_columns:
                        metrics_columns.append(col_name)
            
            results.append(video_metrics)
        
        # 결과를 데이터프레임으로 변환
        metrics_df = pd.DataFrame(results, columns=metrics_columns)
        
        # 평균 계산하여 추가
        avg_metrics = {'video_name': 'average'}
        for col in metrics_columns[1:]:  # video_name 제외
            avg_metrics[col] = metrics_df[col].mean()
            
        metrics_df = pd.concat([metrics_df, pd.DataFrame([avg_metrics])], ignore_index=True)
        
        return metrics_df
    
    # def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    #     """성능 지표 계산"""
    #     tn = np.sum((y_true == 0) & (y_pred == 0))
    #     fp = np.sum((y_true == 0) & (y_pred == 1))
        
    #     metrics = {
    #         'f1': f1_score(y_true, y_pred, zero_division=0),
    #         'accuracy': accuracy_score(y_true, y_pred),
    #         'precision': precision_score(y_true, y_pred, zero_division=0),
    #         'recall': recall_score(y_true, y_pred, zero_division=0),
    #         'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0
    #     }
        
    #     return metrics
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """성능 지표 계산"""
        tn = np.sum((y_true == 0) & (y_pred == 0))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        tp = np.sum((y_true == 1) & (y_pred == 1))
        
        metrics = {
            'f1': f1_score(y_true, y_pred, zero_division=0),
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
            'tp': int(tp),
            'tn': int(tn),
            'fp': int(fp),
            'fn': int(fn)
        }
        
        return metrics
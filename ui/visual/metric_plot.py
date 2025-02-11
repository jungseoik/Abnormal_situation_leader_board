import plotly.graph_objects as go
import pandas as pd
from sheet_manager.sheet_convert.json2sheet import str2json
import enviroments.config as config

def calculate_avg_metrics(df):
    """
    각 모델의 카테고리별 평균 성능 지표를 계산
    """
    metrics_data = []
    for _, row in df.iterrows():
        model_name = row['Model name']
        
        # PIA가 비어있거나 다른 값인 경우 건너뛰기
        if pd.isna(row['PIA']) or not isinstance(row['PIA'], str):
            print(f"Skipping model {model_name}: Invalid PIA data")
            continue
            
        try:
            metrics = str2json(row['PIA'])
            
            # metrics가 None이거나 dict가 아닌 경우 건너뛰기
            if not metrics or not isinstance(metrics, dict):
                print(f"Skipping model {model_name}: Invalid JSON format")
                continue
                
            # 필요한 카테고리가 모두 있는지 확인
            required_categories = ['falldown', 'violence', 'fire']
            if not all(cat in metrics for cat in required_categories):
                print(f"Skipping model {model_name}: Missing required categories")
                continue
                
            # 필요한 메트릭이 모두 있는지 확인
            required_metrics = config.ALL_METRICS
            
            avg_metrics = {}
            for metric in required_metrics:
                try:
                    values = [metrics[cat][metric] for cat in required_categories 
                             if metric in metrics[cat]]
                    if values:  # 값이 있는 경우만 평균 계산
                        avg_metrics[metric] = sum(values) / len(values)
                    else:
                        avg_metrics[metric] = 0  # 또는 다른 기본값 설정
                except (KeyError, TypeError) as e:
                    print(f"Error calculating {metric} for {model_name}: {str(e)}")
                    avg_metrics[metric] = 0  # 에러 발생 시 기본값 설정
            
            metrics_data.append({
                'model_name': model_name,
                **avg_metrics
            })
            
        except Exception as e:
            print(f"Error processing model {model_name}: {str(e)}")
            continue
    
    return pd.DataFrame(metrics_data)

def create_performance_chart(df, selected_metrics):
    """
    모델별 선택된 성능 지표의 수평 막대 그래프 생성
    """
    fig = go.Figure()
    
    # 모델 이름 길이에 따른 마진 계산
    max_name_length = max([len(name) for name in df['model_name']])
    left_margin = min(max_name_length * 7, 500)  # 글자 수에 따라 마진 조정, 최대 500
    
    for metric in selected_metrics:
        fig.add_trace(go.Bar(
            name=metric,
            y=df['model_name'],  # y축에 모델 이름
            x=df[metric],        # x축에 성능 지표 값
            text=[f'{val:.3f}' for val in df[metric]],
            textposition='auto',
            orientation='h'      # 수평 방향 막대
        ))
    
    fig.update_layout(
        title='Model Performance Comparison',
        yaxis_title='Model Name',
        xaxis_title='Performance',
        barmode='group',
        height=max(400, len(df) * 40),  # 모델 수에 따라 높이 조정
        margin=dict(l=left_margin, r=50, t=50, b=50),  # 왼쪽 마진 동적 조정
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis={'categoryorder': 'total ascending'}  # 성능 순으로 정렬
    )
    
    # y축 레이블 스타일 조정
    fig.update_yaxes(tickfont=dict(size=10))  # 글자 크기 조정
    
    return fig
def create_confusion_matrix(metrics_data, selected_category):
    """혼동 행렬 시각화 생성"""
    tp = metrics_data[selected_category]['tp']
    tn = metrics_data[selected_category]['tn']
    fp = metrics_data[selected_category]['fp']
    fn = metrics_data[selected_category]['fn']
    
    z = [[tn, fp], [fn, tp]]
    x = ['Negative', 'Positive']
    y = ['Negative', 'Positive']
    
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x,
        y=y,
        colorscale=[[0, '#f7fbff'], [1, '#08306b']],
        showscale=False,
        text=[[str(val) for val in row] for row in z],
        texttemplate="%{text}",
        textfont={"color": "black", "size": 16},  # 글자 색상을 검정색으로 고정
    ))
    
    fig.update_layout(
        title={
            'text': f'Confusion Matrix - {selected_category}',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Predicted',
        yaxis_title='Actual',
        width=600,  
        height=600,  
        margin=dict(l=80, r=80, t=100, b=80),  
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(size=14) 
    )
    
    fig.update_xaxes(side="bottom", tickfont=dict(size=14))
    fig.update_yaxes(side="left", tickfont=dict(size=14))

    return fig

def create_category_metrics_chart(metrics_data, selected_metrics):
    """
    선택된 모델의 각 카테고리별 성능 지표 시각화
    """
    fig = go.Figure()
    categories = ['falldown', 'violence', 'fire']
    
    for metric in selected_metrics:
        values = []
        for category in categories:
            values.append(metrics_data[category][metric])
        
        fig.add_trace(go.Bar(
            name=metric,
            x=categories,
            y=values,
            text=[f'{val:.3f}' for val in values],
            textposition='auto',
        ))

    fig.update_layout(
        title='Performance Metrics by Category',
        xaxis_title='Category',
        yaxis_title='Score',
        barmode='group',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

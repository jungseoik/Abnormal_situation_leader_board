import gradio as gr
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sheet_manager.sheet_loader.sheet2df import sheet2df
from sheet_manager.sheet_convert.json2sheet import str2json
import enviroments.config as config
from ui.visual.metric_plot import calculate_avg_metrics, create_performance_chart, create_confusion_matrix, create_category_metrics_chart

def metric_visual_tab():
    
    df = sheet2df(sheet_name="metric")
    avg_metrics_df = calculate_avg_metrics(df)
    all_metrics = config.ALL_METRICS
    
    with gr.Tab("📊 Performance Visualization"):
        with gr.Row():
            metrics_multiselect = gr.CheckboxGroup(
                choices=all_metrics,
                value=[],  # 초기 선택 없음
                label="Select Performance Metrics",
                interactive=True
            )
        
        performance_plot = gr.Plot()
        
        def update_plot(selected_metrics):
            if not selected_metrics:
                return None
            try:
                sorted_df = avg_metrics_df.sort_values(by='accuracy', ascending=True)
                return create_performance_chart(sorted_df, selected_metrics)
            except Exception as e:
                print(f"Error in update_plot: {str(e)}")
                return None
        
        metrics_multiselect.change(
            fn=update_plot,
            inputs=[metrics_multiselect],
            outputs=[performance_plot]
        )
        
        gr.Markdown("## Detailed Model Analysis")
        with gr.Row():
            model_dropdown = gr.Dropdown(
                choices=sorted(df['Model name'].unique().tolist()),
                label="Select Model",
                interactive=True
            )
            
            column_dropdown = gr.Dropdown(
                choices=[col for col in df.columns if col != 'Model name'],
                label="Select Metric Column",
                interactive=True
            )
            
            category_dropdown = gr.Dropdown(
                choices=['falldown', 'violence', 'fire'],
                label="Select Category",
                interactive=True
            )
        
        # 혼동 행렬 시각화
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("") 
            with gr.Column(scale=2):
                confusion_matrix_plot = gr.Plot(container=True) 
            with gr.Column(scale=1):
                gr.Markdown("") 

        with gr.Column(scale=2):
            # 성능 지표 선택
            metrics_select = gr.CheckboxGroup(
                choices=config.ALL_METRICS,
                value=['accuracy'],  # 기본값
                label="Select Metrics to Display",
                interactive=True
            )
            category_metrics_plot = gr.Plot()

        def update_visualizations(model, column, category, selected_metrics):
            if not all([model, column]):  # category는 혼동행렬에만 필요
                return None, None
                
            try:
                # 선택된 모델의 데이터 가져오기
                selected_data = df[df['Model name'] == model][column].iloc[0]
                metrics = str2json(selected_data)
                
                if not metrics:
                    return None, None
                    
                # 혼동 행렬 (왼쪽)
                confusion_fig = create_confusion_matrix(metrics, category) if category else None
                
                # 카테고리별 성능 지표 (오른쪽)
                if not selected_metrics:
                    selected_metrics = ['accuracy']
                category_fig = create_category_metrics_chart(metrics, selected_metrics)
                
                return confusion_fig, category_fig
                
            except Exception as e:
                print(f"Error updating visualizations: {str(e)}")
                return None, None
        
        # 이벤트 핸들러 연결
        for input_component in [model_dropdown, column_dropdown, category_dropdown, metrics_select]:
            input_component.change(
                fn=update_visualizations,
                inputs=[model_dropdown, column_dropdown, category_dropdown, metrics_select],
                outputs=[confusion_matrix_plot, category_metrics_plot]
            )        




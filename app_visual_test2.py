import gradio as gr
from pathlib import Path
from leaderboard_ui.tab.submit_tab import submit_tab
from leaderboard_ui.tab.leaderboard_tab import leaderboard_tab
abs_path = Path(__file__).parent
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Mock 데이터 생성
def create_mock_data():
    benchmarks = ['VQA-2023', 'ImageQuality-2024', 'VideoEnhance-2024']
    categories = ['Animation', 'Game', 'Movie', 'Sports', 'Vlog']
    
    data_list = []
    
    for benchmark in benchmarks:
        n_videos = np.random.randint(50, 100)
        for _ in range(n_videos):
            category = np.random.choice(categories)
            
            data_list.append({
                "비디오이름": f"video_{np.random.randint(1000, 9999)}.mp4",
                "해상도": np.random.choice(["1920x1080", "3840x2160", "1280x720"]),
                "비디오 시간": f"{np.random.randint(0, 10)}:{np.random.randint(0, 60)}",
                "카테고리": category,
                "벤치마크": benchmark,
                "비디오길이 초": np.random.randint(30, 600),
                "비디오 총 프레임수": np.random.randint(1000, 10000),
                "파일형식": ".mp4",
                "파일크기(MB)": round(np.random.uniform(10, 1000), 2),
                "화면비율": 16/9,
                "fps": np.random.choice([24, 30, 60])
            })
    
    return pd.DataFrame(data_list)
def create_bar_chart(df, selected_benchmark, selected_categories, selected_column):
    # 벤치마크와 카테고리로 필터링
    filtered_df = df[df['벤치마크'] == selected_benchmark]
    if selected_categories:
        filtered_df = filtered_df[filtered_df['카테고리'].isin(selected_categories)]
    
    # 선택된 열에 대한 막대 그래프 생성
    fig = px.bar(
        filtered_df,
        x=selected_column,
        y='비디오이름',
        color='카테고리',  # 카테고리별로 색상 구분
        title=f'{selected_benchmark} - 비디오별 {selected_column}',
        orientation='h',  # 수평 막대 그래프
        color_discrete_sequence=px.colors.qualitative.Set3  # 색상 팔레트 설정
    )
    
    # 그래프 레이아웃 조정
    fig.update_layout(
        height=max(400, len(filtered_df) * 30),  # 데이터 수에 따라 높이 조정
        yaxis={'categoryorder': 'total ascending'},  # 값 기준으로 정렬
        margin=dict(l=200),  # 긴 비디오 이름을 위한 여백
        showlegend=True,  # 범례 표시
        legend=dict(
            orientation="h",  # 범례를 수평으로 배치
            yanchor="bottom",
            y=1.02,  # 그래프 위에 범례 배치
            xanchor="right",
            x=1
        )
    )
    
    return fig

# Mock 데이터 생성
df = create_mock_data()

def create_category_pie_chart(df, selected_benchmark, selected_categories=None):
    filtered_df = df[df['벤치마크'] == selected_benchmark]
    
    if selected_categories:
        filtered_df = filtered_df[filtered_df['카테고리'].isin(selected_categories)]
    
    category_counts = filtered_df['카테고리'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title=f'{selected_benchmark} - 카테고리별 비디오 분포',
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig
 
###TODO 스트링일경우 어케 처리

def leaderboard_tab():
    with gr.Blocks() as demo:
        with gr.Tab("📊 벤치마크 시각화"):
            with gr.Row():
                benchmark_dropdown = gr.Dropdown(
                    choices=sorted(df['벤치마크'].unique().tolist()),
                    value=sorted(df['벤치마크'].unique().tolist())[0],
                    label="벤치마크 선택",
                    interactive=True
                )
                
                category_multiselect = gr.CheckboxGroup(
                    choices=sorted(df['카테고리'].unique().tolist()),
                    label="카테고리 선택 (선택하지 않으면 전체)",
                    interactive=True
                )
            
            # 파이 차트
            pie_plot_output = gr.Plot()
            
            # 데이터 컬럼 선택을 위한 드롭다운 추가
            column_options = [
                "비디오 시간", "비디오길이 초", "비디오 총 프레임수", 
                "파일크기(MB)", "화면비율", "fps", "파일형식"
            ]
            
            column_dropdown = gr.Dropdown(
                choices=column_options,
                value=column_options[0],
                label="비교할 데이터 선택",
                interactive=True
            )
            
            # 막대 그래프
            bar_plot_output = gr.Plot()
            
            def update_plots(benchmark, categories, selected_column):
                pie_chart = create_category_pie_chart(df, benchmark, categories)
                bar_chart = create_bar_chart(df, benchmark, categories, selected_column)
                return pie_chart, bar_chart
            
            # 이벤트 핸들러 연결
            benchmark_dropdown.change(
                fn=update_plots,
                inputs=[benchmark_dropdown, category_multiselect, column_dropdown],
                outputs=[pie_plot_output, bar_plot_output]
            )
            category_multiselect.change(
                fn=update_plots,
                inputs=[benchmark_dropdown, category_multiselect, column_dropdown],
                outputs=[pie_plot_output, bar_plot_output]
            )
            column_dropdown.change(
                fn=update_plots,
                inputs=[benchmark_dropdown, category_multiselect, column_dropdown],
                outputs=[pie_plot_output, bar_plot_output]
            )
        
        return demo

if __name__ == "__main__":
    demo = leaderboard_tab()
    demo.launch()
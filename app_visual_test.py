import gradio as gr
from pathlib import Path
from leaderboard_ui.tab.submit_tab import submit_tab
from leaderboard_ui.tab.leaderboard_tab import leaderboard_tab
abs_path = Path(__file__).parent

# with gr.Blocks() as demo:
#     gr.Markdown("""
#     # 🥇 PIA_leaderboard
#     """)
#     with gr.Tabs():
#         leaderboard_tab()
#         submit_tab()
        

# if __name__ == "__main__":
#     demo.launch()


import gradio as gr
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def display_plot(plot_type):
    # 샘플 데이터 생성
    data = {
        '게임': ['롤', '피파', '배그', '오버워치', '로스트아크'],
        '플레이어수': [1500, 800, 1200, 950, 1100],
        '평균플레이시간': [2.5, 1.8, 3.2, 2.1, 4.5]
    }
    df = pd.DataFrame(data)
    
    if plot_type == "막대 그래프":
        # 게임별 플레이어 수를 보여주는 막대 그래프
        fig = px.bar(df, 
                    x='게임', 
                    y='플레이어수',
                    title='게임별 플레이어 수',
                    color='플레이어수',
                    labels={'플레이어수': '활성 플레이어 (천 명)'},
                    template='plotly_dark')
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        
    else:
        # 게임별 점유율을 보여주는 파이 차트
        fig = px.pie(df, 
                    values='플레이어수', 
                    names='게임',
                    title='게임별 플레이어 점유율',
                    hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig

# Gradio 인터페이스 생성
demo = gr.Interface(
    fn=display_plot,
    inputs=gr.Radio(["막대 그래프", "파이 차트"], label="그래프 종류 선택"),
    outputs=gr.Plot(),
    title="게임 통계 시각화",
    description="게임별 플레이어 통계를 다양한 그래프로 확인해보세요"
)

if __name__ == "__main__":
    demo.launch()
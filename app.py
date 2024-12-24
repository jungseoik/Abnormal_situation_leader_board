import gradio as gr
from gradio_leaderboard import Leaderboard, SelectColumns, ColumnFilter,SearchColumns
import config
from pathlib import Path
import pandas as pd
import random
from sheet_loader.sheet2df import sheet2df
abs_path = Path(__file__).parent

# 상세 데이터
df_detail = {
    "PIA-SPACE-LAB/20241014_FT_CLIP4Clip_KTT": pd.DataFrame({
        "Attribute": ["Height", "Weight", "Average F1"],
        "Value": [170, 65, 85.3]
    }),
}

# 메인 데이터프레임
df_main = pd.DataFrame({
    "Model name": ["PIA-SPACE-LAB/20241014_FT_CLIP4Clip_KTT"] * 3,  # 동일한 모델 이름 반복
    "Accuracy": [90, 85, 88],
    "Params (B)": [1.2, 0.8, 1.5]
})
def on_select(evt: gr.SelectData):
    selected_value = evt.value  # 클릭된 셀의 값
    selected_index = evt.index  # 클릭된 셀의 (row, col)
        # 디버깅 로그 추가
    print(f"Selected value: {selected_value}")
    print(f"Selected index: {selected_index}")
    # 선택된 열 이름 확인
    col_name = df_main.columns[selected_index[1]]
    print(f"Column name: {col_name}")

    # 클릭된 열의 인덱스 확인 (0번째 열이 "Model name")
    if selected_index[1] == 0:  # "Model name" 열
        # 선택된 모델 이름으로 세부 데이터 반환
        details = df_detail.get(selected_value, pd.DataFrame({"Message": ["No details available"]}))
        print(f"Details found: {not details.empty}")  # 디버깅 로그
        return details
    else:
        # 다른 열 클릭 시 적절한 메시지 반환
        return pd.DataFrame({"Message": [f"Please select a value from the 'Model name' column. You selected from column index {selected_index[1]}"]})    
    # # "Model name" 열만 처리
    # if col_name == "Model name":
    #     # 선택된 모델 이름으로 세부 데이터 반환
    #     return df_detail.get(selected_value, pd.DataFrame({"Message": ["No details available"]}))
    # else:
    #     # 다른 열 클릭 시 메시지 반환
    #     return pd.DataFrame({"Message": ["Please select a valid Model name"]})

with gr.Blocks() as demo:
    gr.Markdown("""
    # 🥇 PIA_leaderboard
    """)
    with gr.Tabs():
        with gr.Tab("Demo"):
            leaderboard = Leaderboard(
                value=sheet2df(),
                select_columns=SelectColumns(
                    default_selection=config.ON_LOAD_COLUMNS,
                    cant_deselect=config.OFF_LOAD_COLUMNS,
                    label="Select Columns to Display:",
                    info="Check"
                ),

                search_columns=SearchColumns(
                    primary_column="Model name", 
                    secondary_columns=["TASK"],                 
                    placeholder="Search",
                    label="Search"
                ),
                hide_columns=["#Params (B)"],
                filter_columns=[
                    "TASK",
                    ColumnFilter("Average F1", default=[30, 80]),
                ],

                datatype=config.TYPES,
                # column_widths=["33%", "10%"],

            )
            # 세부 정보를 표시할 데이터프레임
            detail_view = gr.Dataframe(label="Model Details")
            # 클릭 이벤트 연결
            leaderboard.select(on_select, outputs=detail_view)
            
        with gr.Tab("Docs"):
            gr.Markdown((Path(__file__).parent / "docs.md").read_text())

if __name__ == "__main__":
    demo.launch()

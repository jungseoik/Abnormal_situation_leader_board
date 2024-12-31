import gradio as gr
import pandas as pd

# 데이터 생성
df_main = pd.DataFrame({
    "ID": [1, 2, 3],
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35]
})

df_detail = {
    1: pd.DataFrame({"Attribute": ["Height", "Weight"], "Value": [170, 65]}),
    2: pd.DataFrame({"Attribute": ["Height", "Weight"], "Value": [180, 75]}),
    3: pd.DataFrame({"Attribute": ["Height", "Weight"], "Value": [160, 55]})
}

# 클릭 이벤트 처리 함수
def on_select(evt: gr.SelectData):
    # 선택된 셀의 위치 및 값 가져오기
    selected_value = evt.value
    selected_index = evt.index  # (row, col) 형태
    # 선택된 칼럼이 "ID"인지 확인
    col_name = df_main.columns[selected_index[1]]  # 선택된 열 이름
    print(selected_value, col_name)

    if col_name == "ID":
        selected_id = int(selected_value)
        return df_detail.get(selected_id, pd.DataFrame())
    else:
        # 다른 칼럼 클릭 시 기본 메시지 반환
        return pd.DataFrame({"Message": ["Please select an ID to view details"]})

with gr.Blocks() as demo:
    # 메인 데이터프레임
    dataframe_main = gr.Dataframe(df_main, label="Main DataFrame")
    # 세부 정보를 표시할 데이터프레임
    dataframe_detail = gr.Dataframe(label="Detail DataFrame")
    
    # 이벤트 리스너 설정
    dataframe_main.select(on_select, outputs=dataframe_detail)

demo.launch()

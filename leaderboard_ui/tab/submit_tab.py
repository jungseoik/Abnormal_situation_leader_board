import gradio as gr


# def update_components(submit_type):
#     if submit_type == "Model":
#         return gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True)
#     else:
#         return gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)
from sheet_manager.sheet_crud.sheet_crud import  SheetManager
import pandas as pd

def list_to_dataframe(data):
    """
    리스트 데이터를 데이터프레임으로 변환하는 함수.
    각 값이 데이터프레임의 한 행(row)에 들어가도록 설정.
    
    :param data: 리스트 형태의 데이터
    :return: pandas.DataFrame
    """
    if not isinstance(data, list):
        raise ValueError("입력 데이터는 리스트 형태여야 합니다.")
    
    # 열 이름을 문자열로 설정
    headers = [f"Queue {i}" for i in range(len(data))]
    df = pd.DataFrame([data], columns=headers)
    return df

def model_submit(model_id):
    model_id = model_id.split("/")[-1]
    sheet_manager = SheetManager()
    sheet_manager.push(model_id)
    return list_to_dataframe(sheet_manager.get_all_values())

def read_queue():
    sheet_manager = SheetManager()
    return list_to_dataframe(sheet_manager.get_all_values())

def submit_tab():
    with gr.Tab("🚀 Submit here! "):
        with gr.Row():
            gr.Markdown("# ✉️✨ Submit your Result here!")

        with gr.Row():
            with gr.Tab("Model"):
                with gr.Row():
                    with gr.Column():
                        model_id_textbox = gr.Textbox(
                            label="huggingface_id", 
                            placeholder="PIA-SPACE-LAB/T2V_CLIP4Clip",
                            interactive = True
                            )
                    with gr.Column():
                        gr.Markdown("## 평가를 받아보세요 반드시 허깅페이스에 업로드된 모델이어야 합니다.")
                        gr.Markdown("#### 현재 평가 대기중 모델입니다.")
                        model_queue = gr.Dataframe()
                        refresh_button = gr.Button("refresh")
                        refresh_button.click(
                            fn=read_queue,
                            outputs=model_queue
                        )
                with gr.Row():
                    model_submit_button = gr.Button("Submit Eval")
                    model_submit_button.click(
                        fn=model_submit,
                        inputs=model_id_textbox,
                        outputs=model_queue
                    )
            with gr.Tab("Prompt"):
                with gr.Row():
                    with gr.Column():
                        prompt_cfg_selector = gr.Dropdown(
                            choices=["전부"],
                            label="Prompt_CFG",
                            multiselect=False,
                            value=None,
                            interactive=True,
                        )
                        weight_type = gr.Dropdown(
                            choices=["전부"],
                            label="Weights type",
                            multiselect=False,
                            value=None,
                            interactive=True,
                        )
                    with gr.Column():
                        gr.Markdown("## 평가를 받아보세요 반드시 허깅페이스에 업로드된 모델이어야 합니다.")

                with gr.Row():
                    prompt_submit_button = gr.Button("Submit Eval")

            with gr.Tab("Result"):
                with gr.Row():
                    with gr.Column():
                        precision = gr.Dropdown(
                            choices=["전부"],
                            label="Result",
                            multiselect=False,
                            value=None,
                            interactive=True,
                        )
                        weight_type = gr.Dropdown(
                            choices=["전부"],
                            label="Weights type",
                            multiselect=False,
                            value=None,
                            interactive=True,
                        )
                    with gr.Column():
                        a = 1
                        gr.Markdown("## 평가를 받아보세요 반드시 허깅페이스에 업로드된 모델이어야 합니다.")


        # submit_button = gr.Button("Submit Eval")
        # submission_result = gr.Markdown()


            # model_submit_button.click(
            #     add_new_eval,
            #     [
            #         model_id_textbox,

            #     ],
            #     submission_result,
            # )

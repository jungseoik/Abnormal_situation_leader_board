import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from dotenv import load_dotenv
import os
from enviroments.convert import get_json_from_env_var
from utils.logger import custom_logger
logger = custom_logger(__name__)
load_dotenv()

def sheet2df(sheet_name: str = "model") -> pd.DataFrame:
    """
    Google 스프레드시트에서 데이터를 읽어와 Pandas DataFrame으로 변환하는 함수.

    동작 과정:
    1. 환경변수에서 Google API 인증 정보를 불러와 서비스 계정 인증 수행.
    2. 환경변수에서 스프레드시트 URL을 가져와 해당 문서를 열기.
    3. 지정된 시트(sheet_name)를 선택하여 데이터 불러오기.
    4. 데이터를 Pandas DataFrame으로 변환.
    5. 첫 번째 행을 컬럼명으로 설정하고 기존 첫 번째 행을 삭제하여 데이터 정리.

    Args:
        sheet_name (str, optional): 불러올 시트의 이름. 기본값은 "model".

    Returns:
        pd.DataFrame: 스프레드시트 데이터를 정리한 Pandas DataFrame.

    필수 환경 변수:
    - `GOOGLE_CREDENTIALS`: Google API 인증 정보를 JSON 형식의 문자열로 저장.
    - `SPREADSHEET_URL`: 데이터를 가져올 Google 스프레드시트의 URL.

    """
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # 환경변수에서 Google API 인증 JSON 정보 가져오기
    json_key_dict = get_json_from_env_var("GOOGLE_CREDENTIALS")
    credential = ServiceAccountCredentials.from_json_keyfile_dict(json_key_dict, scope)
    gc = gspread.authorize(credential)
    
    # 스프레드시트 열기
    spreadsheet_url = os.getenv("SPREADSHEET_URL")
    doc = gc.open_by_url(spreadsheet_url)
    sheet = doc.worksheet(sheet_name)
    
    # 데이터를 DataFrame으로 변환
    df = pd.DataFrame(sheet.get_all_values())

    # 첫 번째 행을 컬럼명으로 지정 후 기존 첫 번째 행 삭제
    df.rename(columns=df.iloc[0], inplace=True)
    df.drop(df.index[0], inplace=True)

    return df

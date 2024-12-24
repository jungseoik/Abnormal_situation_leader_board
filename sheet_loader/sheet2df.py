import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def sheet2df():
    """
    Reads data from a specified Google Spreadsheet and converts it into a Pandas DataFrame.

    Steps:
    1. Authenticate using a service account JSON key.
    2. Open the spreadsheet by its URL.
    3. Select the worksheet to read.
    4. Convert the worksheet data to a Pandas DataFrame.
    5. Clean up the DataFrame:
        - Rename columns using the first row of data.
        - Drop the first row after renaming columns.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the cleaned data from the spreadsheet.

    Note:
    - The following variables must be configured before using this function:
      - `json_key_path`: Path to the service account JSON key file.
      - `spreadsheet_url`: URL of the Google Spreadsheet.
      - `sheet_name`: Name of the worksheet to load.

    Dependencies:
    - pandas
    - gspread
    - oauth2client
    """
    # Define scope and key path
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    json_key_path = "enviroments/abnormal-situation-leaderboard-3ca42d06719e.json"
    
    # Authenticate and open Google Spreadsheet
    credential = ServiceAccountCredentials.from_json_keyfile_name(json_key_path, scope)
    gc = gspread.authorize(credential)
    
    # Spreadsheet URL and worksheet selection
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1MY0okfx4niDAH1SovZ8Wh1K9QosL2Cww09ORtPrC-yQ/edit?gid=0#gid=0"
    doc = gc.open_by_url(spreadsheet_url)
    sheet = doc.worksheet("시트1")
    
    # Convert to DataFrame
    df = pd.DataFrame(sheet.get_all_values())
    
    # Clean DataFrame
    df.rename(columns=df.iloc[0], inplace=True)
    df.drop(df.index[0], inplace=True)
    
    return df

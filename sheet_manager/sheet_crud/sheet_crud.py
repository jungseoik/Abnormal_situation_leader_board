import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from dotenv import load_dotenv
from enviroments.convert import get_json_from_env_var
from typing import Optional, List

load_dotenv()

class SheetManager:
    def __init__(self, spreadsheet_url: Optional[str] = None):
        """
        Initialize SheetManager with Google Sheets credentials and connection.
        """
        self.spreadsheet_url = spreadsheet_url or os.getenv("SPREADSHEET_URL")
        if not self.spreadsheet_url:
            raise ValueError("Spreadsheet URL not provided and not found in environment variables")
        
        # Initialize credentials and client
        self._init_google_client()
        
        # Initialize sheet connection
        self.doc = None
        self.sheet = None
        self.col_index = None
        self._connect_to_sheet()

    def _init_google_client(self):
        """Initialize Google Sheets client with credentials."""
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        json_key_dict = get_json_from_env_var("GOOGLE_CREDENTIALS")
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_key_dict, scope)
        self.client = gspread.authorize(credentials)
    
    def _connect_to_sheet(self):
        """Connect to the specified Google Sheet and initialize necessary attributes."""
        try:
            self.doc = self.client.open_by_url(self.spreadsheet_url)
            self.sheet = self.doc.worksheet("flag")
            
            headers = self.sheet.row_values(1)
            try:
                self.col_index = headers.index("huggingface_id") + 1
            except ValueError:
                raise ValueError("Column 'huggingface_id' not found in sheet")
                
        except Exception as e:
            raise ConnectionError(f"Failed to connect to sheet: {str(e)}")

    def _reconnect_if_needed(self):
        """Reconnect to the sheet if the connection is lost."""
        try:
            self.sheet.row_values(1)
        except (gspread.exceptions.APIError, AttributeError):
            self._init_google_client()
            self._connect_to_sheet()

    def _fetch_column_data(self) -> List[str]:
        """Fetch all data from the huggingface_id column."""
        values = self.sheet.col_values(self.col_index)
        return values[1:]  # Exclude header

    def _update_sheet(self, data: List[str]):
        """Update the entire column with new data."""
        try:
            # Prepare the range for update (excluding header)
            start_cell = gspread.utils.rowcol_to_a1(2, self.col_index)  # Start from row 2
            end_cell = gspread.utils.rowcol_to_a1(len(data) + 2, self.col_index)
            range_name = f"{start_cell}:{end_cell}"
            
            # Convert data to 2D array format required by gspread
            cells = [[value] for value in data]
            
            # Update the range
            self.sheet.update(range_name, cells)
        except Exception as e:
            print(f"Error updating sheet: {str(e)}")
            raise

    def push(self, text: str) -> int:
        """
        Push a text value to the next empty cell in the huggingface_id column.
        
        Args:
            text (str): Text to push to the sheet
            
        Returns:
            int: The row number where the text was pushed
        """
        try:
            self._reconnect_if_needed()
            
            # Get all values in the huggingface_id column
            column_values = self.sheet.col_values(self.col_index)
            
            # Find the next empty row
            next_row = None
            for i in range(1, len(column_values)):
                if not column_values[i].strip():
                    next_row = i + 1
                    break
            
            # If no empty row found, append to the end
            if next_row is None:
                next_row = len(column_values) + 1

            # Update the cell
            self.sheet.update_cell(next_row, self.col_index, text)
            print(f"Successfully pushed value: {text} to row {next_row}")
            return next_row
            
        except Exception as e:
            print(f"Error pushing to sheet: {str(e)}")
            raise

    def pop(self) -> Optional[str]:
        """Remove and return the most recent value."""
        try:
            self._reconnect_if_needed()
            data = self._fetch_column_data()
            
            if not data or not data[0].strip():
                return None
            
            value = data.pop(0)  # Remove first value
            data.append("")  # Add empty string at the end to maintain sheet size
            
            self._update_sheet(data)
            print(f"Successfully popped value: {value}")
            return value
            
        except Exception as e:
            print(f"Error popping from sheet: {str(e)}")
            raise

    def delete(self, value: str) -> List[int]:
        """Delete all occurrences of a value."""
        try:
            self._reconnect_if_needed()
            data = self._fetch_column_data()
            
            # Find all indices before deletion
            indices = [i + 1 for i, v in enumerate(data) if v.strip() == value.strip()]
            if not indices:
                print(f"Value '{value}' not found in sheet")
                return []
            
            # Remove matching values and add empty strings at the end
            data = [v for v in data if v.strip() != value.strip()]
            data.extend([""] * len(indices))  # Add empty strings to maintain sheet size
            
            self._update_sheet(data)
            print(f"Successfully deleted value '{value}' from rows: {indices}")
            return indices
            
        except Exception as e:
            print(f"Error deleting from sheet: {str(e)}")
            raise

    def get_all_values(self) -> List[str]:
        """Get all values from the huggingface_id column."""
        self._reconnect_if_needed()
        return [v for v in self._fetch_column_data() if v.strip()]

# Example usage
if __name__ == "__main__":
    # Initialize sheet manager
    sheet_manager = SheetManager()
    
    # Push some test values
    sheet_manager.push("test-model-1")
    sheet_manager.push("test-model-2")
    sheet_manager.push("test-model-3")
    
    print("Initial values:", sheet_manager.get_all_values())
    
    # Pop the most recent value
    popped = sheet_manager.pop()
    print(f"Popped value: {popped}")
    print("After pop:", sheet_manager.get_all_values())
    
    # Delete a specific value
    deleted_rows = sheet_manager.delete("test-model-2")
    print(f"Deleted from rows: {deleted_rows}")
    print("After delete:", sheet_manager.get_all_values())
import json
from sheet_manager.sheet_crud.sheet_crud import SheetManager
from typing import Dict, Any, Optional

class Json2Sheet:
    def __init__(self, worksheet_name: str = "metric", column_name: str = "metrics"):
        """
        Initialize Json2Sheet with sheet configuration
        
        Args:
            worksheet_name (str): Name of the worksheet to operate on. Defaults to "metric".
            column_name (str): Name of the column to operate on. Defaults to "metrics".
        """
        self.sheet_manager = SheetManager(
            worksheet_name=worksheet_name,
            column_name=column_name
        )
        
    def dict_to_sheet(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Convert dictionary to JSON string and push to sheet
        
        Args:
            data: Dictionary to be converted and stored
            
        Returns:
            Optional[int]: Row number where the data was stored, None if failed
        """
        try:
            # Convert dictionary to JSON string
            json_str = json.dumps(data, ensure_ascii=False)
            
            # Push to sheet
            row_num = self.sheet_manager.push(json_str)
            print(f"Successfully pushed JSON data to row {row_num}")
            return row_num
            
        except Exception as e:
            print(f"Error pushing JSON to sheet: {str(e)}")
            return None
            
    def update_metrics_by_model(self, model_name: str, metrics_data: Dict[str, Any]) -> Optional[int]:
        """
        Update metrics for a specific model
        
        Args:
            model_name: Name of the model to update metrics for
            metrics_data: Dictionary containing metrics data
            
        Returns:
            Optional[int]: Row number where the data was updated, None if failed
        """
        try:
            json_str = json.dumps(metrics_data, ensure_ascii=False)
            row_num = self.sheet_manager.update_cell_by_condition(
                condition_column="Model name",
                condition_value=model_name,
                target_column=self.sheet_manager.column_name,
                target_value=json_str
            )
            return row_num
        except Exception as e:
            print(f"Error updating metrics for model {model_name}: {str(e)}")
            return None

# Test code
if __name__ == "__main__":
    # Test data
    test_metrics = {
        "overall_metrics": {
            "falldown": {"accuracy": 0.85, "f1": 0.82},
            "violence": {"accuracy": 0.78, "f1": 0.75},
            "fire": {"accuracy": 0.92, "f1": 0.90}
        },
        "category_metrics": {
            "test_category": {
                "falldown_accuracy": 0.85,
                "violence_accuracy": 0.78,
                "fire_accuracy": 0.92
            }
        }
    }
    
    # Initialize Json2Sheet
    json2sheet = Json2Sheet(worksheet_name="metric", column_name="metrics")
    
    # Test pushing new data
    print("\nTesting push operation:")
    row_num = json2sheet.dict_to_sheet(test_metrics)
    print(f"Data pushed to row: {row_num}")
    
    # Test updating existing model
    print("\nTesting update operation:")
    updated_row = json2sheet.update_metrics_by_model("test_model", test_metrics)
    print(f"Data updated in row: {updated_row}")
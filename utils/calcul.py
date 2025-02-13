
import os
def calculate_total_accuracy(metrics: dict) -> float:
    """
    모든 카테고리의 평균 정확도를 계산합니다. 'micro_avg' 카테고리는 제외됩니다.

    Args:
        metrics (Dict[str, Dict[str, float]]): 정확도 값을 포함하는 메트릭 딕셔너리
            형식: {
                "카테고리1": {"accuracy": float, ...},
                "카테고리2": {"accuracy": float, ...},
                ...
            }

    Returns:
        float: 모든 카테고리의 평균 정확도 값

    Raises:
        ValueError: 메트릭 딕셔너리에 accuracy 값이 하나도 없는 경우 발생

    Examples:
        >>> metrics = {
        ...     "category1": {"accuracy": 0.8},
        ...     "category2": {"accuracy": 0.9},
        ...     "micro_avg": {"accuracy": 0.85}
        ... }
        >>> calculate_total_accuracy(metrics)
        0.85
    """
    total_accuracy = 0
    total_count = 0

    for category, values in metrics.items():
        if category == "micro_avg":
            continue  # Skip 'micro_avg'

        if "accuracy" in values:
            total_accuracy += values["accuracy"]
            total_count += 1

    if total_count == 0:
        raise ValueError("No accuracy values found in the provided metrics dictionary.")

    return total_accuracy / total_count
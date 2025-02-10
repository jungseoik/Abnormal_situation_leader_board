import json
from typing import Dict, List, Tuple, Optional, Any

def load_config(config_path: str) -> Dict[str, Any]:
    """
    JSON 설정 파일을 읽어서 딕셔너리로 반환합니다.
    
    Args:
        config_path (str): JSON 설정 파일의 경로
        
    Returns:
        Dict[str, Any]: 설정 정보가 담긴 딕셔너리
        
    Raises:
        FileNotFoundError: 설정 파일을 찾을 수 없는 경우
        json.JSONDecodeError: JSON 파일 형식이 잘못된 경우
        
    Example:
        >>> config = load_config("prompt_config.json")
        >>> print(config["PROMPT_CFG"])
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

class PromptManager:
    """
    프롬프트 설정을 관리하고 검색하는 클래스입니다.
    
    이벤트, 상태(normal/abnormal), 프롬프트 인덱스를 기반으로 
    프롬프트 문장을 관리하고 검색할 수 있습니다.

    Attributes:
        config (Dict): 전체 설정 정보
        sentences (List[str]): 모든 프롬프트 문장 목록
        index_mapping (Dict): (event_idx, status, prompt_idx) -> sentence 매핑
        reverse_mapping (Dict): sentence -> [(event_idx, status, prompt_idx)] 매핑

    Example:
        >>> manager = PromptManager("config.json")
        >>> sentences = manager.get_all_sentences()
        >>> details = manager.get_details_by_sentence(sentences[0])
    """
    
    def __init__(self, config_path: str):
        """
        PromptManager 인스턴스를 초기화합니다.

        Args:
            config_path (str): 프롬프트 설정 JSON 파일 경로
            
        Raises:
            FileNotFoundError: 설정 파일을 찾을 수 없는 경우
            KeyError: 필수 설정 키가 누락된 경우
        """
        self.config = load_config(config_path)
        self.sentences, self.index_mapping = self._extract_all_sentences_with_index()
        self.reverse_mapping = self._create_reverse_mapping()
    
    def _extract_all_sentences_with_index(self) -> Tuple[List[str], Dict[Tuple[int, str, int], str]]:
        """
        설정에서 모든 프롬프트 문장과 인덱스 매핑을 추출합니다.
        
        Returns:
            Tuple[List[str], Dict[Tuple[int, str, int], str]]: 
                - 모든 프롬프트 문장 리스트
                - (event_idx, status, prompt_idx) -> sentence 매핑 딕셔너리
                
        Note:
            인덱스 매핑의 키는 (이벤트 인덱스, 상태, 프롬프트 인덱스) 형태의 튜플입니다.
        """
        sentences = []
        index_mapping = {}
        
        for event_idx, event_config in enumerate(self.config.get('PROMPT_CFG', [])):
            prompts = event_config.get('prompts', {})
            for status in ['normal', 'abnormal']:
                for prompt_idx, prompt in enumerate(prompts.get(status, [])):
                    sentence = prompt.get('sentence', '')
                    sentences.append(sentence)
                    index_mapping[(event_idx, status, prompt_idx)] = sentence
        
        return sentences, index_mapping
    
    def _create_reverse_mapping(self) -> Dict[str, List[Tuple[int, str, int]]]:
        """
        문장에서 인덱스로의 역방향 매핑을 생성합니다.
        
        Returns:
            Dict[str, List[Tuple[int, str, int]]]: 
                문장을 키로 하고, 해당 문장이 사용된 모든 위치의 인덱스 튜플 리스트를 값으로 하는 딕셔너리
        
        Note:
            동일한 문장이 여러 위치에서 사용될 수 있으므로, 값은 리스트 형태입니다.
        """
        reverse_map = {}
        for indices, sent in self.index_mapping.items():
            if sent not in reverse_map:
                reverse_map[sent] = []
            reverse_map[sent].append(indices)
        return reverse_map
    
    def get_sentence_indices(self, sentence: str) -> List[Tuple[int, str, int]]:
        """
        주어진 문장이 사용된 모든 위치의 인덱스를 반환합니다.
        
        Args:
            sentence (str): 검색할 프롬프트 문장
            
        Returns:
            List[Tuple[int, str, int]]: 
                (event_idx, status, prompt_idx) 형태의 인덱스 튜플 리스트
                
        Example:
            >>> indices = manager.get_sentence_indices("특정 문장")
            >>> for event_idx, status, prompt_idx in indices:
            ...     print(f"Event {event_idx}, {status}, Prompt {prompt_idx}")
        """
        return self.reverse_mapping.get(sentence, [])
    
    def get_details_by_sentence(self, sentence: str) -> List[Dict[str, Any]]:
        """
        문장으로 관련된 모든 상세 정보를 검색합니다.
        
        Args:
            sentence (str): 검색할 프롬프트 문장
            
        Returns:
            List[Dict[str, Any]]: 해당 문장이 사용된 모든 위치의 상세 정보 리스트
            각 딕셔너리는 다음 키를 포함합니다:
                - event: 이벤트 이름
                - status: 상태 (normal/abnormal)
                - sentence: 프롬프트 문장
                - top_candidates: 상위 후보 수
                - alert_threshold: 경고 임계값
                - event_idx: 이벤트 인덱스
                - prompt_idx: 프롬프트 인덱스
        """
        indices = self.get_sentence_indices(sentence)
        return [self.get_details_by_index(*idx) for idx in indices]
    
    def get_details_by_index(self, event_idx: int, status: str, prompt_idx: int) -> Dict[str, Any]:
        """
        인덱스로 상세 정보를 검색합니다.
        
        Args:
            event_idx (int): 이벤트 인덱스
            status (str): 상태 ('normal' 또는 'abnormal')
            prompt_idx (int): 프롬프트 인덱스
            
        Returns:
            Dict[str, Any]: 해당 위치의 상세 정보를 담은 딕셔너리
            
        Raises:
            IndexError: 잘못된 인덱스가 제공된 경우
            KeyError: 필요한 설정 키가 누락된 경우
        """
        event_config = self.config['PROMPT_CFG'][event_idx]
        prompt = event_config['prompts'][status][prompt_idx]
        
        return {
            'event': event_config['event'],
            'status': status,
            'sentence': prompt['sentence'],
            'top_candidates': event_config['top_candidates'],
            'alert_threshold': event_config['alert_threshold'],
            'event_idx': event_idx,
            'prompt_idx': prompt_idx
        }
    
    def get_all_sentences(self) -> List[str]:
        """
        모든 프롬프트 문장 리스트를 반환합니다.
        
        Returns:
            List[str]: 설정에 포함된 모든 프롬프트 문장 리스트
            
        """
        return self.sentences
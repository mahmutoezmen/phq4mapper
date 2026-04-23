import json
from pathlib import Path

class PHQ4Mapper:
    """Map EDC answers to openEHR node values"""
    
    def __init__(self, config_path: str = "config/mapping_config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.fields = self.config['fields']
    
    def map_answer(self, field_id: str, answer_text: str) -> dict:
        """Map a single EDC answer to openEHR format"""
        
        if field_id not in self.fields:
            raise ValueError(f"Unknown field: {field_id}")
        
        field_config = self.fields[field_id]
        answers = field_config['answers']
        
        # Clean answer text
        answer_text = answer_text.strip()
        
        if answer_text not in answers:
            raise ValueError(
                f"Unknown answer '{answer_text}' for field '{field_id}'. "
                f"Valid answers: {list(answers.keys())}"
            )
        
        answer_data = answers[answer_text]
        
        return {
            "archetype_node_id": field_config['archetype_node_id'],
            "type": field_config['type'],
            "value": answer_data['value'],
            "code": answer_data['code'],
            "text": answer_text
        }
    
    def map_record(self, edc_record: dict) -> dict:
        """Map a full EDC record to openEHR mapped values"""
        
        mapped = {}
        phq_fields = ['phq5a', 'phq5b', 'phq2a', 'phq2b']
        
        for field in phq_fields:
            if field in edc_record:
                mapped[field] = self.map_answer(field, edc_record[field])
        
        # Calculate scores
        mapped['total_score'] = self._calculate_total(mapped)
        mapped['depression_score'] = self._calculate_depression(mapped)
        mapped['anxiety_score'] = self._calculate_anxiety(mapped)
        mapped['interpretation'] = self._interpret_score(mapped['total_score'])
        
        return mapped
    
    def _calculate_total(self, mapped: dict) -> int:
        total = 0
        for field in ['phq5a', 'phq5b', 'phq2a', 'phq2b']:
            if field in mapped:
                total += mapped[field]['value']
        return total
    
    def _calculate_depression(self, mapped: dict) -> int:
        """PHQ-2: first two questions"""
        score = 0
        for field in ['phq5a', 'phq5b']:
            if field in mapped:
                score += mapped[field]['value']
        return score
    
    def _calculate_anxiety(self, mapped: dict) -> int:
        """GAD-2: last two questions"""
        score = 0
        for field in ['phq2a', 'phq2b']:
            if field in mapped:
                score += mapped[field]['value']
        return score
    
    def _interpret_score(self, score: int) -> str:
        if score <= 2:
            return "Normal (0-2)"
        elif score <= 5:
            return "Mild (3-5)"
        elif score <= 8:
            return "Moderat (6-8)"
        else:
            return "Schwer (9-12)"

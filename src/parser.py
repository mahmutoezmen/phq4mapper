import csv
import json
from pathlib import Path

class EDCParser:
    """Parse EDC output into structured format"""
    
    def parse_csv(self, filepath: str) -> list[dict]:
        """
        Parse CSV output from EDC tool
        Expected format:
        patient_id, date, phq5a, phq5b, phq2a, phq2b
        """
        records = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        return records

    def parse_flat(self, raw_text: str) -> dict:
        """
        Parse flat text output like your example:
        phq5a An einzelnen Tagen
        phq5b An mehr als der Hälfte der Tage
        """
        result = {}
        for line in raw_text.strip().split('\n'):
            parts = line.strip().split(' ', 1)
            if len(parts) == 2:
                field_id = parts[0].strip()
                answer = parts[1].strip()
                result[field_id] = answer
        return result

    def parse_json(self, filepath: str) -> list[dict]:
        """Parse JSON output from EDC tool"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

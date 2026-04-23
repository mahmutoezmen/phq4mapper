from datetime import datetime, timezone

class OpenEHRComposer:
    """Build openEHR composition from mapped PHQ-4 data"""
    
    def __init__(self, config: dict):
        self.config = config
    
    def build_composition(
        self,
        mapped_data: dict,
        patient_id: str,
        event_time: str = None
    ) -> dict:
        """Build complete openEHR composition"""
        
        if not event_time:
            event_time = datetime.now(timezone.utc).isoformat()
        
        composition = {
            "_type": "COMPOSITION",
            "archetype_node_id": "openEHR-EHR-COMPOSITION.encounter.v1",
            "name": {"value": "PHQ-4 Assessment"},
            "uid": {"_type": "OBJECT_VERSION_ID"},
            "language": {
                "terminology_id": {"value": "ISO_639-1"},
                "code_string": "de"
            },
            "territory": {
                "terminology_id": {"value": "ISO_3166-1"},
                "code_string": "DE"
            },
            "category": {
                "value": "event",
                "defining_code": {
                    "terminology_id": {"value": "openehr"},
                    "code_string": "433"
                }
            },
            "composer": {"_type": "PARTY_IDENTIFIED", "name": "System"},
            "context": {
                "_type": "EVENT_CONTEXT",
                "start_time": {"value": event_time},
                "setting": {
                    "value": "other care",
                    "defining_code": {
                        "terminology_id": {"value": "openehr"},
                        "code_string": "238"
                    }
                }
            },
            "content": [
                self._build_observation(mapped_data, event_time)
            ]
        }
        
        return composition
    
    def _build_observation(self, mapped_data: dict, event_time: str) -> dict:
        """Build the PHQ-4 OBSERVATION section"""
        
        items = []
        
        # Map each PHQ-4 question
        question_map = {
            'phq5a': "Wenig Interesse oder Freude an Ihren Tätigkeiten",
            'phq5b': "Niedergeschlagenheit, Schwermut oder Hoffnungslosigkeit",
            'phq2a': "Nervosität, Ängstlichkeit oder Anspannung",
            'phq2b': "Nicht in der Lage sein, Sorgen zu stoppen oder zu kontrollieren"
        }
        
        for field_id, question_text in question_map.items():
            if field_id in mapped_data:
                field_data = mapped_data[field_id]
                items.append(
                    self._build_ordinal_element(
                        archetype_node_id=field_data['archetype_node_id'],
                        name=question_text,
                        ordinal_value=field_data['value'],
                        code=field_data['code'],
                        text=field_data['text']
                    )
                )
        
        # Add total score
        items.append(
            self._build_count_element(
                archetype_node_id="at0027",
                name="Bewertung der Patientengesundheit",
                count_value=mapped_data['total_score']
            )
        )
        
        return {
            "_type": "OBSERVATION",
            "archetype_node_id": "openEHR-EHR-OBSERVATION.phq4.v1",
            "name": {
                "value": "Patientengesundheit (PHQ-4) Angst und Depression"
            },
            "language": {
                "terminology_id": {"value": "ISO_639-1"},
                "code_string": "de"
            },
            "encoding": {
                "terminology_id": {"value": "IANA_character-sets"},
                "code_string": "UTF-8"
            },
            "subject": {"_type": "PARTY_SELF"},
            "data": {
                "_type": "HISTORY",
                "archetype_node_id": "at0001",
                "name": {"value": "History"},
                "origin": {"value": event_time},
                "events": [
                    {
                        "_type": "POINT_EVENT",
                        "archetype_node_id": "at0002",
                        "name": {"value": "Any event"},
                        "time": {"value": event_time},
                        "data": {
                            "_type": "ITEM_TREE",
                            "archetype_node_id": "at0003",
                            "name": {"value": "Tree"},
                            "items": items
                        }
                    }
                ]
            }
        }
    
    def _build_ordinal_element(
        self,
        archetype_node_id: str,
        name: str,
        ordinal_value: int,
        code: str,
        text: str
    ) -> dict:
        return {
            "_type": "ELEMENT",
            "archetype_node_id": archetype_node_id,
            "name": {"value": name},
            "value": {
                "_type": "DV_ORDINAL",
                "value": ordinal_value,
                "symbol": {
                    "_type": "DV_CODED_TEXT",
                    "value": text,
                    "defining_code": {
                        "terminology_id": {"value": "local"},
                        "code_string": code
                    }
                }
            }
        }
    
    def _build_count_element(
        self,
        archetype_node_id: str,
        name: str,
        count_value: int
    ) -> dict:
        return {
            "_type": "ELEMENT",
            "archetype_node_id": archetype_node_id,
            "name": {"value": name},
            "value": {
                "_type": "DV_COUNT",
                "magnitude": count_value
            }
        }

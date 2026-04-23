import json
import logging
from src.parser import EDCParser
from src.mapper import PHQ4Mapper
from src.composer import OpenEHRComposer
from src.uploader import OpenEHRUploader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ─── Configuration ────────────────────────────────────────────
OPENEHR_SERVER = "http://localhost:8080/ehrbase/rest/openehr/v1"
OPENEHR_USER   = "ehrbase-user"
OPENEHR_PASS   = "SuperSecretPassword1!"

def process_single_record(raw_text: str, patient_id: str):
    """Process a single EDC record end-to-end"""
    
    # 1. Parse EDC output
    logger.info("Step 1: Parsing EDC output...")
    parser = EDCParser()
    edc_record = parser.parse_flat(raw_text)
    logger.info(f"Parsed record: {edc_record}")
    
    # 2. Map to openEHR values
    logger.info("Step 2: Mapping to openEHR values...")
    mapper = PHQ4Mapper("config/mapping_config.json")
    mapped_data = mapper.map_record(edc_record)
    
    logger.info(f"Total Score:      {mapped_data['total_score']}")
    logger.info(f"Depression Score: {mapped_data['depression_score']}")
    logger.info(f"Anxiety Score:    {mapped_data['anxiety_score']}")
    logger.info(f"Interpretation:   {mapped_data['interpretation']}")
    
    # 3. Build openEHR composition
    logger.info("Step 3: Building composition...")
    with open("config/mapping_config.json") as f:
        config = json.load(f)
    
    composer = OpenEHRComposer(config)
    composition = composer.build_composition(mapped_data, patient_id)
    
    # Save composition locally
    with open(f"output/composition_{patient_id}.json", 'w', encoding='utf-8') as f:
        json.dump(composition, f, indent=2, ensure_ascii=False)
    logger.info(f"Composition saved to output/composition_{patient_id}.json")
    
    # 4. Upload to openEHR server
    logger.info("Step 4: Uploading to EHRbase...")
    uploader = OpenEHRUploader(OPENEHR_SERVER, OPENEHR_USER, OPENEHR_PASS)
    ehr_id = uploader.get_or_create_ehr(patient_id)
    composition_id = uploader.upload_composition(ehr_id, composition)
    logger.info(f"✅ Successfully uploaded! Composition ID: {composition_id}")
    
    return composition_id


def process_csv_batch(csv_filepath: str):
    """Process multiple records from CSV file"""
    
    parser = EDCParser()
    records = parser.parse_csv(csv_filepath)
    
    results = []
    for record in records:
        patient_id = record.get('patient_id', 'unknown')
        try:
            comp_id = process_single_record(record, patient_id)
            results.append({"patient_id": patient_id, "status": "success", "id": comp_id})
        except Exception as e:
            logger.error(f"Failed for patient {patient_id}: {e}")
            results.append({"patient_id": patient_id, "status": "failed", "error": str(e)})
    
    return results


# ─── Run ──────────────────────────────────────────────────────
if __name__ == "__main__":
    
    # Your example input
    raw_edc_output = """
    phq5a An einzelnen Tagen
    phq5b An mehr als der Hälfte der Tage
    phq2a An mehr als der Hälfte der Tage
    phq2b An mehr als der Hälfte der Tage
    """
    
    process_single_record(raw_edc_output, patient_id="patient_001")

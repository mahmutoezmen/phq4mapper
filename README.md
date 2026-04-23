EDC Raw Text
     │
     ▼
[parser.py]  →  {"phq5a": "An einzelnen Tagen", ...}
     │
     ▼
[mapper.py]  →  {"phq5a": {value: 1, code: "at0007"}, total: 7}
     │
     ▼
[composer.py] → Full openEHR JSON Composition
     │
     ▼
[uploader.py] → POST to EHRbase → Composition ID

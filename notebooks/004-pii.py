import marimo

__generated_with = "0.18.0"
app = marimo.App(width="medium", sql_output="polars")

with app.setup:
    # Initialization code that runs before all other cells
    import marimo as mo
    import re
    from enum import Enum


@app.cell
def _():
    class PIIEntity(Enum):
        # Global
        CREDIT_CARD = 'CREDIT_CARD'
        CRYPTO = 'CRYPTO'
        DATE_TIME = 'DATE_TIME'
        EMAIL_ADDRESS = 'EMAIL_ADDRESS'
        IBAN_CODE = 'IBAN_CODE'
        IP_ADDRESS = 'IP_ADDRESS'
        LOCATION = 'LOCATION'
        PHONE_NUMBER = 'PHONE_NUMBER'
        MEDICAL_LICENSE = 'MEDICAL_LICENSE'

        # USA
        US_BANK_NUMBER = 'US_BANK_NUMBER'
        US_DRIVER_LICENSE = 'US_DRIVER_LICENSE'
        US_ITIN = 'US_ITIN'
        US_PASSPORT = 'US_PASSPORT'
        US_SSN = 'US_SSN'

        # UK
        UK_NHS = 'UK_NHS'
        UK_NINO = 'UK_NINO'

        # Spain
        ES_NIF = 'ES_NIF'
        ES_NIE = 'ES_NIE'

        # Italy
        IT_FISCAL_CODE = 'IT_FISCAL_CODE'
        IT_DRIVER_LICENSE = 'IT_DRIVER_LICENSE'
        IT_VAT_CODE = 'IT_VAT_CODE'
        IT_PASSPORT = 'IT_PASSPORT'
        IT_IDENTITY_CARD = 'IT_IDENTITY_CARD'

        # Poland
        PL_PESEL = 'PL_PESEL'

        # Singapore
        SG_NRIC_FIN = 'SG_NRIC_FIN'
        SG_UEN = 'SG_UEN'

        # Australia
        AU_ABN = 'AU_ABN'
        AU_ACN = 'AU_ACN'
        AU_TFN = 'AU_TFN'
        AU_MEDICARE = 'AU_MEDICARE'

        # India
        IN_PAN = 'IN_PAN'
        IN_AADHAAR = 'IN_AADHAAR'
        IN_VEHICLE_REGISTRATION = 'IN_VEHICLE_REGISTRATION'
        IN_VOTER = 'IN_VOTER'
        IN_PASSPORT = 'IN_PASSPORT'

        # Finland
        FI_PERSONAL_IDENTITY_CODE = 'FI_PERSONAL_IDENTITY_CODE'


    PII_NAME_MAP = {
        PIIEntity.CREDIT_CARD: 'Credit Card',
        PIIEntity.CRYPTO: 'Crypto',
        PIIEntity.DATE_TIME: 'Date Time',
        PIIEntity.EMAIL_ADDRESS: 'Email Address',
        PIIEntity.IBAN_CODE: 'IBAN Code',
        PIIEntity.IP_ADDRESS: 'IP Address',
        PIIEntity.LOCATION: 'Location',
        PIIEntity.PHONE_NUMBER: 'Phone Number',
        PIIEntity.MEDICAL_LICENSE: 'Medical License',
        PIIEntity.US_BANK_NUMBER: 'US Bank Number',
        PIIEntity.US_DRIVER_LICENSE: 'US Driver License',
        PIIEntity.US_ITIN: 'US ITIN',
        PIIEntity.US_PASSPORT: 'US Passport',
        PIIEntity.US_SSN: 'US SSN',
        PIIEntity.UK_NHS: 'UK NHS',
        PIIEntity.UK_NINO: 'UK NINO',
        PIIEntity.ES_NIF: 'ES NIF',
        PIIEntity.ES_NIE: 'ES NIE',
        PIIEntity.IT_FISCAL_CODE: 'IT Fiscal Code',
        PIIEntity.IT_DRIVER_LICENSE: 'IT Driver License',
        PIIEntity.IT_VAT_CODE: 'IT VAT Code',
        PIIEntity.IT_PASSPORT: 'IT Passport',
        PIIEntity.IT_IDENTITY_CARD: 'IT Identity Card',
        PIIEntity.PL_PESEL: 'PL PESEL',
        PIIEntity.SG_NRIC_FIN: 'SG NRIC FIN',
        PIIEntity.SG_UEN: 'SG UEN',
        PIIEntity.AU_ABN: 'AU ABN',
        PIIEntity.AU_ACN: 'AU ACN',
        PIIEntity.AU_TFN: 'AU TFN',
        PIIEntity.AU_MEDICARE: 'AU Medicare',
        PIIEntity.IN_PAN: 'IN PAN',
        PIIEntity.IN_AADHAAR: 'IN AADHAAR',
        PIIEntity.IN_VEHICLE_REGISTRATION: 'IN Vehicle Registration',
        PIIEntity.IN_VOTER: 'IN Voter',
        PIIEntity.IN_PASSPORT: 'IN Passport',
        PIIEntity.FI_PERSONAL_IDENTITY_CODE: 'FI Personal Identity Code',
    }


    DEFAULT_PII_PATTERNS = {
        PIIEntity.CREDIT_CARD: re.compile(r'\b\d{4}[\-\s]?\d{4}[\-\s]?\d{4}[\-\s]?\d{4}\b'),
        PIIEntity.CRYPTO: re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'),
        PIIEntity.DATE_TIME: re.compile(r'\b(0[1-9]|1[0-2])[\-\/](0[1-9]|[12]\d|3[01])[\-\/](19|20)\d{2}\b'),
        PIIEntity.EMAIL_ADDRESS: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        PIIEntity.IBAN_CODE: re.compile(r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b'),
        PIIEntity.IP_ADDRESS: re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
        PIIEntity.LOCATION: re.compile(r'\b[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Place|Pl|Court|Ct|Way|Highway|Hwy)\b'),
        PIIEntity.PHONE_NUMBER: re.compile(r'\b[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}\b'),
        PIIEntity.MEDICAL_LICENSE: re.compile(r'\b[A-Z]{2}\d{6}\b'),

        # USA
        PIIEntity.US_BANK_NUMBER: re.compile(r'\b\d{8,17}\b'),
        PIIEntity.US_DRIVER_LICENSE: re.compile(r'\b[A-Z]\d{7}\b'),
        PIIEntity.US_ITIN: re.compile(r'\b9\d{2}-\d{2}-\d{4}\b'),
        PIIEntity.US_PASSPORT: re.compile(r'\b[A-Z]\d{8}\b'),
        PIIEntity.US_SSN: re.compile(r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'),

        # UK
        PIIEntity.UK_NHS: re.compile(r'\b\d{3} \d{3} \d{4}\b'),
        PIIEntity.UK_NINO: re.compile(r'\b[A-Z]{2}\d{6}[A-Z]\b'),

        # Spain
        PIIEntity.ES_NIF: re.compile(r'\b[A-Z]\d{8}\b'),
        PIIEntity.ES_NIE: re.compile(r'\b[A-Z]\d{8}\b'),

        # Italy
        PIIEntity.IT_FISCAL_CODE: re.compile(r'\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b'),
        PIIEntity.IT_DRIVER_LICENSE: re.compile(r'\b[A-Z]{2}\d{7}\b'),
        PIIEntity.IT_VAT_CODE: re.compile(r'\bIT\d{11}\b'),
        PIIEntity.IT_PASSPORT: re.compile(r'\b[A-Z]{2}\d{7}\b'),
        PIIEntity.IT_IDENTITY_CARD: re.compile(r'\b[A-Z]{2}\d{7}\b'),

        # Poland
        PIIEntity.PL_PESEL: re.compile(r'\b\d{11}\b'),

        # Singapore
        PIIEntity.SG_NRIC_FIN: re.compile(r'\b[A-Z]\d{7}[A-Z]\b'),
        PIIEntity.SG_UEN: re.compile(r'\b\d{8}[A-Z]\b|\b\d{9}[A-Z]\b'),

        # Australia
        PIIEntity.AU_ABN: re.compile(r'\b\d{2} \d{3} \d{3} \d{3}\b'),
        PIIEntity.AU_ACN: re.compile(r'\b\d{3} \d{3} \d{3}\b'),
        PIIEntity.AU_TFN: re.compile(r'\b\d{9}\b'),
        PIIEntity.AU_MEDICARE: re.compile(r'\b\d{4} \d{5} \d{1}\b'),

        # India
        PIIEntity.IN_PAN: re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b'),
        PIIEntity.IN_AADHAAR: re.compile(r'\b\d{4} \d{4} \d{4}\b'),
        PIIEntity.IN_VEHICLE_REGISTRATION: re.compile(r'\b[A-Z]{2}\d{2}[A-Z]{2}\d{4}\b'),
        PIIEntity.IN_VOTER: re.compile(r'\b[A-Z]{3}\d{7}\b'),
        PIIEntity.IN_PASSPORT: re.compile(r'\b[A-Z]\d{7}\b'),

        # Finland
        PIIEntity.FI_PERSONAL_IDENTITY_CODE: re.compile(r'\b\d{6}[+\-A]\d{3}[A-Z0-9]\b'),
    }
    return DEFAULT_PII_PATTERNS, PIIEntity, PII_NAME_MAP


@app.cell
def _(DEFAULT_PII_PATTERNS, PIIEntity):
    def detect_pii(text, entities=None):
        if not text:
            return {'mapping': {}, 'analyzer_results': []}

        grouped = {}
        analyzer_results = []

        def match_against_pattern(entity_name, pattern):
            for match in pattern.finditer(text):
                start = match.start()
                end = match.end()
                entity_type = entity_name.value

                if entity_type not in grouped:
                    grouped[entity_type] = []
                grouped[entity_type].append(text[start:end])

                analyzer_results.append({
                    'entity_type': entity_type,
                    'text': text[start:end]
                })

        if entities is None:
            entities = list(PIIEntity)

        for entity in entities:
            pattern = DEFAULT_PII_PATTERNS[entity]
            match_against_pattern(entity, pattern)

        return {
            'mapping': grouped,
            'analyzer_results': analyzer_results
        }
    return (detect_pii,)


@app.cell
def c_input():
    user_input = mo.ui.text_area().form()
    user_input
    return (user_input,)


@app.cell
def c_pii_check(PIIEntity, PII_NAME_MAP, detect_pii, user_input):
    if user_input.value:
        result = detect_pii(user_input.value)
        pii_found = bool(result['mapping'])

        if pii_found:
            entities_found = []
            for entity_type, matches in result['mapping'].items():
                entity_name = PII_NAME_MAP[PIIEntity(entity_type)]
                entities_found.append(f"{entity_name}: {', '.join(matches)}")

            result_md = """
            ### PII Detected
            The input contains potentially sensitive information:

            """ + '\n'.join(f"- {entity}" for entity in entities_found)
        else:
            result_md = "### No PII Detected\nThe input appears to be free of sensitive information."
    return (result_md,)


@app.cell
def _(result_md):
    mo.md(rf"""
    { result_md }
    """)
    return


if __name__ == "__main__":
    app.run()

import re

class PlateNormalizer:
    @staticmethod
    def normalize(raw_text: str) -> str:
        """
        Normalize plate text:
        - Convert to uppercase
        - Remove whitespace and non-alphanumeric characters
        """
        if not raw_text:
            return ""
        
        # Convert to upper case
        text = raw_text.upper()
        
        # Remove anything that isn't a letter or number
        text = re.sub(r'[^A-Z0-9]', '', text)
        
        return text

    @staticmethod
    def is_valid_format(normalized_text: str) -> bool:
        """
        Check if the normalized text looks like a valid license plate.
        For this prototype, we assume plates are 4 to 8 alphanumeric characters.
        """
        if not normalized_text:
            return False
            
        length = len(normalized_text)
        if 4 <= length <= 8:
            # We can add more specific regex patterns here if needed,
            # e.g., Indian plates format: ^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$
            # but for a generic prototype, length filter is enough.
            return True
            
        return False

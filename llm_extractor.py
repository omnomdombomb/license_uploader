"""
LLM-based license term extraction using LiteLLM
"""
import json
from pathlib import Path
import openai
from config import Config
from license_terms_data import LICENSE_TERMS, TERM_TYPE_VALUES


class LLMExtractor:
    """Extract license terms from text using LLM"""

    # Maximum characters to send to LLM (configurable)
    MAX_DOCUMENT_LENGTH = 15000

    # Path to custom prompt file
    CUSTOM_PROMPT_FILE = 'custom_prompt.txt'

    # Path to custom term descriptions file
    CUSTOM_DESCRIPTIONS_FILE = 'custom_term_descriptions.json'

    def __init__(self, api_key=None, base_url=None, model=None):
        """Initialize OpenAI client with LiteLLM proxy

        Args:
            api_key: Optional custom API key (defaults to Config.LITELLM_API_KEY)
            base_url: Optional custom base URL (defaults to Config.LITELLM_BASE_URL)
            model: Optional custom model (defaults to Config.LITELLM_MODEL)

        Raises:
            ValueError: If API key is missing or invalid
        """
        import httpx

        # Use provided api_key if not None, otherwise fall back to config
        effective_api_key = api_key if api_key is not None else Config.LITELLM_API_KEY
        effective_base_url = base_url if base_url is not None else Config.LITELLM_BASE_URL
        effective_model = model if model is not None else Config.LITELLM_MODEL

        # Validate API key
        if not effective_api_key or not isinstance(effective_api_key, str) or len(effective_api_key.strip()) < 10:
            raise ValueError(
                "LITELLM_API_KEY is required and must be a valid API key (minimum 10 characters). "
                "Please set LITELLM_API_KEY in your .env file."
            )

        # Create httpx client without proxy
        self.http_client = httpx.Client(
            verify=True,
            timeout=180.0
        )

        self.client = openai.OpenAI(
            api_key=effective_api_key,
            base_url=effective_base_url,
            http_client=self.http_client
        )
        self.model = effective_model

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup"""
        self.close()
        return False

    def close(self):
        """Close the HTTP client and release resources"""
        if hasattr(self, 'http_client') and self.http_client:
            try:
                self.http_client.close()
            except Exception:
                pass  # Ignore errors during cleanup

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()

    @staticmethod
    def load_custom_prompt():
        """
        Load custom prompt from file if it exists
        Returns None if file doesn't exist or is empty
        """
        prompt_file = Path(LLMExtractor.CUSTOM_PROMPT_FILE)
        if prompt_file.exists():
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    return content if content else None
            except Exception:
                return None
        return None

    @staticmethod
    def save_custom_prompt(prompt_text):
        """
        Save custom prompt to file

        Args:
            prompt_text: The prompt template to save
        """
        with open(LLMExtractor.CUSTOM_PROMPT_FILE, 'w', encoding='utf-8', newline='\n') as f:
            f.write(prompt_text)

    @staticmethod
    def get_default_prompt_template():
        """
        Get the default prompt template (without document text)
        This is used for displaying in the UI
        """
        # FEATURE DISABLED: Citation tracking is commented out for now
        # Original prompt included citation requirements - now simplified
        return """Analyze the following license agreement and extract all relevant license terms.

LICENSE TERMS TO EXTRACT:
{terms_description}

INSTRUCTIONS:
1. For each term, determine if it is mentioned in the document
2. If mentioned, extract the relevant value or text
3. For terms with predefined values (Yes/No, Permitted/Prohibited, etc.), use EXACTLY those values
4. For FREE-TEXT terms, extract the relevant text from the document
5. If a term is NOT mentioned or cannot be determined, set the value to null
6. Be thorough but precise - avoid false positives
7. For Permitted/Prohibited terms, look for explicit language about permissions or restrictions
{truncation_note}
DOCUMENT TEXT:
{document_text}

OUTPUT FORMAT:
Return a JSON object where each key is a term code and the value is the extracted value or null.

Example:
{{
  "ARCHIVE": "Permitted (Explicit)",
  "FAIRUSE": "Yes",
  "GOVJUR": "State of New York",
  "DIGCOPY": null
}}

Return ONLY valid JSON, no additional text."""

    @staticmethod
    def load_custom_descriptions():
        """Load custom term descriptions from JSON file.
        Returns dict of {term_code: custom_description} or empty dict."""
        desc_file = Path(LLMExtractor.CUSTOM_DESCRIPTIONS_FILE)
        if desc_file.exists():
            try:
                with open(desc_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else {}
            except Exception:
                return {}
        return {}

    @staticmethod
    def save_custom_descriptions(descriptions):
        """Save custom term descriptions to JSON file."""
        with open(LLMExtractor.CUSTOM_DESCRIPTIONS_FILE, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(descriptions, f, indent=2, ensure_ascii=False)

    @staticmethod
    def get_effective_descriptions():
        """Return all term descriptions, merging defaults with custom overrides."""
        custom = LLMExtractor.load_custom_descriptions()
        result = []
        for term in LICENSE_TERMS:
            is_custom = term['code'] in custom
            result.append({
                'code': term['code'],
                'name': term['name'],
                'description': custom.get(term['code'], term['description']),
                'default_description': term['description'],
                'type': term['type'],
                'is_custom': is_custom
            })
        return result

    def extract_license_terms(self, document_text, document_parser=None):
        """
        Extract license terms from document text

        FEATURE DISABLED: Citation validation is currently disabled.

        Args:
            document_text: Full text of the license document
            document_parser: Optional DocumentParser instance (currently unused)

        Returns:
            Dictionary with 'terms' and optional 'truncation_warning' keys
        """
        # Check if document will be truncated
        was_truncated = len(document_text) > self.MAX_DOCUMENT_LENGTH

        # Create extraction prompt
        prompt = self._create_extraction_prompt(document_text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing license agreements and extracting specific license terms. You provide responses in valid JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                response_format={"type": "json_object"}
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)
            formatted_terms = self._validate_and_format_terms(result, document_parser)

            # Return terms with truncation warning if applicable
            response_data = {'terms': formatted_terms}
            if was_truncated:
                response_data['truncation_warning'] = {
                    'truncated': True,
                    'original_length': len(document_text),
                    'analyzed_length': self.MAX_DOCUMENT_LENGTH,
                    'message': f'Document was truncated from {len(document_text)} to {self.MAX_DOCUMENT_LENGTH} characters. Some terms in later sections may have been missed.'
                }

            return response_data

        except Exception as e:
            # Check for timeout-specific errors
            import httpx
            if isinstance(e, (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout)):
                raise Exception("AI service took too long to respond (timeout after 180 seconds). Please try again or contact support if the issue persists.")
            raise Exception(f"Error extracting terms with LLM: {str(e)}")

    def _create_extraction_prompt(self, document_text):
        """Create detailed extraction prompt using custom template if available"""

        # Load custom descriptions (if any)
        custom_descriptions = self.load_custom_descriptions()

        # Build term descriptions
        terms_description = []
        for term in LICENSE_TERMS:
            description = custom_descriptions.get(term['code'], term['description'])
            term_info = f"- {term['code']}: {term['name']} - {description}"
            if term['type'] != 'FREE-TEXT':
                values = TERM_TYPE_VALUES.get(term['type'], [])
                term_info += f" (Valid values: {', '.join(values)})"
            terms_description.append(term_info)

        # Check if truncation will occur and add warning
        truncation_note = ""
        if len(document_text) > self.MAX_DOCUMENT_LENGTH:
            truncation_note = f"\n⚠️ NOTE: This document is {len(document_text)} characters but only the first {self.MAX_DOCUMENT_LENGTH} characters are shown below. Important terms may appear in the truncated section.\n"

        # Try to load custom prompt, fallback to default
        custom_prompt = self.load_custom_prompt()

        if custom_prompt:
            # Use custom prompt template with variable substitution
            prompt = custom_prompt.format(
                terms_description=chr(10).join(terms_description),
                truncation_note=truncation_note,
                document_text=document_text[:self.MAX_DOCUMENT_LENGTH]
            )
        else:
            # Use default prompt
            prompt = self.get_default_prompt_template().format(
                terms_description=chr(10).join(terms_description),
                truncation_note=truncation_note,
                document_text=document_text[:self.MAX_DOCUMENT_LENGTH]
            )

        return prompt

    def _fuzzy_match_value(self, extracted_value, allowed_values):
        """
        Attempt fuzzy matching of extracted value against allowed values
        Returns best match if confidence is high enough, otherwise None
        """
        if not extracted_value or not allowed_values:
            return None

        # Normalize extracted value for comparison
        normalized_extracted = extracted_value.lower().strip()

        # Try exact match (case-insensitive)
        for allowed in allowed_values:
            if normalized_extracted == allowed.lower():
                return allowed

        # Try partial match (extracted value contains or is contained in allowed value)
        for allowed in allowed_values:
            normalized_allowed = allowed.lower()
            if normalized_extracted in normalized_allowed or normalized_allowed in normalized_extracted:
                # Check similarity threshold (at least 50% overlap)
                overlap = min(len(normalized_extracted), len(normalized_allowed))
                max_len = max(len(normalized_extracted), len(normalized_allowed))
                if overlap / max_len >= 0.5:
                    return allowed

        # Try common synonyms and variations
        synonyms = {
            'allowed': 'Permitted',
            'permitted': 'Permitted',
            'yes': 'Yes',
            'true': 'Yes',
            'no': 'No',
            'false': 'No',
            'prohibited': 'Prohibited',
            'forbidden': 'Prohibited',
            'not allowed': 'Prohibited',
            'explicit': 'Explicit',
            'silent': 'Silent',
            'interpreted': 'Interpreted'
        }

        for synonym, standard in synonyms.items():
            if synonym in normalized_extracted and standard in allowed_values:
                return standard

        return None

    def _validate_and_format_terms(self, extracted_terms, document_parser=None):
        """Validate and format extracted terms with fuzzy matching"""
        # FEATURE DISABLED: Citation validation and source location tracking commented out
        formatted = {}

        for term in LICENSE_TERMS:
            code = term['code']
            extracted_data = extracted_terms.get(code)

            # Handle both old format (string) and new format (object with value/citation)
            if isinstance(extracted_data, dict):
                extracted_value = extracted_data.get('value')
                # citation = extracted_data.get('citation')  # DISABLED: Citation tracking
            else:
                # Backward compatibility - old format was just the value
                extracted_value = extracted_data
                # citation = None  # DISABLED: Citation tracking

            # If null or not present, keep as null
            if extracted_value is None or extracted_value == "":
                formatted[code] = {
                    'value': None,
                    'type': term['type'],
                    'name': term['name'],
                    'description': term['description'],
                    # DISABLED: Citation and source location fields
                    # 'citation': None,
                    # 'source_location': None
                }
                continue

            # Validate against allowed values
            if term['type'] != 'FREE-TEXT':
                allowed_values = TERM_TYPE_VALUES.get(term['type'], [])
                if extracted_value not in allowed_values:
                    # Try fuzzy matching before discarding
                    matched_value = self._fuzzy_match_value(extracted_value, allowed_values)
                    if matched_value:
                        extracted_value = matched_value
                    else:
                        # No good match found, set to null
                        extracted_value = None
                        # citation = None  # DISABLED: Citation tracking

            # DISABLED: Citation validation and source location tracking
            # source_location = None
            # citation_verified = False
            #
            # if citation and document_parser:
            #     # Try to find the citation in the document
            #     location = document_parser.find_text_in_document(citation)
            #     if location:
            #         source_location = location
            #         citation_verified = not location.get('fuzzy_matched', False)
            #         # Use the matched text from the document as the verified citation
            #         if citation_verified:
            #             citation = location['matched_text']

            formatted[code] = {
                'value': extracted_value,
                'type': term['type'],
                'name': term['name'],
                'description': term['description'],
                # DISABLED: Citation and source location fields
                # 'citation': citation,
                # 'source_location': source_location,
                # 'citation_verified': citation_verified if citation else None
            }

        return formatted

    def refine_term(self, document_text, term_code, current_value):
        """
        Refine a specific term extraction

        Args:
            document_text: Full document text
            term_code: Term code to refine
            current_value: Current extracted value

        Returns:
            Refined value
        """
        term = next((t for t in LICENSE_TERMS if t['code'] == term_code), None)
        if not term:
            return current_value

        # Use custom description if available
        custom_descriptions = self.load_custom_descriptions()
        description = custom_descriptions.get(term_code, term['description'])

        prompt = f"""Focus on extracting this specific license term from the document:

TERM: {term['name']} ({term['code']})
DESCRIPTION: {description}
CURRENT VALUE: {current_value if current_value else 'Not extracted'}

"""

        if term['type'] != 'FREE-TEXT':
            values = TERM_TYPE_VALUES.get(term['type'], [])
            prompt += f"VALID VALUES: {', '.join(values)}\n\n"

        prompt += f"""DOCUMENT TEXT:
{document_text[:10000]}

Extract ONLY this specific term. Return a JSON object with a single key "value" containing the extracted value or null.
Example: {{"value": "Permitted (Explicit)"}} or {{"value": null}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing license agreements. Provide responses in valid JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get('value')

        except Exception as e:
            # Check for timeout-specific errors
            import httpx
            import logging
            logger = logging.getLogger(__name__)
            if isinstance(e, (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout)):
                logger.warning(f"Timeout error refining term: AI service took too long to respond")
            else:
                logger.warning(f"Error refining term: {str(e)}")
            return current_value

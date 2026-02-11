"""
Alma API integration for license management
"""
import requests
import json
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)


class AlmaAPI:
    """Interface for Alma Acquisition/License APIs"""

    def __init__(self, api_key=None, base_url=None):
        """Initialize Alma API client

        Args:
            api_key: Optional custom API key (defaults to Config.ALMA_API_KEY)
            base_url: Optional custom base URL (defaults to Config.ALMA_API_BASE_URL)

        Raises:
            ValueError: If API key is missing or invalid
        """
        # Use provided api_key if not None, otherwise fall back to config
        self.api_key = api_key if api_key is not None else Config.ALMA_API_KEY
        self.base_url = base_url if base_url is not None else Config.ALMA_API_BASE_URL

        # Validate API key
        if not self.api_key or not isinstance(self.api_key, str) or len(self.api_key.strip()) < 10:
            raise ValueError(
                "ALMA_API_KEY is required and must be a valid API key (minimum 10 characters). "
                "Please set ALMA_API_KEY in your .env file."
            )

        self.headers = {
            'Authorization': f'apikey {self.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_vendors(self, limit=100, offset=0):
        """
        Retrieve list of vendors from Alma

        Args:
            limit: Number of results per API call (max 100)
            offset: Starting offset for pagination

        Returns:
            List of all vendors with codes and names
        """
        url = f"{self.base_url}/almaws/v1/acq/vendors"
        all_vendors = []
        current_offset = offset

        try:
            while True:
                params = {
                    'limit': limit,
                    'offset': current_offset,
                    'status': 'active'
                }

                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                data = response.json()

                if 'vendor' in data and len(data['vendor']) > 0:
                    for vendor in data['vendor']:
                        all_vendors.append({
                            'code': vendor.get('code'),
                            'name': vendor.get('name'),
                            'status': vendor.get('status', {}).get('value')
                        })

                    # If we got fewer results than the limit, we've reached the end
                    if len(data['vendor']) < limit:
                        break

                    # Otherwise, increment offset and continue
                    current_offset += limit
                else:
                    # No vendors in response, we're done
                    break

            return all_vendors

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching vendors from Alma: {str(e)}")

    def get_license(self, license_code):
        """
        Get a specific license from Alma

        Args:
            license_code: License code

        Returns:
            License object
        """
        url = f"{self.base_url}/almaws/v1/acq/licenses/{license_code}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching license: {str(e)}")

    def create_license(self, license_data):
        """
        Create a new license in Alma

        Args:
            license_data: License object conforming to Alma schema

        Returns:
            Created license object
        """
        url = f"{self.base_url}/almaws/v1/acq/licenses"

        try:
            # Validate required fields
            self._validate_license_data(license_data)

            logger.debug("="*80)
            logger.debug("Sending POST request to Alma API:")
            logger.debug(f"URL: {url}")
            logger.debug("="*80)

            response = requests.post(
                url,
                headers=self.headers,
                json=license_data
            )

            logger.debug("="*80)
            logger.debug(f"Alma API Response Status: {response.status_code}")
            logger.debug(f"Alma API Response Headers: {dict(response.headers)}")
            logger.debug("Alma API Response Body:")
            logger.debug(response.text)
            logger.debug("="*80)

            response.raise_for_status()

            result = response.json()

            # Check if terms were saved in the response
            if 'term' in result and len(result['term']) > 0:
                logger.debug(f"✅ SUCCESS! Response contains {len(result['term'])} terms")
            elif 'term' in result:
                logger.debug(f"⚠️  WARNING - Response has 'term' field but it's empty: {result['term']}")
            else:
                logger.debug("❌ ERROR - Response does NOT contain 'term' field!")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Error creating license: {str(e)}"
            if hasattr(e.response, 'text'):
                error_msg += f"\nResponse: {e.response.text}"
            raise Exception(error_msg)

    def update_license(self, license_code, license_data):
        """
        Update an existing license in Alma

        Args:
            license_code: License code
            license_data: Updated license object

        Returns:
            Updated license object
        """
        url = f"{self.base_url}/almaws/v1/acq/licenses/{license_code}"

        try:
            response = requests.put(
                url,
                headers=self.headers,
                json=license_data
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error updating license: {str(e)}")

    def _validate_license_data(self, license_data):
        """
        Validate license data before submission

        Args:
            license_data: License object to validate

        Raises:
            ValueError if required fields are missing
        """
        required_fields = ['name', 'code', 'type', 'status']

        for field in required_fields:
            if field not in license_data or not license_data[field]:
                raise ValueError(f"Required field '{field}' is missing")

    def build_license_payload(self, basic_info, extracted_terms):
        """
        Build Alma license payload from basic info and extracted terms

        Args:
            basic_info: Dictionary with name, code, type, status, etc.
            extracted_terms: Dictionary of extracted license terms

        Returns:
            Alma-compliant license object
        """
        # Build terms array
        terms = []

        # Handle None or non-dict extracted_terms
        if extracted_terms and isinstance(extracted_terms, dict):
            for code, term_data in extracted_terms.items():
                # Ensure term_data is a dict with 'value' key
                if isinstance(term_data, dict) and 'value' in term_data:
                    if term_data['value'] is not None and term_data['value'] != '':
                        # Normalize value based on term type
                        value = term_data['value']
                        term_type = term_data.get('type', '')

                        # For Yes/No terms, convert to uppercase YES/NO
                        if term_type == 'LicenseTermsYesNo':
                            if isinstance(value, str):
                                value_lower = value.lower()
                                if value_lower == 'yes':
                                    value = 'YES'
                                elif value_lower == 'no':
                                    value = 'NO'

                        # For Permitted/Prohibited terms, normalize format
                        # e.g., "Permitted (Explicit)" -> "PERMITTED_EXPLICIT"
                        elif term_type == 'LicenseTermsPermittedProhibited':
                            if isinstance(value, str):
                                # Remove parentheses, replace spaces with underscores, uppercase
                                value = value.replace('(', '').replace(')', '').replace(' ', '_').upper()

                        # For Unit of Measure terms, remove spaces and uppercase
                        # e.g., "Calendar Day" -> "CALENDARDAY"
                        elif term_type == 'LicenseTermsUOM':
                            if isinstance(value, str):
                                value = value.replace(' ', '').upper()

                        # For Renewal Type terms, convert to uppercase
                        # e.g., "Explicit" -> "EXPLICIT", "Automatic" -> "AUTOMATIC"
                        elif term_type == 'LicenseTermsRenewalType':
                            if isinstance(value, str):
                                value = value.upper()

                        terms.append({
                            'code': {'value': code},
                            'value': {'value': value}
                        })
                        logger.debug(f"Adding term {code} = {value} (type: {term_type})")
                    else:
                        logger.debug(f"Skipping term {code} - value is None or empty")
                else:
                    logger.debug(f"Skipping term {code} - invalid structure: {term_data}")
        else:
            logger.debug(f"extracted_terms is None or not a dict: {type(extracted_terms)}")

        # Build license object
        license_obj = {
            'code': basic_info.get('code'),
            'name': basic_info.get('name'),
            'type': {
                'value': basic_info.get('type', 'LICENSE')
            },
            'status': {
                'value': basic_info.get('status', 'ACTIVE')
            },
            'review_status': {
                'value': basic_info.get('review_status', 'INREVIEW')
            }
        }

        # Add optional fields
        if basic_info.get('start_date'):
            license_obj['start_date'] = basic_info['start_date']

        if basic_info.get('end_date'):
            license_obj['end_date'] = basic_info['end_date']

        if basic_info.get('vendor_code'):
            license_obj['licensor'] = {
                'value': basic_info['vendor_code']
            }

        # Add terms directly to the license object (not nested in 'terms')
        if terms:
            license_obj['term'] = terms
            logger.debug(f"Added {len(terms)} terms to license payload")
        else:
            logger.debug("No terms added to license payload - terms list is empty")

        return license_obj

    def test_connection(self):
        """
        Test connection to Alma API
        Uses /almaws/v1/acq/vendors endpoint with limit=1 to validate connectivity

        Returns:
            True if connection successful, False otherwise
        """
        # Use a real endpoint to test connection - vendors list with minimal results
        url = f"{self.base_url}/almaws/v1/acq/vendors?limit=1"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return True
        except:
            return False

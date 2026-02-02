"""
Alma API integration for license management
"""
import requests
import json
from datetime import datetime
from config import Config


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
            limit: Number of results to return
            offset: Offset for pagination

        Returns:
            List of vendors with codes and names
        """
        url = f"{self.base_url}/almaws/v1/acq/vendors"
        params = {
            'limit': limit,
            'offset': offset,
            'status': 'active'
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            vendors = []

            if 'vendor' in data:
                for vendor in data['vendor']:
                    vendors.append({
                        'code': vendor.get('code'),
                        'name': vendor.get('name'),
                        'status': vendor.get('status', {}).get('value')
                    })

            return vendors

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

            response = requests.post(
                url,
                headers=self.headers,
                json=license_data
            )
            response.raise_for_status()

            return response.json()

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
        for code, term_data in extracted_terms.items():
            if term_data['value'] is not None:
                terms.append({
                    'code': code,
                    'value': term_data['value']
                })

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

        if terms:
            license_obj['terms'] = {'term': terms}

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

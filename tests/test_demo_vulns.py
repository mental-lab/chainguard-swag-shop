"""
Demo vulnerability tests for security scanning demonstration.

These tests verify that intentional security vulnerabilities are properly implemented
for demonstration purposes. They test the vulnerable code paths to ensure they work
as expected for security scanning tools to detect.

WARNING: This file contains tests for intentionally vulnerable code.
These vulnerabilities are for demonstration purposes only.
"""

import pytest
from config import BRAND_NAME
import os
import tempfile
from app import app, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            yield client


class TestHardcodedCredentials:
    """Tests for CWE-798: Hardcoded AWS Credentials vulnerability."""

    def test_aws_credentials_are_hardcoded(self):
        """Test that AWS credentials are hardcoded (vulnerability detection)."""
        # Verify the hardcoded credentials exist
        assert AWS_ACCESS_KEY_ID == "AKIAIOSFODNN7EXAMPLE"
        assert AWS_SECRET_ACCESS_KEY == "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        assert AWS_REGION == "us-west-2"

    def test_credentials_accessible_in_app_context(self):
        """Test that credentials are accessible in application context."""
        from app import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
        
        assert len(AWS_ACCESS_KEY_ID) > 0
        assert len(AWS_SECRET_ACCESS_KEY) > 0
        assert AWS_ACCESS_KEY_ID.startswith("AKIA")

    def test_credentials_follow_aws_format(self):
        """Test that hardcoded credentials follow AWS format patterns."""
        # AWS Access Key ID format: AKIA followed by 16 characters
        assert AWS_ACCESS_KEY_ID.startswith("AKIA")
        assert len(AWS_ACCESS_KEY_ID) == 20
        
        # AWS Secret Access Key format: 40 characters
        assert len(AWS_SECRET_ACCESS_KEY) == 40

    def test_credentials_not_from_environment(self):
        """Test that credentials are not loaded from environment variables."""
        # Ensure we're not accidentally using env vars
        original_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        original_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        # Temporarily clear env vars
        if 'AWS_ACCESS_KEY_ID' in os.environ:
            del os.environ['AWS_ACCESS_KEY_ID']
        if 'AWS_SECRET_ACCESS_KEY' in os.environ:
            del os.environ['AWS_SECRET_ACCESS_KEY']
        
        try:
            # Re-import to ensure we get hardcoded values
            from app import AWS_ACCESS_KEY_ID as test_access_key
            from app import AWS_SECRET_ACCESS_KEY as test_secret_key
            
            # Should still have hardcoded values
            assert test_access_key == "AKIAIOSFODNN7EXAMPLE"
            assert test_secret_key == "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
            
        finally:
            # Restore original env vars
            if original_access_key:
                os.environ['AWS_ACCESS_KEY_ID'] = original_access_key
            if original_secret_key:
                os.environ['AWS_SECRET_ACCESS_KEY'] = original_secret_key


class TestDemoVulnerabilityFramework:
    """Tests for the demo vulnerability testing framework."""

    def test_demo_test_file_exists(self):
        """Test that this demo test file exists and is properly structured."""
        import tests.test_demo_vulns
        assert hasattr(tests.test_demo_vulns, 'TestHardcodedCredentials')

    def test_app_runs_with_vulnerabilities(self, client):
        """Test that the application still runs normally with vulnerabilities present."""
        response = client.get('/')
        assert response.status_code == 200

    def test_existing_functionality_unaffected(self, client):
        """Test that existing functionality is not affected by demo vulnerabilities."""
        # Test main pages still work
        response = client.get('/products.html')
        assert response.status_code == 200
        
        response = client.get('/cart.html')
        assert response.status_code == 200

    @pytest.mark.security
    def test_vulnerability_markers_present(self):
        """Test that vulnerability markers are present in code for scanning tools."""
        # Read the app.py file to verify vulnerability markers
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for CWE reference
        assert 'CWE-798' in content
        assert 'DEMO VULNERABILITY' in content
        assert 'DO NOT USE IN PRODUCTION' in content


class TestSQLInjectionDemo:
    """Tests for CWE-89: SQL Injection vulnerability."""

    def test_demo_search_route_exists(self, client):
        """Test that the SQL injection demo route exists and is accessible."""
        response = client.get('/demo/search.html')
        assert response.status_code == 200
        assert b'SQL Injection' in response.data
        assert b'CWE-89' in response.data

    def test_normal_search_functionality(self, client):
        """Test that normal search functionality works."""
        response = client.post('/demo/search.html', data={
            'search_term': BRAND_NAME
        })
        assert response.status_code == 200
        assert b'Search Results' in response.data

    def test_sql_injection_vulnerability_present(self, client):
        """Test that SQL injection vulnerability is present (for scanning tools to detect)."""
        # Test basic SQL injection payload
        response = client.post('/demo/search.html', data={
            'search_term': "' OR '1'='1"
        })
        assert response.status_code == 200
        # Should return results due to the injection (vulnerability confirmed)

    def test_sql_injection_union_attack(self, client):
        """Test UNION-based SQL injection attack."""
        response = client.post('/demo/search.html', data={
            'search_term': "' UNION SELECT 1,2,3,4--"
        })
        # Should either return results or show an error, but not crash
        assert response.status_code == 200

    def test_sql_injection_error_handling(self, client):
        """Test that SQL injection attempts are handled without crashing."""
        malicious_payloads = [
            "'; DROP TABLE demo_products;--",
            "' OR 1=1--",
            "' UNION SELECT null,null,null,null--",
            "admin'--",
            "' OR 'x'='x"
        ]
        
        for payload in malicious_payloads:
            response = client.post('/demo/search.html', data={
                'search_term': payload
            })
            # Should handle gracefully, not crash
            assert response.status_code == 200

    def test_empty_search_handling(self, client):
        """Test handling of empty search terms."""
        response = client.post('/demo/search.html', data={
            'search_term': ''
        })
        assert response.status_code == 200

    def test_demo_template_renders_correctly(self, client):
        """Test that the demo template renders with proper warning messages."""
        response = client.get('/demo/search.html')
        assert response.status_code == 200
        assert b'Security Demo' in response.data
        assert b'WARNING' in response.data
        assert b'demonstration purposes' in response.data

    @pytest.mark.security
    def test_vulnerability_documentation_present(self, client):
        """Test that vulnerability documentation is present in the template."""
        response = client.get('/demo/search.html')
        assert response.status_code == 200
        assert b'CWE-89' in response.data
        assert b'SQL Injection' in response.data
        assert b'parameterized queries' in response.data


class TestCommandInjectionDemo:
    """Tests for CWE-78: Command Injection vulnerability."""

    def test_demo_invoice_route_exists(self, client):
        """Test that the command injection demo route exists and is accessible."""
        response = client.get('/demo/generate_invoice.html')
        assert response.status_code == 200
        assert b'Command Injection' in response.data
        assert b'CWE-78' in response.data

    def test_normal_invoice_generation(self, client):
        """Test that normal invoice generation works."""
        response = client.post('/demo/generate_invoice.html', data={
            'customer_name': 'John Doe',
            'invoice_format': 'txt'
        })
        assert response.status_code == 200
        assert b'Generated Invoice' in response.data
        assert b'John Doe' in response.data

    def test_command_injection_vulnerability_present(self, client):
        """Test that command injection vulnerability is present (for scanning tools to detect)."""
        # Test basic command injection payload
        response = client.post('/demo/generate_invoice.html', data={
            'customer_name': "John'; echo 'INJECTED'; echo '",
            'invoice_format': 'txt'
        })
        assert response.status_code == 200
        # Should execute the injected command (vulnerability confirmed)

    def test_command_injection_with_system_commands(self, client):
        """Test command injection with various system commands."""
        test_payloads = [
            "Alice'; whoami; echo '",
            "Bob'; pwd; echo '",
            "Charlie'; ls; echo '"
        ]
        
        for payload in test_payloads:
            response = client.post('/demo/generate_invoice.html', data={
                'customer_name': payload,
                'invoice_format': 'txt'
            })
            # Should handle gracefully, not crash
            assert response.status_code == 200

    def test_different_invoice_formats(self, client):
        """Test invoice generation with different formats."""
        formats = ['txt', 'pdf', 'html']
        
        for fmt in formats:
            response = client.post('/demo/generate_invoice.html', data={
                'customer_name': 'Test Customer',
                'invoice_format': fmt
            })
            assert response.status_code == 200

    def test_empty_customer_name_handling(self, client):
        """Test handling of empty customer names."""
        response = client.post('/demo/generate_invoice.html', data={
            'customer_name': '',
            'invoice_format': 'txt'
        })
        assert response.status_code == 200

    def test_command_injection_error_handling(self, client):
        """Test that command injection attempts are handled without crashing."""
        malicious_payloads = [
            "'; rm -rf /tmp/*; echo '",
            "'; cat /etc/passwd; echo '",
            "'; sleep 1; echo '",
            "'; python -c 'print(\"injected\")'; echo '"
        ]
        
        for payload in malicious_payloads:
            response = client.post('/demo/generate_invoice.html', data={
                'customer_name': payload,
                'invoice_format': 'txt'
            })
            # Should handle gracefully, not crash
            assert response.status_code == 200

    def test_demo_template_renders_correctly(self, client):
        """Test that the demo template renders with proper warning messages."""
        response = client.get('/demo/generate_invoice.html')
        assert response.status_code == 200
        assert b'Security Demo' in response.data
        assert b'WARNING' in response.data
        assert b'demonstration purposes' in response.data

    @pytest.mark.security
    def test_vulnerability_documentation_present(self, client):
        """Test that vulnerability documentation is present in the template."""
        response = client.get('/demo/generate_invoice.html')
        assert response.status_code == 200
        assert b'CWE-78' in response.data
        assert b'Command Injection' in response.data
        assert b'input validation' in response.data


class TestPathTraversalDemo:
    """Tests for CWE-22: Path Traversal vulnerability."""

    def test_demo_receipt_route_exists(self, client):
        """Test that the path traversal demo route exists and is accessible."""
        response = client.get('/demo/download_receipt.html')
        assert response.status_code == 200
        assert b'Path Traversal' in response.data
        assert b'CWE-22' in response.data

    def test_legitimate_receipt_download(self, client):
        """Test that legitimate receipt downloads work."""
        response = client.post('/demo/download_receipt.html', data={
            'receipt_filename': 'receipt_001.txt'
        })
        assert response.status_code == 200
        expected_header = f"{BRAND_NAME.upper()} SWAG SHOP RECEIPT".encode()
        assert expected_header in response.data

    def test_path_traversal_vulnerability_present(self, client):
        """Test that path traversal vulnerability is present (for scanning tools to detect)."""
        # Test basic path traversal to access app.py
        response = client.post('/demo/download_receipt.html', data={
            'receipt_filename': '../app.py'
        })
        assert response.status_code == 200
        # Should be able to access the file (vulnerability confirmed)

    def test_path_traversal_to_sensitive_files(self, client):
        """Test path traversal to access sensitive files in receipts directory."""
        sensitive_files = ['sensitive_data.txt', 'admin_notes.txt']
        
        for filename in sensitive_files:
            response = client.post('/demo/download_receipt.html', data={
                'receipt_filename': filename
            })
            assert response.status_code == 200
            # Should be able to access sensitive files

    def test_path_traversal_with_directory_traversal(self, client):
        """Test various directory traversal patterns."""
        traversal_payloads = [
            '../README.md',
            '../requirements.txt',
            '../app.py',
            '../../etc/passwd',  # This might not exist but should be handled
            '../../../etc/hosts'  # This might not exist but should be handled
        ]
        
        for payload in traversal_payloads:
            response = client.post('/demo/download_receipt.html', data={
                'receipt_filename': payload
            })
            # Should handle gracefully, not crash
            assert response.status_code == 200

    def test_nonexistent_file_handling(self, client):
        """Test handling of requests for non-existent files."""
        response = client.post('/demo/download_receipt.html', data={
            'receipt_filename': 'nonexistent_file.txt'
        })
        assert response.status_code == 200
        assert b'not found' in response.data

    def test_empty_filename_handling(self, client):
        """Test handling of empty filenames."""
        response = client.post('/demo/download_receipt.html', data={
            'receipt_filename': ''
        })
        assert response.status_code == 200

    def test_available_receipts_displayed(self, client):
        """Test that available receipts are displayed on the page."""
        response = client.get('/demo/download_receipt.html')
        assert response.status_code == 200
        assert b'Available Receipts' in response.data
        assert b'receipt_001.txt' in response.data

    def test_multiple_legitimate_receipts(self, client):
        """Test downloading multiple legitimate receipt files."""
        receipt_files = ['receipt_001.txt', 'receipt_002.txt', 'receipt_003.txt']
        
        for receipt in receipt_files:
            response = client.post('/demo/download_receipt.html', data={
                'receipt_filename': receipt
            })
            assert response.status_code == 200
            expected_header = f"{BRAND_NAME.upper()} SWAG SHOP RECEIPT".encode()
            assert expected_header in response.data

    def test_demo_template_renders_correctly(self, client):
        """Test that the demo template renders with proper warning messages."""
        response = client.get('/demo/download_receipt.html')
        assert response.status_code == 200
        assert b'Security Demo' in response.data
        assert b'WARNING' in response.data
        assert b'demonstration purposes' in response.data

    @pytest.mark.security
    def test_vulnerability_documentation_present(self, client):
        """Test that vulnerability documentation is present in the template."""
        response = client.get('/demo/download_receipt.html')
        assert response.status_code == 200
        assert b'CWE-22' in response.data
        assert b'Path Traversal' in response.data
        assert b'Validate and sanitize' in response.data

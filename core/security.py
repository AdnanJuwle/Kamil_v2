import os
import re

class SecurityManager:
    @staticmethod
    def sanitize_filename(filename):
        """Remove potentially dangerous characters from filenames"""
        if not filename:
            raise ValueError("Filename cannot be empty")
            
        # Remove path traversal attempts
        filename = re.sub(r'\.\./|\.\.\\', '', filename)
        
        # Remove potentially dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # Limit filename length
        if len(filename) > 100:
            raise ValueError("Filename too long")
            
        return filename

    @staticmethod
    def safe_path(base_path, user_path):
        """Ensure the resolved path is within the safe base path"""
        base_path = os.path.abspath(base_path)
        full_path = os.path.abspath(os.path.join(base_path, user_path))
        
        if not full_path.startswith(base_path):
            raise SecurityError("Path traversal attempt detected")
            
        return full_path

class SecurityError(Exception):
    pass

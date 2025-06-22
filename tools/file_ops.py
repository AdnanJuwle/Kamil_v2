import os
import logging

class FileOperationsTool:
    def __init__(self):
        self.logger = logging.getLogger("FileOperations")

    def execute(self, action, **kwargs):
        if action == "save_file":
            return self.save_file(kwargs['filename'], kwargs['content'])
        elif action == "read_file":
            return self.read_file(kwargs['filename'])
        elif action == "list_dir":
            return self.list_directory(kwargs['path'])
        else:
            raise ValueError(f"Unknown action: {action}")

    def save_file(self, filename, content):
        try:
            with open(filename, 'w') as f:
                f.write(content)
            self.logger.info(f"Saved file: {filename}")
            return f"File saved successfully: {filename}"
        except Exception as e:
            self.logger.error(f"Error saving file: {str(e)}")
            return f"Error: {str(e)}"

    def read_file(self, filename):
        try:
            if not os.path.exists(filename):
                return "File not found"
            with open(filename, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error: {str(e)}"

    def list_directory(self, path):
        try:
            return os.listdir(path)
        except Exception as e:
            return f"Error: {str(e)}"

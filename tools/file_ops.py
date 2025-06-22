import os
import subprocess
import logging
import uuid

class FileOperationsTool:
    def __init__(self, workspace="kamil_workspace"):
        self.logger = logging.getLogger("FileOperations")
        self.workspace = workspace
        os.makedirs(workspace, exist_ok=True)
        self.logger.info(f"File operations initialized. Workspace: {os.path.abspath(workspace)}")

    def execute(self, action, **kwargs):
        try:
            if action == "create_file":
                return self.create_file(kwargs['filename'], kwargs['content'])
            elif action == "read_file":
                return self.read_file(kwargs['filename'])
            elif action == "modify_file":
                return self.modify_file(kwargs['filename'], kwargs['content'], kwargs.get('mode', 'replace'))
            elif action == "delete_file":
                return self.delete_file(kwargs['filename'])
            elif action == "execute_file":
                return self.execute_file(kwargs['filename'])
            elif action == "list_files":
                return self.list_files(kwargs.get('path', '.'))
            else:
                raise ValueError(f"Unknown action: {action}")
        except Exception as e:
            self.logger.error(f"File operation error: {str(e)}")
            return f"Error: {str(e)}"

    def create_file(self, filename, content):
        filepath = self._resolve_path(filename)
        with open(filepath, 'w') as f:
            f.write(content)
        self.logger.info(f"Created file: {filepath}")
        return f"File created: {os.path.basename(filepath)}"

    def read_file(self, filename):
        filepath = self._resolve_path(filename)
        if not os.path.exists(filepath):
            return "File not found"
        with open(filepath, 'r') as f:
            content = f.read()
        return content

    def modify_file(self, filename, content, mode='replace'):
        filepath = self._resolve_path(filename)
        if mode == 'append':
            with open(filepath, 'a') as f:
                f.write(content)
            action = "appended to"
        elif mode == 'prepend':
            with open(filepath, 'r+') as f:
                existing = f.read()
                f.seek(0)
                f.write(content + existing)
            action = "prepended to"
        else:  # replace
            with open(filepath, 'w') as f:
                f.write(content)
            action = "modified"
            
        self.logger.info(f"{action.capitalize()} file: {filepath}")
        return f"File {action}: {os.path.basename(filepath)}"

    def delete_file(self, filename):
        filepath = self._resolve_path(filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            self.logger.info(f"Deleted file: {filepath}")
            return f"File deleted: {os.path.basename(filepath)}"
        return "File not found"

    def execute_file(self, filename):
        filepath = self._resolve_path(filename)
        if not os.path.exists(filepath):
            return "File not found"
        
        try:
            result = subprocess.run(
                ["python", filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout or result.stderr or "No output"
            self.logger.info(f"Executed file: {filepath}")
            return f"Execution result:\n{output}"
        except Exception as e:
            return f"Execution error: {str(e)}"

    def list_files(self, path='.'):
        dirpath = self._resolve_path(path)
        if not os.path.isdir(dirpath):
            return "Directory not found"
            
        files = []
        for item in os.listdir(dirpath):
            item_path = os.path.join(dirpath, item)
            files.append({
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0,
                "modified": os.path.getmtime(item_path)
            })
        return files

    def _resolve_path(self, path):
        # Prevent directory traversal attacks
        if '../' in path:
            raise ValueError("Invalid path")
        return os.path.join(self.workspace, path)

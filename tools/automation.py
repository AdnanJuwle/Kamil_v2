import time
import threading
import psutil
import logging
import schedule

class AutomationEngine:
    def __init__(self):
        self.workflows = {
            "optimize_system": [
                {"action": "Clean temporary files"},
                {"action": "Adjust process priorities"}
            ]
        }
        self.logger = logging.getLogger("Automation")
        self.performance_stats = {
            "llm_calls": 0,
            "avg_response_time": 0,
            "total_requests": 0
        }
        self.logger.info("Automation engine initialized")
        self._start_monitoring()
        self._start_performance_monitoring()

    def execute(self, action, **kwargs):
        if action == "create_workflow":
            return self.create_workflow(kwargs['name'], kwargs['steps'])
        elif action == "run_workflow":
            return self.run_workflow(kwargs['name'])
        elif action == "system_status":
            return self.get_system_status()
        else:
            raise ValueError(f"Unknown action: {action}")

    def create_workflow(self, name, steps):
        self.workflows[name] = steps
        self.logger.info(f"Created workflow: {name} with {len(steps)} steps")
        return f"Workflow '{name}' created"

    def run_workflow(self, name):
        if name not in self.workflows:
            return f"Workflow '{name}' not found"
        
        self.logger.info(f"Running workflow: {name}")
        for step in self.workflows[name]:
            time.sleep(1)  # Simulate task execution
        return f"Completed workflow: {name}"

    def get_system_status(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return f"System Status:\n- CPU: {cpu}%\n- Memory: {mem}%\n- Disk: {disk}%"

    def track_request(self, response_time):
        self.performance_stats['total_requests'] += 1
        self.performance_stats['llm_calls'] += 1
        # Calculate moving average of response time
        if self.performance_stats['avg_response_time'] == 0:
            self.performance_stats['avg_response_time'] = response_time
        else:
            self.performance_stats['avg_response_time'] = (
                self.performance_stats['avg_response_time'] * 0.9 + 
                response_time * 0.1
            )

    def _start_monitoring(self):
        def monitor():
            cpu = psutil.cpu_percent()
            if cpu > 90:
                self.logger.warning(f"High CPU usage: {cpu}%")
                if "optimize_system" in self.workflows:
                    self.run_workflow("optimize_system")
        
        schedule.every(1).minutes.do(monitor)
        threading.Thread(target=self._run_scheduler, daemon=True).start()

    def _start_performance_monitoring(self):
        def log_performance():
            self.logger.info(
                f"Performance: Requests={self.performance_stats['total_requests']}, "
                f"LLM calls={self.performance_stats['llm_calls']}, "
                f"Avg response={self.performance_stats['avg_response_time']:.2f}s"
            )
        
        schedule.every(5).minutes.do(log_performance)
        threading.Thread(target=self._run_scheduler, daemon=True).start()

    def _run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

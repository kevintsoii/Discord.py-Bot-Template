from prometheus_client import Counter, start_http_server


class MetricsHandler:
    def __init__(self):
        self.command_counter = Counter("commands_total", "Total number of successful commands", ["cog", "command"])
        self.error_counter = Counter("errors_total", "Total number of command errors", ["cog", "command", "error"])

    def start_server(self):
        start_http_server(8000)

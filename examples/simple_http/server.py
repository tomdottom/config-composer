import logging
import sys
from pathlib import Path

from http.server import HTTPServer, BaseHTTPRequestHandler


# Add repo root to path to make config_composer importable
repo_root = str(Path(__file__).absolute().parent.parent.parent)
sys.path.append(repo_root)
from config_composer.core import Config, Spec  # noqa: E402s


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigSpec(Spec):
    host: str
    port: int
    db_pass: str


config = Config(config_spec=ConfigSpec, env_var="SOURCE_SPEC_PATH")


def mock_query_db():
    # password = config.db_pass

    return "Bob"


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        username = mock_query_db().encode()

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, " + username)


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    logger.info(f"Serving on {config.host}:{config.port}")
    server_address = (config.host, config.port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    run()

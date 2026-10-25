"""Render real Compose configurations without starting containers or sending mail."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which("docker"), "Docker Compose is required")
class ProductionConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in (
            "docker/docker-compose.prod.yml",
            "docker/docker-compose.creator-watch.yml",
            "scripts/start-production-stack.sh",
        ):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.values = {
            "QATOOLBOX_IMAGE": "local-app:verified-release",
            "POSTGRES_PASSWORD": "test-database-password",
            "REDIS_PASSWORD": "test-redis-password",
            "DJANGO_SECRET_KEY": "test-only-django-secret",
        }

    def render(self):
        (self.root / ".env").write_text("".join(f"{key}='{value}'\n" for key, value in self.values.items()))
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in self.values
            and key
            not in {
                "DB_NAME",
                "DB_USER",
                "POSTGRES_PASSWORD",
                "REDIS_PASSWORD",
                "DJANGO_SECRET_KEY",
                "QATOOLBOX_IMAGE",
                "REDIS_URL",
                "XHS_MCP_TOKEN",
                "XHS_MCP_BASE_URL",
                "XHS_MCP_IMAGE",
                "COMPOSE_FILE",
                "COMPOSE_PROJECT_NAME",
            }
        }
        environment.update(QATOOLBOX_DIR=str(self.root), COMPOSE_PROJECT_NAME="wrong-project")
        return subprocess.run(
            [
                "bash",
                str(self.root / "scripts/start-production-stack.sh"),
                "compose",
                "config",
                "--format",
                "json",
            ],
            cwd=tempfile.gettempdir(),
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def config(self):
        result = self.render()
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_web_and_worker_use_identical_environment_and_image(self):
        self.values["XHS_MCP_TOKEN"] = "test-mcp-token"
        config = self.config()
        web = config["services"]["web"]
        worker = config["services"]["creator_watch"]
        self.assertEqual(web["environment"], worker["environment"])
        self.assertEqual(web["image"], "local-app:verified-release")
        self.assertEqual(web["image"], worker["image"])
        self.assertEqual(web["volumes"], worker["volumes"])
        self.assertEqual(web["environment"]["XHS_MCP_BASE_URL"], "http://xiaohongshu-mcp:18060")

    def test_every_service_uses_existing_production_network_and_volumes(self):
        self.values["XHS_MCP_TOKEN"] = "test-mcp-token"
        config = self.config()
        self.assertEqual(config["name"], "docker")
        self.assertEqual(config["networks"]["default"]["name"], "modeshift_network")
        for service in config["services"].values():
            self.assertEqual(set(service["networks"]), {"default"})
        for volume in ("postgres_data", "redis_data", "media_volume", "xhs_mcp_data"):
            self.assertEqual(config["volumes"][volume]["name"], f"docker_{volume}")

    def test_database_and_redis_credentials_match_their_clients(self):
        config = self.config()["services"]
        self.assertEqual(config["db"]["environment"]["POSTGRES_PASSWORD"], config["web"]["environment"]["DB_PASSWORD"])
        self.assertEqual(config["db"]["environment"]["POSTGRES_DB"], config["web"]["environment"]["DB_NAME"])
        self.assertEqual(config["web"]["environment"]["REDIS_URL"], "redis://:test-redis-password@redis:6379/0")
        self.assertIn("test-redis-password", config["redis"]["command"])

    def test_empty_mcp_token_does_not_enable_the_overlay(self):
        self.values["XHS_MCP_TOKEN"] = ""
        self.assertNotIn("xiaohongshu-mcp", self.config()["services"])

    def test_missing_password_fails_instead_of_using_legacy_env(self):
        del self.values["POSTGRES_PASSWORD"]
        (self.root / ".env.vm").write_text("POSTGRES_PASSWORD=legacy-value\n")
        result = self.render()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("POSTGRES_PASSWORD", result.stderr)
        self.assertNotIn("legacy-value", result.stdout + result.stderr)

    def test_env_file_is_not_executed_as_shell_code(self):
        marker = self.root / "must-not-exist"
        self.values["XHS_MCP_TOKEN"] = f"$(touch {marker})"
        self.assertIn("xiaohongshu-mcp", self.config()["services"])
        self.assertFalse(marker.exists())

    def test_missing_release_does_not_fall_back_to_main(self):
        del self.values["QATOOLBOX_IMAGE"]
        result = self.render()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("QATOOLBOX_IMAGE", result.stderr)


if __name__ == "__main__":
    unittest.main()

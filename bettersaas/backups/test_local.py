import gzip
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from bettersaas.backups import local


class TestLocalBackups(unittest.TestCase):
	def setUp(self):
		self.temp_dir = tempfile.TemporaryDirectory()
		self.bench = Path(self.temp_dir.name)
		self.site = "customer.example.test"
		self.site_path = self.bench / "sites" / self.site
		self.backup_path = self.site_path / "private" / "backups"
		self.backup_path.mkdir(parents=True)
		self.bench_patch = patch.object(local, "get_bench_path", return_value=str(self.bench))
		self.bench_patch.start()

	def tearDown(self):
		self.bench_patch.stop()
		self.temp_dir.cleanup()

	def _backup_set(self, number, age_hours=0, with_files=False):
		prefix = f"2026080{number}_013000-{self.site}"
		database = self.backup_path / f"{prefix}-database.sql.gz"
		with gzip.open(database, "wb") as stream:
			stream.write(b"SELECT 1;\n")
		config = self.backup_path / f"{prefix}-site_config_backup.json"
		config.write_text(json.dumps({"db_name": "test"}), encoding="utf-8")
		paths = [database, config]
		if with_files:
			for suffix in ("-files.tar", "-private-files.tar"):
				path = self.backup_path / f"{prefix}{suffix}"
				path.write_bytes(b"archive")
				paths.append(path)
		stamp = (datetime.now() - timedelta(hours=age_hours)).timestamp()
		for path in paths:
			os.utime(path, (stamp, stamp))
		return paths

	@patch.object(local.frappe, "conf", {"local_backup_count": 2, "local_file_backup_retention_hours": 24})
	def test_cleanup_keeps_latest_database_sets_and_expires_file_archives(self):
		old = self._backup_set(1, age_hours=72, with_files=True)
		middle = self._backup_set(2, age_hours=48, with_files=True)
		latest = self._backup_set(3, age_hours=1, with_files=True)
		legacy_zip = self.site_path / "private" / f"20260801_013000-{self.site}.zip"
		legacy_zip.write_bytes(b"legacy")
		old_stamp = (datetime.now() - timedelta(hours=48)).timestamp()
		os.utime(legacy_zip, (old_stamp, old_stamp))
		unrelated_zip = self.site_path / "private" / "customer-document.zip"
		unrelated_zip.write_bytes(b"keep")

		local.cleanup_site_backups(self.site)

		self.assertFalse(old[0].exists())
		self.assertFalse(old[1].exists())
		self.assertTrue(middle[0].exists())
		self.assertTrue(middle[1].exists())
		self.assertTrue(latest[0].exists())
		self.assertTrue(latest[1].exists())
		self.assertFalse(middle[2].exists())
		self.assertFalse(middle[3].exists())
		self.assertTrue(latest[2].exists())
		self.assertTrue(latest[3].exists())
		self.assertFalse(legacy_zip.exists())
		self.assertTrue(unrelated_zip.exists())

	def test_site_path_rejects_traversal(self):
		with self.assertRaises(ValueError):
			local._site_path("../other")

	def test_verifies_database_and_matching_config(self):
		database, config = self._backup_set(1)[:2]
		local._verify_database_file(database)
		local._verify_config_file(database)
		config.unlink()
		with self.assertRaises(RuntimeError):
			local._verify_config_file(database)

	def test_recognizes_native_encrypted_backup_names(self):
		prefix = f"20260807_013000-{self.site}"
		database = self.backup_path / f"{prefix}-database-enc.sql.gz"
		database.write_bytes(b"encrypted")
		config = self.backup_path / f"{prefix}-site_config_backup-enc.json"
		config.write_text(json.dumps({"backup_encryption_key": "test"}), encoding="utf-8")
		self.assertIn(database, local._database_backups(self.site_path))
		local._verify_database_file(database)
		local._verify_config_file(database)

	@patch.object(local.frappe, "conf", {"local_backup_min_free_gb": 20})
	@patch.object(local.shutil, "disk_usage")
	def test_disk_reserve_stops_backup(self, disk_usage):
		disk_usage.return_value = SimpleNamespace(free=10 * 1024**3)
		with self.assertRaisesRegex(RuntimeError, "reserve.*required"):
			local._assert_disk_reserve(self.site_path)


if __name__ == "__main__":
	unittest.main()

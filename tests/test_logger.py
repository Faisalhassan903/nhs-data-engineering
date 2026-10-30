import logging

from src.utlis import logger as logger_module


def test_logger_uses_configured_directory(tmp_path, monkeypatch):
    log_dir = tmp_path / "configured_logs"
    working_dir = tmp_path / "working_directory"
    working_dir.mkdir()
    monkeypatch.setattr(logger_module, "LOG_DIR", log_dir)
    monkeypatch.chdir(working_dir)
    name = "tests.configured_log_directory"
    logger = logging.getLogger(name)
    try:
        configured = logger_module.get_logger(name)
        configured.info("test log message")
        assert "test log message" in (log_dir / "pipeline.log").read_text()
        assert not (working_dir / "logs").exists()
        assert logger_module.get_logger(name) is configured
        assert len(configured.handlers) == 2
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

from interactive import log


class TestLog:

    def test_set_log_level(self):
        """
        Simply tests there is no error when calling set_log_level()
        """
        log.set_log_level(log.DEBUG)
        log.set_log_level(log.WARNING)

    def test_stacktrace(self):
        """
        Simply tests there is no error when calling stacktrace()
        """
        try:
            raise Exception("raise error")
        except Exception as e:
            log.stacktrace(e)

    def test_debug(self):
        """
        Simply tests there is no error when calling debug()
        """
        log.debug("DEBUG message")

    def test_info(self):
        """
        Simply tests there is no error when calling info()
        """
        log.info("INFO message")

    def test_warn(self):
        """
        Simply tests there is no error when calling warn()
        """
        log.warn("WARN message")

    def test_error(self):
        """
        Simply tests there is no error when calling error()
        """
        log.error("ERROR message")

    def test_critical(self):
        """
        Simply tests there is no error when calling critical()
        """
        log.critical("CRITICAL message")

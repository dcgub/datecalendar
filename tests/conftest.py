def pytest_configure(config):
	#  https://docs.pytest.org/en/latest/how-to/mark.html
	config.addinivalue_line(
		"markers", 'slow: marks tests as slow (deselect with -m "not slow")'
	)

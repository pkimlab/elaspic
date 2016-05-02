import os
import os.path as op
import pytest


# %% Directories
try:
    TESTS_BASE_DIR = op.dirname(__file__)
except NameError:
    TESTS_BASE_DIR = os.getcwd()
assert op.split(TESTS_BASE_DIR)[-1] == 'tests'

TESTS_DATA_DIR = op.join(TESTS_BASE_DIR, 'data')

# Config files
DEFAULT_LOCAL_CONFIG = op.join(TESTS_BASE_DIR, 'test_local_pipeline.ini')
DEFAULT_DATABASE_CONFIG = op.join(TESTS_BASE_DIR, 'test_database_pipeline.ini')


# %% Pytest
def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)


# Command line options
def pytest_addoption(parser):
    parser.addoption("--quick", default=False, action="store_true",
                     help="Run only quick tests.")
    parser.addoption("--config-file", default=None,
                     help="Name of the configuration file.")


@pytest.fixture
def quick(request):
    return request.config.getoption("--quick")


@pytest.fixture
def config_file(request):
    return request.config.getoption("--config-file")


print('Conftest loaded!')

"""Test package loading default extension

"""
import pytest
import yamlsettings
from yamlsettings.extensions.package import PackageExtension
from yamlsettings.extensions.registry import ExtensionRegistry


@pytest.fixture
def package_data(monkeypatch, mocker):
    """Clean registry with only a fresh package extension"""
    reg_fixture = ExtensionRegistry([
        PackageExtension
    ])
    # Remove persistance support
    monkeypatch.setattr(PackageExtension, '_persistence', {})
    # Hook load functions to root of yamlsettings
    monkeypatch.setattr(yamlsettings, 'load', reg_fixture.load)
    monkeypatch.setattr(yamlsettings, 'load_all', reg_fixture.load_all)

    # Lock down environment loading support
    monkeypatch.setattr('os.environ', {
        'ENV_VAL': "mocked",
    })

    return mocker.patch('pkgutil.get_data')


@pytest.mark.parametrize("data_input", [
    b'---\nmocked: package\n',
    b'---\nmocked: package2\n',
])
def test_package_config(package_data, data_input):
    """Package load

    Note: This will fail on the second pass if PackageExtension is not fresh

    """
    package_data.return_value = data_input

    cfg = yamlsettings.load('package://example')
    package_data.assert_called_once_with('example', 'settings.yaml')
    assert cfg.mocked.startswith("package")

    # Verify persistence is working
    package_data.return_value = 'should not be read'
    cfg = yamlsettings.load('package://example')
    assert cfg.mocked.startswith("package")
    assert package_data.call_count == 1


def test_no_package_data(package_data):
    """Verify IOError without package data"""
    package_data.return_value = None
    with pytest.raises(IOError):
        yamlsettings.load('package://example')


def test_resource(package_data):
    """Testing loading another resource"""
    package_data.return_value = b'a: b\n'
    cfg = yamlsettings.load('package://example?resource=foo.yaml')
    package_data.assert_called_once_with('example', 'foo.yaml')
    assert cfg.a == 'b'


def test_env(package_data):
    """Testing with key matching the env"""
    package_data.return_value = b'env_val: needed\n'
    cfg = yamlsettings.load('pkg://example')
    assert cfg.env_val == 'mocked'


def test_env_prefix(package_data):
    """Test env prefix support"""
    package_data.return_value = b'val: needed\n'
    cfg = yamlsettings.load('pkg://example?prefix=ENV')
    assert cfg.val == 'mocked'


def test_no_cache(package_data):
    """Disable persistence"""
    package_data.return_value = b'val: one\n'
    cfg = yamlsettings.load('pkg://example?persist=false')
    assert cfg.val == 'one'

    package_data.return_value = b'val: two\n'
    cfg = yamlsettings.load('pkg://example?persist=false')
    assert cfg.val == 'two'

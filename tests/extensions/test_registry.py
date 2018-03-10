"""Test registry"""
import pytest
import yamlsettings
from yamlsettings.extensions.registry import ExtensionRegistry

from mock import Mock


class MockExtension(yamlsettings.YamlSettingsExtension):
    protocols = ['mock']

    @classmethod
    def load_target(cls, scheme, path, fragment, username,
                    password, hostname, port, query,
                    load_method, **kwargs):
        return load_method("mock: test")


class MockExtension2(yamlsettings.YamlSettingsExtension):
    protocols = ['mock2']

    @classmethod
    def load_target(cls, scheme, path, fragment, username,
                    password, hostname, port, query,
                    load_method, **kwargs):
        return load_method("mock: test")


@pytest.fixture
def base_registry(monkeypatch, mocker):
    """Clean registry with only a fresh package extension"""

    entry_iter = mocker.patch('pkg_resources.iter_entry_points')
    # Test when object already created
    mock_call = Mock()
    mock_call.load.return_value = MockExtension()
    # Test when object needs to be called
    mock_call2 = Mock()
    mock_call2.load.return_value = MockExtension2
    entry_iter.return_value = [mock_call, mock_call2]

    clean_reg = ExtensionRegistry([])
    monkeypatch.setattr(yamlsettings, 'load', clean_reg.load)
    monkeypatch.setattr(yamlsettings, 'load_all', clean_reg.load_all)


def test_mock_exists(base_registry):
    """Very mock is loaded with entrypoint detection"""
    cfg = yamlsettings.load('mock://please')
    assert cfg.mock == 'test'

    cfg = yamlsettings.load('mock2://please')
    assert cfg.mock == 'test'


def test_mock_ext(base_registry):
    """Test package extension is not installed"""
    with pytest.raises(yamlsettings.RegistryError):
        yamlsettings.load('package://example')

import pytest

from sopel_boorus.danbooru.plugin import _build_danbooru_headers
from sopel_boorus.danbooru.types import DanbooruSettings


TEST_CFG_NO_USERNAME = '''
[core]
nick = testbot
owner = testowner
'''

TEST_CFG_USERNAME_TPL = '''
[core]
nick = testbot
owner = testowner

[danbooru]
username = {username}
'''

TEST_CFG_WITH_USERNAME = TEST_CFG_USERNAME_TPL.format(username='testuser')

TEST_CFG_EMPTY_USERNAME = TEST_CFG_USERNAME_TPL.format(username='')


@pytest.fixture
def settings_no_username(configfactory):
    """Fixture for config without Danbooru username."""
    settings = configfactory('test.cfg', TEST_CFG_NO_USERNAME)
    settings.define_section('danbooru', DanbooruSettings)
    return settings


@pytest.fixture
def settings_with_username(configfactory):
    """Fixture for config with Danbooru username set."""
    settings = configfactory(
        'test.cfg', TEST_CFG_USERNAME_TPL.format(username='testuser'))
    settings.define_section('danbooru', DanbooruSettings)
    return settings


@pytest.fixture
def settings_empty_username(configfactory):
    """Fixture for config with empty Danbooru username."""
    settings = configfactory(
        'test.cfg', TEST_CFG_USERNAME_TPL.format(username=''))
    settings.define_section('danbooru', DanbooruSettings)
    return settings


def test_headers_with_username(settings_with_username):
    """Test that username is included in User-Agent when set."""
    headers = _build_danbooru_headers(settings_with_username)

    assert 'User-Agent' in headers
    assert headers['User-Agent'].startswith('sopel-boorus/')
    assert '(testuser)' in headers['User-Agent']

def test_headers_without_username(settings_no_username):
    """Test that User-Agent doesn't include username when not set."""
    headers = _build_danbooru_headers(settings_no_username)

    assert 'User-Agent' in headers
    assert headers['User-Agent'].startswith('sopel-boorus/')
    # Should not have parentheses when no username
    assert '()' not in headers['User-Agent']
    assert '(' not in headers['User-Agent']
    assert ')' not in headers['User-Agent']

def test_headers_with_empty_string_username(settings_empty_username):
    """Test that empty string username is treated as not set."""
    headers = _build_danbooru_headers(settings_empty_username)

    assert 'User-Agent' in headers
    # Empty string is falsy, should not be in User-Agent
    assert '()' not in headers['User-Agent']
    assert '(' not in headers['User-Agent']
    assert ')' not in headers['User-Agent']

def test_version_is_dynamic(settings_with_username):
    """Test that version comes from package metadata."""
    from importlib.metadata import version as get_version

    headers = _build_danbooru_headers(settings_with_username)

    expected_version = get_version('sopel-boorus')
    assert expected_version in headers['User-Agent']
    assert headers['User-Agent'].startswith(f'sopel-boorus/{expected_version}')

@pytest.mark.parametrize('username', [
    'test-user_123',
    'user.name',
    'user@domain',
    'user123',
])
def test_headers_with_special_characters_username(configfactory, username):
    """Test that special characters in username are preserved."""
    settings = configfactory(
        'test.cfg', TEST_CFG_USERNAME_TPL.format(username=username))
    settings.define_section('danbooru', DanbooruSettings)
    headers = _build_danbooru_headers(settings)

    assert 'User-Agent' in headers
    assert headers['User-Agent'].endswith(f' ({username})')

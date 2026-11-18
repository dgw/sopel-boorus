from importlib.metadata import version

from sopel_boorus.util import get_json


class FakeResponse:
    """Fake response object for testing without network calls."""
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {'key': 'value'}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        pass


def test_default_user_agent_header(monkeypatch):
    """Test that default User-Agent header is included."""
    # Store the call args by wrapping the function
    calls = []

    def tracking_get(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    monkeypatch.setattr('sopel_boorus.util.requests.get', tracking_get)
    get_json('http://example.com/api')

    assert len(calls) == 1
    call_kwargs = calls[0]
    assert 'headers' in call_kwargs
    assert 'User-Agent' in call_kwargs['headers']
    assert call_kwargs['headers']['User-Agent'].startswith('sopel-boorus/')
    assert version('sopel-boorus') in call_kwargs['headers']['User-Agent']


def test_custom_headers_passed_through(monkeypatch):
    """Test that custom headers are passed to requests.get()."""
    calls = []

    def tracking_get(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    monkeypatch.setattr('sopel_boorus.util.requests.get', tracking_get)

    custom_headers = {'Authorization': 'Bearer token123'}
    get_json('http://example.com/api', headers=custom_headers)

    assert len(calls) == 1
    call_kwargs = calls[0]
    assert 'headers' in call_kwargs
    assert 'Authorization' in call_kwargs['headers']
    assert call_kwargs['headers']['Authorization'] == 'Bearer token123'


def test_custom_headers_override_user_agent(monkeypatch):
    """Test that custom User-Agent header overrides the default."""
    calls = []

    def tracking_get(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    monkeypatch.setattr('sopel_boorus.util.requests.get', tracking_get)

    custom_headers = {'User-Agent': 'CustomBot/1.0'}
    get_json('http://example.com/api', headers=custom_headers)

    assert len(calls) == 1
    call_kwargs = calls[0]
    assert 'headers' in call_kwargs
    assert call_kwargs['headers']['User-Agent'] == 'CustomBot/1.0'


def test_custom_headers_case_insensitivity(monkeypatch):
    """Test that custom headers are case-insensitive."""
    calls = []

    def tracking_get(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    monkeypatch.setattr('sopel_boorus.util.requests.get', tracking_get)

    # Pass a custom header with different case
    custom_headers = {'user-agent': 'CustomBot/1.0'}
    get_json('http://example.com/api', headers=custom_headers)

    assert len(calls) == 1
    call_kwargs = calls[0]
    headers = call_kwargs['headers']

    assert len(headers) == 1
    assert headers['User-Agent'] == 'CustomBot/1.0'


def test_multiple_custom_headers(monkeypatch):
    """Test that multiple custom headers are all passed through."""
    calls = []

    def tracking_get(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    monkeypatch.setattr('sopel_boorus.util.requests.get', tracking_get)

    custom_headers = {
        'Authorization': 'Bearer token123',
        'X-Custom-Header': 'custom-value',
        'Accept': 'application/json',
    }
    # do the thing
    get_json('http://example.com/api', headers=custom_headers)

    assert len(calls) == 1
    call_kwargs = calls[0]
    headers = call_kwargs['headers']

    assert headers['Authorization'] == 'Bearer token123'
    assert headers['X-Custom-Header'] == 'custom-value'
    assert headers['Accept'] == 'application/json'
    # Default User-Agent should also be present
    assert 'User-Agent' in headers
    assert headers['User-Agent'].startswith('sopel-boorus/')


def test_no_custom_headers(monkeypatch):
    """Test that no custom headers defaults to just User-Agent."""
    calls = []

    def tracking_get(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    monkeypatch.setattr('sopel_boorus.util.requests.get', tracking_get)

    # do the thing
    get_json('http://example.com/api', headers=None)

    assert len(calls) == 1
    call_kwargs = calls[0]
    headers = call_kwargs['headers']

    assert len(headers) == 1
    assert 'User-Agent' in headers
    assert headers['User-Agent'].startswith('sopel-boorus/')


def test_custom_headers_with_params(monkeypatch):
    """Test that custom headers work alongside query parameters."""
    calls = []

    def tracking_get(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    monkeypatch.setattr('sopel_boorus.util.requests.get', tracking_get)

    params = {'search': 'test', 'limit': '10'}
    custom_headers = {'Authorization': 'Bearer token123'}

    # do the thing
    get_json('http://example.com/api', params=params, headers=custom_headers)

    assert len(calls) == 1
    call_kwargs = calls[0]

    assert 'params' in call_kwargs
    assert call_kwargs['params'] == params
    assert 'headers' in call_kwargs
    assert call_kwargs['headers']['Authorization'] == 'Bearer token123'


def test_empty_custom_headers_dict(monkeypatch):
    """Test behavior when empty custom headers dict is passed."""
    calls = []

    def tracking_get(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    monkeypatch.setattr('sopel_boorus.util.requests.get', tracking_get)

    # do the thing
    get_json('http://example.com/api', headers={})

    assert len(calls) == 1
    call_kwargs = calls[0]

    assert 'headers' in call_kwargs
    # Empty dict shouldn't remove default headers
    assert 'User-Agent' in call_kwargs['headers']
    assert call_kwargs['headers']['User-Agent'].startswith('sopel-boorus/')

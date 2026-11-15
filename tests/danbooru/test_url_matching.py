import pytest
from sopel.plugins.rules import URLCallback

from sopel_boorus.danbooru.plugin import danbooru_url


TEST_CFG = '''
[core]
nick = testbot
owner = testowner
'''


@pytest.fixture
def url_rule(configfactory):
    settings = configfactory('test.cfg', TEST_CFG)
    return URLCallback.from_callable(settings, danbooru_url)


@pytest.mark.parametrize(('url', 'post_id'), [
    ('https://danbooru.donmai.us/posts/12345', '12345'),
    ('http://danbooru.donmai.us/posts/42', '42'),
    ('https://danbooru.donmai.us/posts/12345/', '12345'),
    ('https://danbooru.donmai.us/posts/12345?tags=cat', '12345'),
    ('https://danbooru.donmai.us/posts/12345#comments', '12345'),
    ('https://danbooru.donmai.us/posts/12345/?tags=cat#comments', '12345'),
    ('https://danbooru.donmai.us/post/show/6789', '6789'),
    ('http://danbooru.donmai.us/post/show/6789/?tags=cat', '6789'),
])
def test_post_urls_match(url_rule, url, post_id):
    matches = list(url_rule.parse(url))

    assert len(matches) == 1
    assert matches[0].group(1) == post_id


@pytest.mark.parametrize('url', [
    'https://danbooru.donmai.us/',
    'https://danbooru.donmai.us/posts',
    'https://danbooru.donmai.us/posts?tags=cat',
    'https://danbooru.donmai.us/posts/12345.json',
    'https://danbooru.donmai.us/posts/12345/edit',
    'https://danbooru.donmai.us/posts/abc',
    'https://danbooru.donmai.us/posts/123abc',
    'https://danbooru.donmai.us/post/show',
    'https://danbooru.donmai.us/wiki_pages/12345',
    'https://danbooru.donmai.us/pools/12345',
    'https://danbooru.donmai.us/artists/12345',
    'https://danbooru.donmai.us/users/12345',
    'https://danbooru.donmai.us/tags/12345',
    'https://example.com/posts/12345',
    'https://danbooru.donmai.us.example.com/posts/12345',
])
def test_non_post_urls_do_not_match(url_rule, url):
    assert list(url_rule.parse(url)) == []

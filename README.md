# sopel-boorus

Image board (booru) plugins for Sopel IRC bots.

## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-boorus
```

[**Depending on your Sopel bot's configuration**][sopel-endis-plugins], you
might need to enable or disable the specific booru plugins ([see
below](#booru-plugins-in-this-collection)) that you want your bot to use. You
can do so with [the `sopel-plugins` command][cli-sopel-plugins], e.g.:

```shell
$ sopel-plugins enable gelbooru
```

[cli-sopel-plugins]: https://sopel.chat/docs/run/cli.html#sopel-plugins
[sopel-endis-plugins]: https://sopel.chat/docs/run/plugin#enabling-or-disabling-plugins

### Booru plugins in this collection

* `danbooru`: Supports Danbooru (https://danbooru.donmai.us) links & searches
* `gelbooru`: Supports Gelbooru (https://gelbooru.com) links & searches

### Installation requirements

The `sopel-boorus` package is written with Python 3 and Sopel 8.0+ in mind.
Installation on Python 2, or usage with Sopel 7.x, is not supported.

## Using

### `danbooru`

**Note: Danbooru strictly limits search capabilities for anonymous users,**
making this plugin more useful for link handling than searching, though it will
be able to handle a tag or two just fine if you want a random pic.

Commands: `.danb` or `.danbooru` to search for a random post by tag(s)

Links: Handles post links, e.g. `https://danbooru.donmai.us/posts/<post_id>`

### `gelbooru`

Commands: `.gelb` or `.gelbooru` to search for a random post by tag(s)

Links: Handles post links, e.g.
`https://gelbooru.com/index.php?page=post&s=view&id=<post_id>`

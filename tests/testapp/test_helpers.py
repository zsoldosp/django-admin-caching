from django.utils import translation
import lxml.html


def text_content(e):
    return e.text_content().strip()


def texts_for(e, selector):
    return list(text_content(m) for m in e.cssselect(selector))


def text_for_tags(e, tags):
    return list(
        text_content(c)
        for c in e.getchildren()
        if c.tag in tags
    )


def parse_table(response):
    html = lxml.html.fromstring(response.content)
    table, = html.cssselect('table#result_list')
    headers = texts_for(table, 'thead th')
    rows = list(
        text_for_tags(row, ('td', 'th'))
        for row in table.cssselect('tbody tr')
    )
    return headers, rows


def get_group_changelist_table(admin_client):
    response = admin_client.get('/admin/auth/group/')
    assert response.status_code == 200
    return parse_table(response)


class translation_being(object):

    def __init__(self, language):
        self.language = language

    def __enter__(self):
        fn_type = type(get_group_changelist_table)
        t = translation._trans.__dict__
        keys_to_delete = list(k for k in t.keys() if isinstance(t[k], fn_type))
        for k in keys_to_delete:
            del t[k]
        self.retained_language = translation.get_language()
        translation.activate(self.language)

    def __exit__(self, exc_type, exc_val, exc_tb):
        translation.activate(self.retained_language)

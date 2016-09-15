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

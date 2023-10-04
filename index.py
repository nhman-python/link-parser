from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired
from wtforms import URLField, SubmitField
import httpx
from selectolax.parser import HTMLParser
from urllib.parse import urlparse, urljoin
import validators

app = Flask(__name__)
app.secret_key = 'password'
user_agent = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; Win64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5653.214 '
                  'Safari/537.36'}


class UrlForm(FlaskForm):
    url = URLField('url', validators=[InputRequired()])
    submit = SubmitField('submit')


def get_html_url(url: str):
    html = httpx.get(url, headers=user_agent).text
    tree = HTMLParser(html)
    links = tree.css('a')
    href_values = [link.attributes.get('href', '') for link in links]
    return href_values


def fixed_links(base: str, links: list[str]):
    links_fixed = []
    for link in links:
        if validators.url(link):
            links_fixed.append(link)
        elif link in ['#', '', ' ']:
            continue
        elif link is None:
            continue
        elif link.startswith('/'):
            link = urljoin(base, link)
            links_fixed.append(link)
            continue
    return links_fixed


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UrlForm()
    if request.method == 'POST':
        url = form.url.data
        parser = urlparse(url)
        base = parser.scheme + '://' + parser.netloc
        links = fixed_links(base, get_html_url(url))
        enumerated_links = list(enumerate(links, start=1))
        return render_template('index.html', form=form, links=enumerated_links)
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)

# tests/test_newsletter_template.py

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def render(**overrides):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    data = {
        "title": "Your Niyoz digest",
        "day_of_week": "Monday",
        "date": "Mar 3rd",
        "video_title_summary": "bread, bikes and a backyard telescope",
        "video_summaries": [
            {
                "video_title": "The 3-Ingredient Sourdough I Bake Every Sunday",
                "video_url": "https://www.youtube.com/watch?v=demo-sourdough",
                "channel_name": "Crumb & Crust Kitchen",
                "summary": "<p>Flour, water, salt and a long cold proof.</p>",
            }
        ],
        "is_premium": False,
        "app_url": "https://niyoz.example.com",
        "contact_email": "hello@example.com",
    }
    data.update(overrides)
    return env.get_template("newsletter.html").render(**data)


def test_free_newsletter_has_upgrade_and_video():
    html = render()
    assert "The 3-Ingredient Sourdough I Bake Every Sunday" in html
    assert "Crumb &amp; Crust Kitchen" in html
    assert "https://niyoz.example.com/pricing" in html


def test_premium_newsletter_hides_upgrade():
    html = render(is_premium=True)
    assert "/pricing" not in html


def test_links_are_optional():
    html = render(app_url="", contact_email="")
    assert "Sign up here" not in html

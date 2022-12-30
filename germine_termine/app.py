from jetforce import GeminiServer, JetforceApplication, Response, Status
from icalevents.icalparser import parse_events
from datetime import datetime
import requests
import re
from pathlib import Path
import os

from .utils import timed_lru_cache


app = JetforceApplication()

ROOT_DIR = Path(__file__).parent.parent
HOST = os.environ.get("GERMINE_HOST", "127.0.0.1")
HOSTNAME = os.environ.get("GERMINE_HOSTNAME", "localhost")
DATEFORMAT_DAY = os.environ.get("GERMINE_DATEFORMAT_DAY", "%a, %d.%m.%y")
DATEFORMAT_EVENT = os.environ.get("GERMINE_DATEFORMAT_DAY", "%H:%Mh")
CAL_URL = os.environ.get("GERMINE_CAL_URL")
TEMPLATE_HEADER = (ROOT_DIR / "templates" / "header.gmi").read_text()
TEMPLATE_SEARCH = (ROOT_DIR / "templates" / "search.gmi").read_text()
TEMPLATE_FOOTER = (ROOT_DIR / "templates" / "footer.gmi").read_text()
SEARCH_INPUT_MESSAGE = os.environ.get(
    "GERMINE_SEARCH_INPUT_MESSAGE",
    "Search query (searches in event summary and location)",
)


@timed_lru_cache(seconds=3600)
@app.route("", strict_trailing_slash=False)
def index(request):
    events = __get_events()
    content = TEMPLATE_HEADER
    content += __generate_events_content(events)
    content += TEMPLATE_FOOTER

    return Response(Status.SUCCESS, "text/gemini", content)


@app.route("/search")
@app.route("/search/(?P<query>[a-z]+)")
def search(request):
    search_term = request.query
    if not search_term:
        return Response(Status.INPUT, SEARCH_INPUT_MESSAGE)

    events = __get_events()

    filtered_events = filter(
        lambda e, s=search_term: re.search(s, e.location, re.IGNORECASE)
        or re.search(s, e.summary, re.IGNORECASE),
        events,
    )
    content = TEMPLATE_HEADER
    content += TEMPLATE_SEARCH.format(search_term=search_term)
    content += __generate_events_content(filtered_events)
    content += TEMPLATE_FOOTER

    return Response(Status.SUCCESS, "text/gemini", content)


@timed_lru_cache(seconds=3600)
def __get_events():
    file = requests.get(CAL_URL)
    file.encoding = file.apparent_encoding
    file_content = file.text

    return parse_events(file_content)


def __generate_events_content(events):
    content = ""
    day_prev = ""
    for event in events:
        start_time = datetime.strftime(event.start, DATEFORMAT_EVENT)
        day = datetime.strftime(event.start, DATEFORMAT_DAY)

        if not day == day_prev:
            content += f"\n## {day}\n"
            day_prev = day

        content += f"\n### {start_time} - {event.summary}\n"
        if event.description:
            description = event.description.replace("&nbsp;", " ").replace(r"\r", "")
            content += f"\n{description}\n"
        if event.location:
            content += f"\n{event.location}\n"
        if event.url:
            content += f"\n=> {event.url} URL\n"

    return content


if __name__ == "__main__":
    server = GeminiServer(app, host=HOST, hostname=HOSTNAME)
    server.run()

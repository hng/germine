from jetforce import GeminiServer, JetforceApplication, Response, Status
from icalevents.icalparser import parse_events
from datetime import datetime
import requests
import re

from .utils import timed_lru_cache


app = JetforceApplication()

CAL_URL = "https://hermine-termine.net/hermine/static/ics/hermine.ics"


@timed_lru_cache(seconds=3600)
@app.route("", strict_trailing_slash=False)
def index(request):
    events = __get_events()
    content = """
# Germine Termine

Ein Gemini-Mirror für Hermine Termine.

> ... hermine ist ein Terminkalender in erster Linie fürs Ruhrgebiet, Düsseldorf und Umgebung. Auf Hermine findet ihr politische Veranstaltungen, Konzerte, Partys und alles Mögliche andere, was von Gruppen oder auch Einzelpersonen organisiert wird. Hermine ist unkommerziell und Gegnerin des Kapitalismus. Hermine will vernetzen, politische Kräfte bündeln und Spass fördern.

=> https://hermine-termine.net

=> /search 🔎 Suche

"""
    content += __generate_events_content(events)

    return Response(Status.SUCCESS, "text/gemini", content)


@app.route("/search")
@app.route("/search/(?P<query>[a-z]+)")
def search(request):
    search_term = request.query
    if not search_term:
        return Response(
            Status.INPUT, "Suchbegriff eingeben (Durchsucht Titel und Ortsangabe)"
        )

    events = __get_events()

    filtered_events = filter(
        lambda e, s=search_term: re.search(s, e.location, re.IGNORECASE)
        or re.search(s, e.summary, re.IGNORECASE),
        events,
    )
    content = __generate_events_content(filtered_events)

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
        start_time = datetime.strftime(event.start, "%H:%Mh")
        day = datetime.strftime(event.start, "%a, %d.%m.%y")

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
    server = GeminiServer(app)
    server.run()

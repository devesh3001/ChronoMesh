import json
from typing import Iterator
from app.models.events import BaseEvent

def read_events(file_path: str) -> Iterator[BaseEvent]:
    """Reads a JSONL file and yields BaseEvent objects."""
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            yield BaseEvent(**data)

def stream_events_ordered(live_stream_path: str) -> Iterator[BaseEvent]:
    """
    Simulates a live stream by reading events.
    For evaluation, we may want to process them in ingestion_time order,
    but here we simply read them line by line from the jsonl.
    """
    events = list(read_events(live_stream_path))
    # Sort by ingestion time to simulate real-world arrival order
    events.sort(key=lambda x: x.ingestion_time)
    for event in events:
        yield event

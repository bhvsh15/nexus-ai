from dataclasses import dataclass, field


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def split_sentences(text: str) -> list[str]:
    cleaned = normalize_text(text)
    if not cleaned:
        return []
    return [part.strip() for part in cleaned.replace("!", ".").replace("?", ".").split(".") if part.strip()]


@dataclass
class Note:
    title: str
    body: str
    tags: list[str] = field(default_factory=list)

    def summary(self) -> str:
        first_line = split_sentences(self.body)
        return first_line[0] if first_line else ""


class NoteBook:
    def __init__(self) -> None:
        self._notes: list[Note] = []

    def add(self, note: Note) -> None:
        self._notes.append(note)

    def list_titles(self) -> list[str]:
        return [note.title for note in self._notes]


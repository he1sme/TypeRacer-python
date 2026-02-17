import re
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from typingtest.models import Work, Passage

def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Убираем очень “мусорные” строки (часто в txt бывают номера страниц)
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
    return text.strip()

def chunk_text(text: str, target_chars=650, min_chars=450):
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    buf = ""
    for p in paras:
        if not buf:
            buf = p
        elif len(buf) + 2 + len(p) <= target_chars:
            buf += "\n\n" + p
        else:
            if len(buf) >= min_chars:
                yield buf
            buf = p
    if buf and len(buf) >= min_chars:
        yield buf

class Command(BaseCommand):
    help = "Import a .txt public-domain work and split into passages."

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to .txt file")
        parser.add_argument("--title", type=str, required=True)
        parser.add_argument("--author", type=str, default="")
        parser.add_argument("--lang", type=str, default="ru")
        parser.add_argument("--source", type=str, default="public domain")
        parser.add_argument("--target", type=int, default=650)
        parser.add_argument("--min", type=int, default=450)

    def handle(self, *args, **opts):
        path = Path(opts["file"])
        if not path.exists():
            raise CommandError("File not found")

        raw = path.read_text(encoding="utf-8", errors="ignore")
        text = normalize(raw)

        work, _ = Work.objects.get_or_create(
            title=opts["title"],
            author=opts["author"],
            language=opts["lang"],
            defaults={"source": opts["source"]},
        )
        if opts["source"] and not work.source:
            work.source = opts["source"]
            work.save(update_fields=["source"])

        created = 0
        for chunk in chunk_text(text, target_chars=opts["target"], min_chars=opts["min"]):
            Passage.objects.create(work=work, text=chunk)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Done. Created {created} passages for '{work}'"))

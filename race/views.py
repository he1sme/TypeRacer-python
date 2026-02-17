import secrets
import string

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from typingtest.models import Passage
from .models import RaceRoom
from .utils import make_word_chunk


def _ensure_guest(request):
    if request.user.is_authenticated:
        return
    if not request.session.get("guest_id"):
        request.session["guest_id"] = secrets.token_hex(8)
        request.session.modified = True
    if not request.session.get("guest_name"):
        request.session["guest_name"] = "Guest"
        request.session.modified = True


def _participant(request):
    if request.user.is_authenticated:
        return {
            "id": f"user:{request.user.id}",
            "name": request.user.get_username(),
            "is_guest": False,
        }
    _ensure_guest(request)
    return {
        "id": f"guest:{request.session['guest_id']}",
        "name": request.session["guest_name"],
        "is_guest": True,
    }


def _new_code():
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(6))


@require_http_methods(["GET", "POST"])
def race_home(request):
    _ensure_guest(request)

    if request.method == "POST":
        if not request.user.is_authenticated:
            name = (request.POST.get("guest_name") or "").strip()
            if name:
                request.session["guest_name"] = name[:20]
                request.session.modified = True

        passage = Passage.objects.select_related("work").order_by("?").first()
        if passage is None:
            return render(request, "race/empty.html")

        chunk, start_idx = make_word_chunk(passage.text, words_target=60, start=None)

        code = _new_code()
        while RaceRoom.objects.filter(code=code).exists():
            code = _new_code()

        room = RaceRoom.objects.create(
            code=code,
            created_by=request.user if request.user.is_authenticated else None,
            passage=passage,
            chunk_text=chunk,
            chunk_start=start_idx,
            duration_sec=60,  # поле модели оставлено, но в гонке таймер не используется
        )
        return redirect("race_room", code=room.code)

    rooms = RaceRoom.objects.select_related("passage__work").order_by("-created_at")[:20]
    return render(request, "race/home.html", {"rooms": rooms, "participant": _participant(request)})


def race_room(request, code: str):
    _ensure_guest(request)
    room = get_object_or_404(RaceRoom.objects.select_related("passage__work"), code=code.upper())
    return render(request, "race/room.html", {"room": room, "participant": _participant(request)})

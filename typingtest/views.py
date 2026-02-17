import json
import random
from datetime import timedelta

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

import re
from .forms import SignUpForm
from .models import Passage, TypingResult


def _random_passage(language: str | None = None, min_chars: int | None = None, max_chars: int | None = None):
    qs = Passage.objects.select_related("work")
    if language:
        qs = qs.filter(work__language=language)
    if min_chars is not None:
        qs = qs.filter(chars_count__gte=min_chars)
    if max_chars is not None:
        qs = qs.filter(chars_count__lte=max_chars)

    total = qs.count()
    if total == 0:
        return None
    # Random offset (better than order_by('?') for large tables)
    idx = random.randint(0, total - 1)
    return qs[idx]


def home(request):
    total_passages = Passage.objects.count()
    total_works = Passage.objects.values("work_id").distinct().count()
    total_results = TypingResult.objects.count()
    return render(request, "typingtest/home.html", {
        "total_passages": total_passages,
        "total_works": total_works,
        "total_results": total_results,
    })


def _make_word_chunk(text: str, words_target: int = 60, start: int | None = None) -> tuple[str, int]:
    """Return (chunk, start_index). Chunk is built from word tokens, preserving normal spacing."""
    words = [w for w in re.split(r"\s+", text.replace("\n", " ").strip()) if w]
    if not words:
        return ("", 0)

    if len(words) <= words_target:
        return (" ".join(words), 0)

    if start is None:
        start = random.randint(0, max(0, len(words) - words_target))
    else:
        start = max(0, min(int(start), max(0, len(words) - words_target)))

    chunk = " ".join(words[start:start + words_target])
    return (chunk, start)


def test(request):
    qs = Passage.objects.select_related("work")
    if not qs.exists():
        return render(request, "typingtest/empty.html")

    # Repeat exact same chunk: ?p=<passage_id>&start=<word_index>
    p = request.GET.get("p")
    start = request.GET.get("start")

    passage = None
    if p:
        try:
            passage = qs.filter(id=int(p)).first()
        except Exception:
            passage = None

    if passage is None:
        total = qs.count()
        passage = qs[random.randint(0, total - 1)]

    chunk, start_idx = _make_word_chunk(passage.text, words_target=60, start=start)

    return render(request, "typingtest/test.html", {
        "passage": passage,
        "chunk": chunk,
        "chunk_start": start_idx,
    })


    # Deterministic "repeat same text": ?p=<passage_id>&start=<word_index>&w=<words_target>
    p = request.GET.get("p")
    start = request.GET.get("start")
    words_target = request.GET.get("w")

    try:
        words_target_i = int(words_target) if words_target else 60
        words_target_i = max(10, min(words_target_i, 200))
    except Exception:
        words_target_i = 60

    passage = None
    if p:
        try:
            passage = qs.filter(id=int(p)).first()
        except Exception:
            passage = None

    if passage is None:
        total = qs.count()
        passage = qs[random.randint(0, total - 1)]

    chunk, start_idx = _make_word_chunk(passage.text, words_target=words_target_i, start=start)

    return render(request, "typingtest/test.html", {
        "passage": passage,
        "chunk": chunk,
        "chunk_start": start_idx,
        "words_target": words_target_i,
    })


    # Берём любой пассаж (хоть огромный) и вырезаем короткий кусок слов как в Monkeytype
    total = qs.count()
    passage = qs[random.randint(0, total - 1)]
    chunk = _make_word_chunk(passage.text, words_target=60)

    return render(request, "typingtest/test.html", {
        "passage": passage,
        "chunk": chunk,
    })


    if not passage:
        return render(request, "typingtest/empty.html")

    return render(request, "typingtest/test.html", {
        "passage": passage,
        "difficulty": difficulty,
        "lang": lang,
    })


@require_POST
def submit_result(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        passage_id = int(data["passage_id"])
        duration_ms = int(data["duration_ms"])
        typed_chars = int(data["typed_chars"])
        correct_chars = int(data["correct_chars"])
        errors = int(data["errors"])
        wpm = float(data["wpm"])
        cpm = float(data["cpm"])
        accuracy = float(data["accuracy"])
    except Exception:
        return HttpResponseBadRequest("Bad payload")

    passage = Passage.objects.filter(id=passage_id).first()
    if not passage:
        return JsonResponse({"ok": False, "error": "Passage not found"}, status=404)

    user = request.user if request.user.is_authenticated else None
    r = TypingResult.objects.create(
        user=user,
        passage=passage,
        duration_ms=max(duration_ms, 1),
        typed_chars=max(typed_chars, 0),
        correct_chars=max(correct_chars, 0),
        errors=max(errors, 0),
        wpm=max(wpm, 0.0),
        cpm=max(cpm, 0.0),
        accuracy=min(max(accuracy, 0.0), 100.0),
    )
    return JsonResponse({"ok": True, "result_id": r.id})


def leaderboard(request):
    mode = request.GET.get("mode", "all")  # all / week
    qs = TypingResult.objects.select_related("user").order_by("-wpm")

    if mode == "week":
        since = timezone.now() - timedelta(days=7)
        qs = qs.filter(created_at__gte=since)

    top = qs[:50]
    avg = qs.aggregate(avg_wpm=Avg("wpm"), avg_acc=Avg("accuracy"), total=Count("id"))
    return render(request, "typingtest/leaderboard.html", {"top": top, "avg": avg, "mode": mode})


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
    else:
        form = SignUpForm()
    return render(request, "typingtest/signup.html", {"form": form})


@login_required
def profile(request):
    qs = TypingResult.objects.filter(user=request.user).order_by("-created_at")
    recent = qs[:20]
    stats = qs.aggregate(
        total=Count("id"),
        best_wpm=Max("wpm"),
        avg_wpm=Avg("wpm"),
        avg_acc=Avg("accuracy"),
    )
    return render(request, "typingtest/profile.html", {"recent": recent, "stats": stats})

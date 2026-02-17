import json
import time

from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import RaceRoom, RaceResult

STATE_TTL = 60 * 60  # 1 hour


def _state_key(code: str) -> str:
    return f"race_state:{code}"


def _now_ms() -> int:
    return int(time.time() * 1000)


class RaceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.code = self.scope["url_route"]["kwargs"]["code"].upper()
        self.group = f"race_{self.code}"

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        self.pid, self.name, self.is_guest = self._identify()

        state = cache.get(_state_key(self.code)) or {
            "started": False,
            "start_ms": None,
            "players": {},
        }

        state["players"].setdefault(
            self.pid,
            {
                "name": self.name,
                "progress": 0.0,
                "ready": False,
                "finished": False,
                "wpm": 0.0,
                "accuracy": 100.0,
                "errors": 0,
                "is_guest": self.is_guest,
            },
        )

        cache.set(_state_key(self.code), state, STATE_TTL)
        await self._broadcast_state()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

        state = cache.get(_state_key(self.code))
        if not state:
            return

        # remove player from room state on disconnect
        if self.pid in state.get("players", {}):
            state["players"].pop(self.pid, None)

        # if nobody left -> delete room + state
        if not state.get("players"):
            cache.delete(_state_key(self.code))
            try:
                room = await RaceRoom.objects.aget(code=self.code)
                await room.adelete()
            except Exception:
                pass
            return

        cache.set(_state_key(self.code), state, STATE_TTL)
        await self._broadcast_state()

    def _identify(self):
        user = self.scope.get("user")
        if user and not isinstance(user, AnonymousUser) and getattr(user, "is_authenticated", False):
            return (f"user:{user.id}", user.get_username(), False)

        session = self.scope.get("session")
        guest_id = session.get("guest_id") if session else None
        guest_name = session.get("guest_name") if session else None
        if not guest_id:
            guest_id = f"tmp_{_now_ms()}"
        if not guest_name:
            guest_name = "Guest"
        return (f"guest:{guest_id}", guest_name, True)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except Exception:
            return

        msg_type = data.get("type")

        state = cache.get(_state_key(self.code)) or {
            "started": False,
            "start_ms": None,
            "players": {},
        }

        state["players"].setdefault(
            self.pid,
            {
                "name": self.name,
                "progress": 0.0,
                "ready": False,
                "finished": False,
                "wpm": 0.0,
                "accuracy": 100.0,
                "errors": 0,
                "is_guest": self.is_guest,
            },
        )

        if msg_type == "set_name" and self.is_guest:
            new_name = (data.get("name") or "").strip()[:20]
            if new_name:
                state["players"][self.pid]["name"] = new_name

        elif msg_type == "ready":
            if not state.get("started"):
                state["players"][self.pid]["ready"] = bool(data.get("ready"))

                # Auto-start when 2+ players and everyone is ready
                if len(state["players"]) >= 2 and all(p.get("ready") for p in state["players"].values()):
                    state["started"] = True
                    state["start_ms"] = _now_ms()

                    for p in state["players"].values():
                        p["progress"] = 0.0
                        p["finished"] = False
                        p["wpm"] = 0.0
                        p["accuracy"] = 100.0
                        p["errors"] = 0

        elif msg_type == "progress":
            if state.get("started") and not state["players"][self.pid].get("finished"):
                prog = float(data.get("progress") or 0.0)
                prog = max(0.0, min(1.0, prog))
                state["players"][self.pid]["progress"] = prog
                state["players"][self.pid]["wpm"] = float(data.get("wpm") or 0.0)
                state["players"][self.pid]["accuracy"] = float(data.get("accuracy") or 100.0)
                state["players"][self.pid]["errors"] = int(data.get("errors") or 0)

        elif msg_type == "finish":
            if state.get("started"):
                state["players"][self.pid]["finished"] = True
                state["players"][self.pid]["progress"] = 1.0
                state["players"][self.pid]["wpm"] = float(data.get("wpm") or state["players"][self.pid].get("wpm") or 0.0)
                state["players"][self.pid]["accuracy"] = float(data.get("accuracy") or state["players"][self.pid].get("accuracy") or 100.0)
                state["players"][self.pid]["errors"] = int(data.get("errors") or state["players"][self.pid].get("errors") or 0)

                # Save results only for authenticated users
                user = self.scope.get("user")
                if user and not isinstance(user, AnonymousUser) and getattr(user, "is_authenticated", False):
                    try:
                        room = await RaceRoom.objects.aget(code=self.code)
                        await RaceResult.objects.acreate(
                            room=room,
                            user=user,
                            duration_ms=int(data.get("duration_ms") or 0),
                            typed_chars=int(data.get("typed_chars") or 0),
                            correct_chars=int(data.get("correct_chars") or 0),
                            errors=int(data.get("errors") or 0),
                            wpm=float(data.get("wpm") or 0.0),
                            cpm=float(data.get("cpm") or 0.0),
                            accuracy=float(data.get("accuracy") or 0.0),
                        )
                    except Exception:
                        pass

        cache.set(_state_key(self.code), state, STATE_TTL)
        await self._broadcast_state()

    async def _broadcast_state(self):
        state = cache.get(_state_key(self.code)) or {}
        payload = {
            "type": "state",
            "started": bool(state.get("started")),
            "start_ms": state.get("start_ms"),
            "players": state.get("players", {}),
            "server_ms": _now_ms(),
        }
        await self.channel_layer.group_send(self.group, {"type": "race.message", "text": json.dumps(payload)})

    async def race_message(self, event):
        await self.send(text_data=event["text"])

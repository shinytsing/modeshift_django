"""Small optional gRPC facade for LifeOS goal operations.

The wire format is UTF-8 JSON so clients can call it without generated
protobuf code while the public API remains stable. Run with
``python -m apps.tools.grpc_lifeos``.
"""
import json
import os

import django
import grpc
from concurrent import futures

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()

from .models import LifeGoal


def _json(value):
    return json.dumps(value, ensure_ascii=False).encode()


def _decode(value):
    return json.loads(value.decode() or "{}")


def create_goal(request, context):
    data = _decode(request)
    if not data.get("title"):
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, "title is required")
    goal = LifeGoal.objects.create(
        user_id=int(data.get("user_id", 1)),
        title=data["title"],
        description=data.get("description", ""),
        category=data.get("category", "personal"),
        goal_type=data.get("goal_type", "daily"),
    )
    return _json({"id": goal.id, "title": goal.title, "category": goal.category})


def list_goals(request, context):
    data = _decode(request)
    goals = LifeGoal.objects.filter(user_id=int(data.get("user_id", 1))).values("id", "title", "category", "status")
    return _json({"goals": list(goals)})


def serve(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    handlers = grpc.method_handlers_generic_handler("lifeos.LifeOS", {
        "CreateGoal": grpc.unary_unary_rpc_method_handler(create_goal, request_deserializer=lambda x: x, response_serializer=lambda x: x),
        "ListGoals": grpc.unary_unary_rpc_method_handler(list_goals, request_deserializer=lambda x: x, response_serializer=lambda x: x),
    })
    server.add_generic_rpc_handlers((handlers,))
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"LifeOS gRPC listening on :{port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve(int(os.getenv("LIFEOS_GRPC_PORT", "50051")))

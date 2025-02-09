import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from app.main import app
import json
from datetime import datetime

client = TestClient(app)

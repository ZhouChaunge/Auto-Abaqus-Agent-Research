#!/usr/bin/env python3
"""Gemini review MCP server for Codex-first workflows.

This server mirrors the narrow review-only interface used by the existing
review bridges, but defaults to the direct Gemini API so Codex can reuse the
original ARIS review-heavy skill structure with minimal changes. Gemini CLI is
kept only as an optional fallback. It is intentionally self-contained so it can
be copied into `~/.codex/mcp-servers/gemini-review/` without depending on this
repository.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


sys.stdout = os.fdopen(sys.stdout.fileno(), "wb", buffering=0)
sys.stdin = os.fdopen(sys.stdin.fileno(), "rb", buffering=0)

SERVER_NAME = os.environ.get("GEMINI_REVIEW_SERVER_NAME", "gemini-review")
GEMINI_BIN = os.environ.get("GEMINI_BIN", "gemini")
DEFAULT_MODEL = os.environ.get("GEMINI_REVIEW_MODEL", "")
DEFAULT_SYSTEM = os.environ.get("GEMINI_REVIEW_SYSTEM", "")
DEFAULT_BACKEND = os.environ.get("GEMINI_REVIEW_BACKEND", "api")
DEFAULT_TIMEOUT_SEC = int(os.environ.get("GEMINI_REVIEW_TIMEOUT_SEC", "600"))
DEFAULT_API_MODEL = os.environ.get("GEMINI_REVIEW_API_MODEL", "gemini-2.5-flash")
DEBUG_LOG = Path(os.environ.get("GEMINI_REVIEW_DEBUG_LOG", f"/tmp/{SERVER_NAME}-mcp-debug.log"))
STATE_DIR = Path(
    os.environ.get(
        "GEMINI_REVIEW_STATE_DIR",
        str(Path.home() / ".codex" / "state" / SERVER_NAME),
    )
)
JOBS_DIR = STATE_DIR / "jobs"
THREADS_DIR = STATE_DIR / "threads"

_use_ndjson = False
TERMINAL_JOB_STATES = {"completed", "failed"}


def debug_log(message: str) -> None:
    try:
        DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with DEBUG_LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"{message}\n")
    except OSError:
        pass


def send_response(response: dict[str, Any]) -> None:
    global _use_ndjson

    payload = json.dumps(response, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    debug_log(f"SEND {payload.decode('utf-8', errors='replace')}")
    if _use_ndjson:
        sys.stdout.write(payload + b"\n")
    else:
        header = f"Content-Length: {len(payload)}\r\n\r\n".encode("utf-8")
        sys.stdout.write(header + payload)
    sys.stdout.flush()


def read_message() -> dict[str, Any] | None:
    global _use_ndjson

    line = sys.stdin.readline()
    if not line:
        return None

    line_text = line.decode("utf-8").rstrip("\r\n")
    if line_text.lower().startswith("content-length:"):
        try:
            content_length = int(line_text.split(":", 1)[1].strip())
        except ValueError:
            return None

        while True:
            header_line = sys.stdin.readline()
            if not header_line:
                return None
            if header_line in {b"\r\n", b"\n"}:
                break

        body = sys.stdin.read(content_length)
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    if line_text.startswith("{") or line_text.startswith("["):
        _use_ndjson = True
        try:
            return json.loads(line_text)
        except json.JSONDecodeError:
            return None

    return None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_private_env_file(env_file: Path | None = None) -> list[str]:
    target = env_file or (Path.home() / ".gemini" / ".env")
    if not target.is_file():
        return []

    loaded: list[str] = []
    for raw_line in target.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return loaded


def normalize_image_paths(raw_value: Any) -> tuple[list[str], str | None]:
    if raw_value is None:
        return [], None
    if isinstance(raw_value, str):
        candidate = raw_value.strip()
        return ([candidate] if candidate else []), None
    if not isinstance(raw_value, list):
        return [], "imagePaths must be a string or an array of strings"

    image_paths: list[str] = []
    for item in raw_value:
        if not isinstance(item, str):
            return [], "imagePaths entries must be strings"
        candidate = item.strip()
        if candidate:
            image_paths.append(candidate)
    return image_paths, None


def build_inline_image_parts(image_paths: list[str]) -> tuple[list[dict[str, Any]], str | None]:
    parts: list[dict[str, Any]] = []
    for raw_path in image_paths:
        path = Path(raw_path).expanduser()
        if not path.is_file():
            return [], f"image file not found: {raw_path}"
        mime_type, _ = mimetypes.guess_type(path.name)
        if not mime_type or not mime_type.startswith("image/"):
            return [], f"unsupported image type for Gemini review: {raw_path}"
        try:
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        except OSError as exc:
            return [], f"failed to read image file {raw_path}: {exc}"
        parts.append({"inlineData": {"mimeType": mime_type, "data": encoded}})
    return parts, None


def find_gemini_bin() -> str | None:
    if Path(GEMINI_BIN).is_file():
        return GEMINI_BIN
    return shutil.which(GEMINI_BIN)


def resolve_backend(preferred_backend: str | None) -> str:
    backend = preferred_backend or DEFAULT_BACKEND
    if backend not in {"auto", "api", "cli"}:
        raise ValueError(f"unsupported Gemini backend: {backend}")
    if backend == "auto":
        return "api" if get_api_key() else "cli"
    return backend


def get_api_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def parse_gemini_json(raw_stdout: str) -> tuple[dict[str, Any] | None, str | None]:
    lines = [line.strip() for line in raw_stdout.splitlines() if line.strip()]
    if not lines:
        return None, "Gemini CLI returned empty output"

    for candidate in reversed(lines):
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload, None

    return None, "Gemini CLI did not return JSON output"


def extract_cli_error_message(raw_stdout: str, raw_stderr: str) -> str:
    for text in (raw_stdout, raw_stderr):
        stripped = text.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            return stripped
        if not isinstance(payload, dict):
            return stripped
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()
        response = payload.get("response")
        if isinstance(response, str) and response.strip():
            return response.strip()
        return stripped
    return "unknown error"


def extract_api_response_text(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates")
    if isinstance(candidates, list):
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            content = candidate.get("content")
            if not isinstance(content, dict):
                continue
            parts = content.get("parts")
            if not isinstance(parts, list):
                continue
            texts: list[str] = []
            for part in parts:
                if isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str):
                        texts.append(text)
            if texts:
                return "\n".join(texts).strip()

    prompt_feedback = payload.get("promptFeedback")
    if isinstance(prompt_feedback, dict):
        block_reason = prompt_feedback.get("blockReason")
        if isinstance(block_reason, str) and block_reason:
            raise ValueError(f"Gemini API response blocked: {block_reason}")

    raise ValueError("Gemini API response does not contain candidate text")


def job_state_path(job_id: str) -> Path:
    return JOBS_DIR / f"{job_id}.json"


def thread_state_path(thread_id: str) -> Path:
    return THREADS_DIR / f"{thread_id}.json"


def is_pid_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def serialize_job(job: dict[str, Any]) -> dict[str, Any]:
    result = job.get("result") or {}
    return {
        "jobId": job.get("jobId"),
        "status": job.get("status"),
        "done": job.get("status") in TERMINAL_JOB_STATES,
        "threadId": result.get("threadId"),
        "response": result.get("response"),
        "model": result.get("model"),
        "backend": result.get("backend"),
        "duration_ms": result.get("duration_ms"),
        "stop_reason": result.get("stop_reason"),
        "error": job.get("error"),
        "createdAt": job.get("createdAt"),
        "startedAt": job.get("startedAt"),
        "completedAt": job.get("completedAt"),
        "updatedAt": job.get("updatedAt"),
        "resumeHint": "Call review_status with this jobId until done=true.",
    }


def load_thread_history(thread_id: str) -> list[dict[str, str]]:
    path = thread_state_path(thread_id)
    if not path.exists():
        return []
    payload = read_json(path)
    history = payload.get("history")
    if not isinstance(history, list):
        return []
    result: list[dict[str, str]] = []
    for item in history:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "")).strip()
        text = str(item.get("text", "")).strip()
        if role in {"user", "model"} and text:
            result.append({"role": role, "text": text})
    return result


def save_thread_history(
    *,
    thread_id: str,
    history: list[dict[str, str]],
    model: str,
    backend: str,
) -> None:
    now = utc_now()
    path = thread_state_path(thread_id)
    created_at = now
    if path.exists():
        existing = read_json(path)
        created_at = str(existing.get("createdAt") or now)
    write_json(
        path,
        {
            "threadId": thread_id,
            "createdAt": created_at,
            "updatedAt": now,
            "model": model,
            "backend": backend,
            "history": history,
        },
    )


def build_cli_prompt(
    prompt: str,
    *,
    history: list[dict[str, str]],
    system: str | None,
) -> str:
    selected_system = (system or DEFAULT_SYSTEM).strip()
    if not history and not selected_system:
        return prompt

    sections: list[str] = []
    if selected_system:
        sections.extend(["## System Instructions", selected_system, ""])
    if history:
        sections.append("## Previous Review Conversation")
        for item in history:
            role = "User" if item["role"] == "user" else "Reviewer"
            sections.append(f"### {role}")
            sections.append(item["text"])
            sections.append("")
    sections.extend(["## New User Prompt", prompt])
    return "\n".join(sections).strip()


def run_gemini_cli_review(
    prompt: str,
    *,
    history: list[dict[str, str]],
    model: str | None,
    system: str | None,
    image_paths: list[str],
) -> tuple[dict[str, Any] | None, str | None]:
    if image_paths:
        return None, "Gemini CLI backend in this bridge does not support imagePaths; use backend=api"

    bin_path = find_gemini_bin()
    if not bin_path:
        return None, f"Gemini CLI not found: {GEMINI_BIN}"

    effective_prompt = build_cli_prompt(prompt, history=history, system=system)
    cmd = [bin_path, "-p", effective_prompt, "--output-format", "json"]
    selected_model = model or DEFAULT_MODEL
    if selected_model:
        cmd.extend(["-m", selected_model])

    debug_log(f"RUN {' '.join(cmd)}")
    try:
        started = time.monotonic()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=DEFAULT_TIMEOUT_SEC,
            check=False,
        )
        duration_ms = int((time.monotonic() - started) * 1000)
    except subprocess.TimeoutExpired:
        return None, f"Gemini review timed out after {DEFAULT_TIMEOUT_SEC} seconds"

    payload, parse_error = parse_gemini_json(result.stdout)
    if parse_error:
        stderr = result.stderr.strip()
        message = parse_error if not stderr else f"{parse_error}. stderr: {stderr}"
        return None, message

    if payload is None:
        return None, "Failed to parse Gemini CLI output"
    if result.returncode != 0:
        return None, f"Gemini review failed: {extract_cli_error_message(result.stdout, result.stderr)}"

    response_text = str(payload.get("response", "")).strip()
    if not response_text:
        return None, "Gemini CLI JSON payload does not contain a non-empty response field"

    return {
        "response": response_text,
        "model": payload.get("model", "") or selected_model or "gemini-cli",
        "duration_ms": duration_ms,
        "stop_reason": payload.get("stop_reason"),
        "backend": "cli",
    }, None


def run_gemini_api_review(
    prompt: str,
    *,
    history: list[dict[str, str]],
    model: str | None,
    system: str | None,
    image_paths: list[str],
) -> tuple[dict[str, Any] | None, str | None]:
    api_key = get_api_key()
    if not api_key:
        return None, "Gemini API backend requires GEMINI_API_KEY or GOOGLE_API_KEY"

    selected_model = model or DEFAULT_MODEL or DEFAULT_API_MODEL
    request_payload: dict[str, Any] = {
        "contents": [],
        "generationConfig": {"temperature": 0.2},
    }
    selected_system = (system or DEFAULT_SYSTEM).strip()
    if selected_system:
        request_payload["systemInstruction"] = {"parts": [{"text": selected_system}]}
    for item in history:
        request_payload["contents"].append(
            {
                "role": item["role"],
                "parts": [{"text": item["text"]}],
            }
        )
    user_parts: list[dict[str, Any]] = [{"text": prompt}]
    inline_parts, image_error = build_inline_image_parts(image_paths)
    if image_error:
        return None, image_error
    user_parts.extend(inline_parts)
    request_payload["contents"].append({"role": "user", "parts": user_parts})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent"
    request = urllib.request.Request(
        url,
        data=json.dumps(request_payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    debug_log(f"RUN gemini-api {selected_model}")
    try:
        started = time.monotonic()
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT_SEC) as response:
            raw_stdout = response.read().decode("utf-8")
        duration_ms = int((time.monotonic() - started) * 1000)
    except urllib.error.HTTPError as exc:
        raw_text = exc.read().decode("utf-8", errors="replace")
        message = raw_text.strip()
        try:
            error_payload = json.loads(raw_text)
            if isinstance(error_payload, dict):
                error = error_payload.get("error")
                if isinstance(error, dict):
                    api_message = error.get("message")
                    if isinstance(api_message, str) and api_message.strip():
                        message = api_message.strip()
        except json.JSONDecodeError:
            pass
        return None, f"Gemini API failed with HTTP {exc.code}: {message or 'unknown error'}"
    except urllib.error.URLError as exc:
        return None, f"Gemini API request failed: {exc.reason}"

    try:
        api_payload = json.loads(raw_stdout)
    except json.JSONDecodeError:
        return None, "Gemini API response is not valid JSON"
    if not isinstance(api_payload, dict):
        return None, "Gemini API response JSON must be an object"

    try:
        response_text = extract_api_response_text(api_payload)
    except ValueError as exc:
        return None, str(exc)

    return {
        "response": response_text,
        "model": selected_model,
        "duration_ms": duration_ms,
        "stop_reason": None,
        "backend": "api",
    }, None


def run_gemini_review(
    prompt: str,
    *,
    session_id: str | None = None,
    model: str | None = None,
    system: str | None = None,
    tools: str | None = None,
    backend: str | None = None,
    image_paths: Any = None,
) -> tuple[dict[str, Any] | None, str | None]:
    del tools

    load_private_env_file()

    normalized_image_paths, image_error = normalize_image_paths(image_paths)
    if image_error:
        return None, image_error

    thread_id = session_id or uuid.uuid4().hex
    history = load_thread_history(thread_id) if session_id else []
    try:
        selected_backend = resolve_backend(backend)
    except ValueError as exc:
        return None, str(exc)

    if selected_backend == "api":
        payload, error = run_gemini_api_review(
            prompt,
            history=history,
            model=model,
            system=system,
            image_paths=normalized_image_paths,
        )
    else:
        payload, error = run_gemini_cli_review(
            prompt,
            history=history,
            model=model,
            system=system,
            image_paths=normalized_image_paths,
        )
    if error:
        return None, error

    if payload is None:
        return None, "Failed to parse Gemini CLI output"
    updated_history = list(history)
    updated_history.append({"role": "user", "text": prompt})
    updated_history.append({"role": "model", "text": str(payload["response"])})
    save_thread_history(
        thread_id=thread_id,
        history=updated_history,
        model=str(payload["model"]),
        backend=str(payload["backend"]),
    )
    payload["threadId"] = thread_id
    return payload, None


def start_async_review(
    prompt: str,
    *,
    session_id: str | None = None,
    model: str | None = None,
    system: str | None = None,
    tools: str | None = None,
    backend: str | None = None,
    image_paths: Any = None,
) -> tuple[dict[str, Any] | None, str | None]:
    normalized_image_paths, image_error = normalize_image_paths(image_paths)
    if image_error:
        return None, image_error

    job_id = uuid.uuid4().hex
    created_at = utc_now()
    job = {
        "jobId": job_id,
        "status": "queued",
        "createdAt": created_at,
        "startedAt": None,
        "completedAt": None,
        "updatedAt": created_at,
        "error": None,
        "result": None,
        "workerPid": None,
        "request": {
            "prompt": prompt,
            "threadId": session_id,
            "model": model,
            "system": system,
            "tools": tools,
            "backend": backend,
            "imagePaths": normalized_image_paths,
        },
    }

    job_path = job_state_path(job_id)
    write_json(job_path, job)

    try:
        worker = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--run-job", job_id],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True,
        )
    except OSError as exc:
        job["status"] = "failed"
        job["completedAt"] = utc_now()
        job["updatedAt"] = job["completedAt"]
        job["error"] = f"Failed to launch background review worker: {exc}"
        write_json(job_path, job)
        return None, job["error"]

    job["workerPid"] = worker.pid
    job["updatedAt"] = utc_now()
    write_json(job_path, job)
    debug_log(f"JOB_START job_id={job_id} worker_pid={worker.pid}")
    return serialize_job(job), None


def get_review_status(job_id: str, *, wait_seconds: int = 0) -> tuple[dict[str, Any] | None, str | None]:
    job_path = job_state_path(job_id)
    if not job_path.exists():
        return None, f"Unknown jobId: {job_id}"

    deadline = time.monotonic() + max(wait_seconds, 0)
    while True:
        job = read_json(job_path)
        if job.get("status") in {"queued", "running"} and not is_pid_alive(job.get("workerPid")):
            job["status"] = "failed"
            job["error"] = "Background review worker exited before writing a final result"
            job["completedAt"] = utc_now()
            job["updatedAt"] = job["completedAt"]
            write_json(job_path, job)
        if job.get("status") in TERMINAL_JOB_STATES:
            return serialize_job(job), None
        if time.monotonic() >= deadline:
            return serialize_job(job), None
        time.sleep(min(0.5, max(deadline - time.monotonic(), 0.0)))


def run_async_job(job_id: str) -> int:
    job_path = job_state_path(job_id)
    if not job_path.exists():
        debug_log(f"JOB_MISSING job_id={job_id}")
        return 1

    job = read_json(job_path)
    job["status"] = "running"
    job["startedAt"] = utc_now()
    job["updatedAt"] = job["startedAt"]
    job["workerPid"] = os.getpid()
    write_json(job_path, job)
    debug_log(f"JOB_RUNNING job_id={job_id} worker_pid={os.getpid()}")

    request = job.get("request") or {}
    try:
        payload, error = run_gemini_review(
            str(request.get("prompt", "")),
            session_id=request.get("threadId"),
            model=request.get("model"),
            system=request.get("system"),
            tools=request.get("tools"),
            backend=request.get("backend"),
            image_paths=request.get("imagePaths"),
        )
    except Exception as exc:
        payload = None
        error = f"Background review crashed: {exc}"
        debug_log(traceback.format_exc())

    finished_at = utc_now()
    job = read_json(job_path)
    job["updatedAt"] = finished_at
    job["completedAt"] = finished_at
    if error:
        job["status"] = "failed"
        job["error"] = error
        job["result"] = None
        debug_log(f"JOB_FAILED job_id={job_id} error={error}")
        write_json(job_path, job)
        return 1

    job["status"] = "completed"
    job["error"] = None
    job["result"] = payload
    debug_log(f"JOB_COMPLETED job_id={job_id} thread_id={(payload or {}).get('threadId')}")
    write_json(job_path, job)
    return 0


def tool_success(request_id: Any, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        },
    }


def tool_error(request_id: Any, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "content": [{"type": "text", "text": json.dumps({"error": message}, ensure_ascii=False)}],
            "isError": True,
        },
    }


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    request_id = request.get("id")
    method = request.get("method", "")
    params = request.get("params", {})
    debug_log(f"REQUEST id={request_id!r} method={method} params={json.dumps(params, ensure_ascii=False)}")

    if request_id is None:
        if method in {"notifications/initialized", "initialized"}:
            return None
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": "1.0.0"},
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}

    if method == "resources/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": []}}

    if method == "resources/templates/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"resourceTemplates": []}}

    if method in {"notifications/initialized", "initialized"}:
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}

    if method == "tools/list":
        common_properties = {
            "prompt": {"type": "string", "description": "Reviewer prompt"},
            "system": {"type": "string", "description": "Optional system prompt"},
            "model": {"type": "string", "description": "Optional Gemini model override"},
            "backend": {"type": "string", "description": "Optional Gemini backend override: auto, api, or cli"},
            "tools": {"type": "string", "description": "Accepted for compatibility but ignored by Gemini review"},
            "imagePaths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional local image paths for Gemini API multimodal review",
            },
            "image_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Alias of imagePaths",
            },
        }
        reply_properties = {
            "threadId": {"type": "string", "description": "Gemini thread id from a previous review call"},
            "thread_id": {"type": "string", "description": "Alias of threadId"},
            **common_properties,
        }
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "review",
                        "description": "Run a fresh Gemini review and return JSON containing threadId and response.",
                        "inputSchema": {
                            "type": "object",
                            "properties": common_properties,
                            "required": ["prompt"],
                        },
                    },
                    {
                        "name": "review_reply",
                        "description": "Continue a previous Gemini review session using threadId.",
                        "inputSchema": {
                            "type": "object",
                            "properties": reply_properties,
                            "required": ["prompt"],
                        },
                    },
                    {
                        "name": "review_start",
                        "description": "Start a background Gemini review job and return a resumable jobId immediately.",
                        "inputSchema": {
                            "type": "object",
                            "properties": common_properties,
                            "required": ["prompt"],
                        },
                    },
                    {
                        "name": "review_reply_start",
                        "description": "Start a background follow-up review job in an existing Gemini thread and return a resumable jobId immediately.",
                        "inputSchema": {
                            "type": "object",
                            "properties": reply_properties,
                            "required": ["prompt"],
                        },
                    },
                    {
                        "name": "review_status",
                        "description": "Check whether a background review job has finished and fetch the final result when available.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "jobId": {"type": "string", "description": "Background review job id"},
                                "job_id": {"type": "string", "description": "Alias of jobId"},
                                "waitSeconds": {"type": "integer", "description": "Optional bounded wait before returning status"},
                            },
                            "required": ["jobId"],
                        },
                    },
                ]
            },
        }

    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {}) or {}

        if name == "review":
            payload, error = run_gemini_review(
                str(args.get("prompt", "")),
                model=args.get("model"),
                system=args.get("system"),
                tools=args.get("tools"),
                backend=args.get("backend"),
                image_paths=args.get("imagePaths") or args.get("image_paths"),
            )
            return tool_error(request_id, error) if error else tool_success(request_id, payload or {})

        if name == "review_reply":
            thread_id = args.get("threadId") or args.get("thread_id")
            if not thread_id:
                return tool_error(request_id, "threadId or thread_id is required")
            payload, error = run_gemini_review(
                str(args.get("prompt", "")),
                session_id=str(thread_id),
                model=args.get("model"),
                system=args.get("system"),
                tools=args.get("tools"),
                backend=args.get("backend"),
                image_paths=args.get("imagePaths") or args.get("image_paths"),
            )
            return tool_error(request_id, error) if error else tool_success(request_id, payload or {})

        if name == "review_start":
            payload, error = start_async_review(
                str(args.get("prompt", "")),
                model=args.get("model"),
                system=args.get("system"),
                tools=args.get("tools"),
                backend=args.get("backend"),
                image_paths=args.get("imagePaths") or args.get("image_paths"),
            )
            return tool_error(request_id, error) if error else tool_success(request_id, payload or {})

        if name == "review_reply_start":
            thread_id = args.get("threadId") or args.get("thread_id")
            if not thread_id:
                return tool_error(request_id, "threadId or thread_id is required")
            payload, error = start_async_review(
                str(args.get("prompt", "")),
                session_id=str(thread_id),
                model=args.get("model"),
                system=args.get("system"),
                tools=args.get("tools"),
                backend=args.get("backend"),
                image_paths=args.get("imagePaths") or args.get("image_paths"),
            )
            return tool_error(request_id, error) if error else tool_success(request_id, payload or {})

        if name == "review_status":
            job_id = args.get("jobId") or args.get("job_id")
            if not job_id:
                return tool_error(request_id, "jobId or job_id is required")
            wait_seconds_raw = args.get("waitSeconds", 0)
            try:
                wait_seconds = int(wait_seconds_raw)
            except (TypeError, ValueError):
                return tool_error(request_id, "waitSeconds must be an integer")
            payload, error = get_review_status(str(job_id), wait_seconds=max(wait_seconds, 0))
            return tool_error(request_id, error) if error else tool_success(request_id, payload or {})

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Unknown tool: {name}"},
        }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--run-job":
        raise SystemExit(run_async_job(sys.argv[2]))

    debug_log(f"=== {SERVER_NAME} starting ===")
    while True:
        try:
            request = read_message()
            if request is None:
                debug_log("EOF")
                break
            response = handle_request(request)
            if response is not None:
                send_response(response)
        except Exception:
            debug_log(traceback.format_exc())
            break


if __name__ == "__main__":
    main()

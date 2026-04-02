import os
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Dict, List, Optional

import jwt
from flask import Flask, jsonify, request
from flasgger import Swagger


app = Flask(__name__)


# Demo config for week6. In production, secret must come from secure env manager.
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "10"))
REFRESH_TOKEN_EXPIRES_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", "7"))


swagger_template: Dict[str, Any] = {
	"swagger": "2.0",
	"info": {
		"title": "Week 6 - Authentication & Authorization API",
		"description": (
			"JWT demo with bearer token, refresh token rotation, scopes and roles.\\n\\n"
			"JWT vs OAuth 2.0 summary:\\n"
			"- JWT: token format (self-contained claims).\\n"
			"- OAuth 2.0: authorization framework/delegation protocol.\\n"
			"- In practice, OAuth 2.0 often issues JWT access tokens."
		),
		"version": "1.0.0",
	},
	"securityDefinitions": {
		"Bearer": {
			"type": "apiKey",
			"name": "Authorization",
			"in": "header",
			"description": "Value format: Bearer <access_token>",
		}
	},
}

Swagger(app, template=swagger_template)


USERS: Dict[str, Dict[str, Any]] = {
	"alice": {
		"password": "alice123",
		"role": "user",
		"scopes": ["users:read"],
	},
	"admin": {
		"password": "admin123",
		"role": "admin",
		"scopes": ["users:read", "users:write", "audit:read"],
	},
}


DATA = {
	"users": [
		{"id": 1, "name": "Alice", "email": "alice@example.com"},
		{"id": 2, "name": "Bob", "email": "bob@example.com"},
	]
}


REFRESH_STORE: Dict[str, Dict[str, Any]] = {}
REVOKED_ACCESS_JTIS = set()


def utc_now() -> datetime:
	return datetime.now(timezone.utc)


def parse_exp_to_datetime(exp_value: Any) -> datetime:
	if isinstance(exp_value, (int, float)):
		return datetime.fromtimestamp(exp_value, tz=timezone.utc)
	if isinstance(exp_value, datetime):
		if exp_value.tzinfo is None:
			return exp_value.replace(tzinfo=timezone.utc)
		return exp_value
	raise ValueError("Unsupported exp type")


def issue_token(
	*,
	username: str,
	role: str,
	scopes: List[str],
	token_type: str,
	expires_delta: timedelta,
) -> str:
	now = utc_now()
	payload = {
		"sub": username,
		"role": role,
		"scopes": scopes,
		"type": token_type,
		"iat": now,
		"exp": now + expires_delta,
		"jti": secrets.token_hex(16),
	}
	return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
	return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def extract_bearer_token() -> Optional[str]:
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return None
	return auth_header.split(" ", 1)[1].strip()


def auth_required(required_scopes: Optional[List[str]] = None, required_roles: Optional[List[str]] = None):
	required_scopes = required_scopes or []
	required_roles = required_roles or []

	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			token = extract_bearer_token()
			if not token:
				return jsonify({"message": "Missing bearer token"}), 401

			try:
				claims = decode_token(token)
			except jwt.ExpiredSignatureError:
				return jsonify({"message": "Token expired"}), 401
			except jwt.InvalidTokenError:
				return jsonify({"message": "Invalid token"}), 401

			if claims.get("type") != "access":
				return jsonify({"message": "Use access token for this endpoint"}), 401

			if claims.get("jti") in REVOKED_ACCESS_JTIS:
				return jsonify({"message": "Token revoked"}), 401

			token_scopes = set(claims.get("scopes", []))
			missing_scopes = [scope for scope in required_scopes if scope not in token_scopes]
			if missing_scopes:
				return jsonify({"message": "Insufficient scopes", "missing_scopes": missing_scopes}), 403

			if required_roles and claims.get("role") not in required_roles:
				return jsonify({"message": "Insufficient role"}), 403

			request.jwt_claims = claims  # type: ignore[attr-defined]
			return func(*args, **kwargs)

		return wrapper

	return decorator


@app.get("/")
def index():
	return jsonify(
		{
			"message": "Week6 JWT Auth API",
			"swagger": "/apidocs",
			"endpoints": [
				"POST /auth/login",
				"POST /auth/refresh",
				"POST /auth/logout",
				"GET /users",
				"POST /users",
				"GET /security/audit",
				"GET /auth/compare",
			],
		}
	)


@app.post("/auth/login")
def login():
	"""Login endpoint: returns access token and refresh token."""
	body = request.get_json(silent=True) or {}
	username = body.get("username")
	password = body.get("password")

	user = USERS.get(username)
	if not user or user["password"] != password:
		return jsonify({"message": "Invalid credentials"}), 401

	access_token = issue_token(
		username=username,
		role=user["role"],
		scopes=user["scopes"],
		token_type="access",
		expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MIN),
	)
	refresh_token = issue_token(
		username=username,
		role=user["role"],
		scopes=user["scopes"],
		token_type="refresh",
		expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
	)

	refresh_claims = decode_token(refresh_token)
	REFRESH_STORE[refresh_claims["jti"]] = {
		"username": username,
		"exp": refresh_claims["exp"],
		"active": True,
	}

	return jsonify(
		{
			"token_type": "Bearer",
			"access_token": access_token,
			"expires_in": ACCESS_TOKEN_EXPIRES_MIN * 60,
			"refresh_token": refresh_token,
			"scope": " ".join(user["scopes"]),
			"role": user["role"],
		}
	)


@app.post("/auth/refresh")
def refresh():
	"""Refresh endpoint: rotates refresh token and issues new tokens."""
	body = request.get_json(silent=True) or {}
	refresh_token = body.get("refresh_token")
	if not refresh_token:
		return jsonify({"message": "refresh_token is required"}), 400

	try:
		claims = decode_token(refresh_token)
	except jwt.ExpiredSignatureError:
		return jsonify({"message": "Refresh token expired"}), 401
	except jwt.InvalidTokenError:
		return jsonify({"message": "Invalid refresh token"}), 401

	if claims.get("type") != "refresh":
		return jsonify({"message": "Not a refresh token"}), 401

	token_state = REFRESH_STORE.get(claims.get("jti"))
	if not token_state or not token_state.get("active"):
		return jsonify({"message": "Refresh token already used or revoked"}), 401

	exp_dt = parse_exp_to_datetime(token_state["exp"])
	if exp_dt < utc_now():
		token_state["active"] = False
		return jsonify({"message": "Refresh token expired"}), 401

	token_state["active"] = False

	username = claims["sub"]
	role = claims["role"]
	scopes = claims.get("scopes", [])

	new_access_token = issue_token(
		username=username,
		role=role,
		scopes=scopes,
		token_type="access",
		expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MIN),
	)
	new_refresh_token = issue_token(
		username=username,
		role=role,
		scopes=scopes,
		token_type="refresh",
		expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
	)

	new_refresh_claims = decode_token(new_refresh_token)
	REFRESH_STORE[new_refresh_claims["jti"]] = {
		"username": username,
		"exp": new_refresh_claims["exp"],
		"active": True,
	}

	return jsonify(
		{
			"token_type": "Bearer",
			"access_token": new_access_token,
			"expires_in": ACCESS_TOKEN_EXPIRES_MIN * 60,
			"refresh_token": new_refresh_token,
		}
	)


@app.post("/auth/logout")
@auth_required()
def logout():
	"""Logout endpoint: revokes current access token via denylist."""
	claims = request.jwt_claims  # type: ignore[attr-defined]
	REVOKED_ACCESS_JTIS.add(claims["jti"])
	return jsonify({"message": "Logged out. Access token revoked."})


@app.get("/users")
@auth_required(required_scopes=["users:read"])
def list_users():
	"""Protected endpoint: list users; requires users:read scope."""
	return jsonify(DATA["users"])


@app.post("/users")
@auth_required(required_scopes=["users:write"], required_roles=["admin"])
def create_user():
	"""Protected endpoint: create user; requires admin role and users:write scope."""
	body = request.get_json(silent=True) or {}
	name = body.get("name")
	email = body.get("email")
	if not name or not email:
		return jsonify({"message": "name and email are required"}), 400

	new_user = {"id": len(DATA["users"]) + 1, "name": name, "email": email}
	DATA["users"].append(new_user)
	return jsonify(new_user), 201


@app.get("/security/audit")
@auth_required(required_scopes=["audit:read"], required_roles=["admin"])
def security_audit():
	"""Protected endpoint: returns security audit findings and mitigations."""
	findings = []

	if app.debug:
		findings.append(
			{
				"risk": "token_leakage",
				"severity": "high",
				"issue": "Flask debug mode may expose headers/tokens in error traces.",
				"mitigation": "Disable debug in production and use centralized sanitized logging.",
			}
		)

	if JWT_SECRET == "dev-secret-change-me":
		findings.append(
			{
				"risk": "token_forgery",
				"severity": "high",
				"issue": "Default weak JWT secret is in use.",
				"mitigation": "Set strong JWT_SECRET from environment/secret manager.",
			}
		)

	if ACCESS_TOKEN_EXPIRES_MIN > 30:
		findings.append(
			{
				"risk": "replay_attack",
				"severity": "medium",
				"issue": "Access token lifetime is long; stolen token remains valid longer.",
				"mitigation": "Reduce access token TTL (5-15 minutes) and rotate refresh token.",
			}
		)

	findings.append(
		{
			"risk": "token_leakage",
			"severity": "medium",
			"issue": "Bearer tokens can leak if sent via URL or stored in localStorage.",
			"mitigation": "Send only in Authorization header and store in HttpOnly secure cookies where possible.",
		}
	)
	findings.append(
		{
			"risk": "replay_attack",
			"severity": "medium",
			"issue": "A stolen bearer token can be replayed until expiration.",
			"mitigation": "Use short-lived access tokens, jti denylist for suspicious sessions, TLS everywhere.",
		}
	)

	return jsonify(
		{
			"checked_at": utc_now().isoformat(),
			"findings": findings,
			"hardening_checklist": [
				"Never log Authorization header or raw tokens",
				"Enable HTTPS only",
				"Use refresh token rotation",
				"Apply scope+role based authorization",
			],
		}
	)


@app.get("/auth/compare")
def compare_jwt_vs_oauth2():
	"""Returns a quick JWT vs OAuth 2.0 comparison."""
	return jsonify(
		{
			"jwt": {
				"type": "token format",
				"good_for": ["self-contained claims", "stateless verification"],
			},
			"oauth2": {
				"type": "authorization framework",
				"good_for": ["delegated access", "3rd-party login", "consent/scopes"],
			},
			"note": "OAuth 2.0 can issue JWT access tokens, but they are different concepts.",
		}
	)


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)

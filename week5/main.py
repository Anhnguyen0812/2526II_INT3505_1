from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from

app = Flask(__name__)

app.config["SWAGGER"] = {
	"title": "Library Management API",
	"uiversion": 3,
	"openapi": "3.0.2",
}

swagger_template = {
	"info": {
		"title": "Library Management API",
		"description": "Practice API for resource tree design, search, and pagination strategies.",
		"version": "1.0.0",
	},
	"servers": [
		{"url": "http://127.0.0.1:8000", "description": "Local development"},
	],
}

Swagger(app, template=swagger_template)

HEALTH_DOC = {
	"tags": ["System"],
	"responses": {
		200: {
			"description": "Service is healthy",
			"content": {"application/json": {"example": {"status": "ok"}}},
		},
	},
}

LIST_BOOKS_DOC = {
	"tags": ["Books"],
	"responses": {
		200: {"description": "List all books"},
	},
}

SEARCH_OFFSET_DOC = {
	"tags": ["Search"],
	"parameters": [
		{"in": "query", "name": "q", "schema": {"type": "string"}, "description": "Keyword for title or author"},
		{"in": "query", "name": "category", "schema": {"type": "string"}},
		{"in": "query", "name": "available", "schema": {"type": "boolean"}},
		{"in": "query", "name": "offset", "schema": {"type": "integer", "minimum": 0, "default": 0}},
		{"in": "query", "name": "limit", "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 5}},
	],
	"responses": {
		200: {"description": "Search result using offset-limit pagination"},
		400: {"description": "Invalid query parameters"},
	},
}

SEARCH_PAGE_DOC = {
	"tags": ["Search"],
	"parameters": [
		{"in": "query", "name": "q", "schema": {"type": "string"}},
		{"in": "query", "name": "category", "schema": {"type": "string"}},
		{"in": "query", "name": "available", "schema": {"type": "boolean"}},
		{"in": "query", "name": "page", "schema": {"type": "integer", "minimum": 1, "default": 1}},
		{"in": "query", "name": "per_page", "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 5}},
	],
	"responses": {
		200: {"description": "Search result using page-based pagination"},
		400: {"description": "Invalid query parameters"},
	},
}

SEARCH_CURSOR_DOC = {
	"tags": ["Search"],
	"parameters": [
		{"in": "query", "name": "q", "schema": {"type": "string"}},
		{"in": "query", "name": "category", "schema": {"type": "string"}},
		{"in": "query", "name": "available", "schema": {"type": "boolean"}},
		{"in": "query", "name": "cursor", "schema": {"type": "integer", "nullable": True}, "description": "Last seen item id"},
		{"in": "query", "name": "limit", "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 5}},
	],
	"responses": {
		200: {"description": "Search result using cursor pagination"},
		400: {"description": "Invalid query parameters"},
	},
}

LIST_MEMBERS_DOC = {
	"tags": ["Members"],
	"responses": {200: {"description": "List all members"}},
}

LIST_MEMBER_LOANS_DOC = {
	"tags": ["Loans"],
	"parameters": [
		{"in": "path", "name": "member_id", "required": True, "schema": {"type": "integer"}},
	],
	"responses": {
		200: {"description": "List loans of a member"},
		404: {"description": "Member not found"},
	},
}

CREATE_MEMBER_LOAN_DOC = {
	"tags": ["Loans"],
	"parameters": [
		{"in": "path", "name": "member_id", "required": True, "schema": {"type": "integer"}},
	],
	"requestBody": {
		"required": True,
		"content": {
			"application/json": {
				"schema": {
					"type": "object",
					"required": ["book_id", "due_date"],
					"properties": {
						"book_id": {"type": "integer"},
						"due_date": {"type": "string", "format": "date"},
					},
				},
			},
		},
	},
	"responses": {
		201: {"description": "Loan created"},
		400: {"description": "Invalid request body"},
		404: {"description": "Member or book not found"},
		409: {"description": "Book unavailable"},
	},
}


@dataclass
class Author:
	id: int
	name: str


@dataclass
class Category:
	id: int
	name: str


@dataclass
class Book:
	id: int
	title: str
	author_id: int
	category_id: int
	published_year: int
	isbn: str
	total_copies: int
	available_copies: int


@dataclass
class Member:
	id: int
	full_name: str
	email: str
	joined_at: str


@dataclass
class Loan:
	id: int
	member_id: int
	book_id: int
	borrowed_at: str
	due_date: str
	returned_at: Optional[str] = None


AUTHORS: List[Author] = [
	Author(id=1, name="Harper Lee"),
	Author(id=2, name="George Orwell"),
	Author(id=3, name="J.K. Rowling"),
	Author(id=4, name="Yuval Noah Harari"),
	Author(id=5, name="James Clear"),
	Author(id=6, name="Nguyen Nhat Anh"),
]

CATEGORIES: List[Category] = [
	Category(id=1, name="Classic"),
	Category(id=2, name="Dystopian"),
	Category(id=3, name="Fantasy"),
	Category(id=4, name="History"),
	Category(id=5, name="Self-help"),
	Category(id=6, name="Vietnamese Literature"),
]

BOOKS: List[Book] = [
	Book(1, "To Kill a Mockingbird", 1, 1, 1960, "9780061120084", 8, 3),
	Book(2, "1984", 2, 2, 1949, "9780451524935", 10, 2),
	Book(3, "Animal Farm", 2, 2, 1945, "9780451526342", 6, 1),
	Book(4, "Harry Potter and the Sorcerer's Stone", 3, 3, 1997, "9780439708180", 12, 4),
	Book(5, "Harry Potter and the Chamber of Secrets", 3, 3, 1998, "9780439064873", 12, 7),
	Book(6, "Sapiens", 4, 4, 2011, "9780062316097", 9, 5),
	Book(7, "Homo Deus", 4, 4, 2015, "9780062464316", 7, 6),
	Book(8, "Atomic Habits", 5, 5, 2018, "9780735211292", 15, 10),
	Book(9, "Mat Biec", 6, 6, 1990, "9786042042338", 5, 2),
	Book(10, "Cho Toi Xin Mot Ve Di Tuoi Tho", 6, 6, 2008, "9786042042307", 5, 1),
	Book(11, "The Casual Vacancy", 3, 3, 2012, "9780316228534", 4, 2),
	Book(12, "Go Set a Watchman", 1, 1, 2015, "9780062409850", 3, 3),
]

MEMBERS: List[Member] = [
	Member(id=1, full_name="An Nguyen", email="an.nguyen@example.com", joined_at="2025-01-12"),
	Member(id=2, full_name="Linh Tran", email="linh.tran@example.com", joined_at="2025-02-03"),
	Member(id=3, full_name="Minh Pham", email="minh.pham@example.com", joined_at="2025-02-20"),
]

LOANS: List[Loan] = [
	Loan(id=1, member_id=1, book_id=2, borrowed_at="2026-03-01", due_date="2026-03-15"),
	Loan(id=2, member_id=1, book_id=9, borrowed_at="2026-03-07", due_date="2026-03-21"),
	Loan(id=3, member_id=2, book_id=4, borrowed_at="2026-03-10", due_date="2026-03-24"),
	Loan(id=4, member_id=3, book_id=8, borrowed_at="2026-03-09", due_date="2026-03-23", returned_at="2026-03-18"),
]


def _index_by_id(items: Sequence[Any]) -> Dict[int, Any]:
	return {item.id: item for item in items}


AUTHOR_BY_ID = _index_by_id(AUTHORS)
CATEGORY_BY_ID = _index_by_id(CATEGORIES)
BOOK_BY_ID = _index_by_id(BOOKS)
MEMBER_BY_ID = _index_by_id(MEMBERS)


def serialize_book(book: Book) -> Dict[str, Any]:
	author = AUTHOR_BY_ID.get(book.author_id)
	category = CATEGORY_BY_ID.get(book.category_id)
	data = asdict(book)
	data["author"] = asdict(author) if author else None
	data["category"] = asdict(category) if category else None
	data["is_available"] = book.available_copies > 0
	return data


def serialize_loan(loan: Loan) -> Dict[str, Any]:
	data = asdict(loan)
	member = MEMBER_BY_ID.get(loan.member_id)
	book = BOOK_BY_ID.get(loan.book_id)
	data["member"] = asdict(member) if member else None
	data["book"] = serialize_book(book) if book else None
	data["is_overdue"] = loan.returned_at is None and date.fromisoformat(loan.due_date) < date.today()
	return data


def get_int_query_param(name: str, default: int, min_value: int = 0, max_value: int = 100) -> Tuple[int, Optional[Tuple[Dict[str, str], int]]]:
	value = request.args.get(name, str(default))
	try:
		parsed = int(value)
	except ValueError:
		return default, ({"error": f"Query param '{name}' must be an integer."}, 400)

	if parsed < min_value or parsed > max_value:
		return default, ({"error": f"Query param '{name}' must be between {min_value} and {max_value}."}, 400)
	return parsed, None


def search_books(keyword: str, category_name: Optional[str], available: Optional[bool]) -> List[Book]:
	keyword_lower = keyword.lower().strip()

	def matches(book: Book) -> bool:
		author_name = AUTHOR_BY_ID.get(book.author_id).name.lower()
		category_label = CATEGORY_BY_ID.get(book.category_id).name.lower()
		title_match = keyword_lower in book.title.lower()
		author_match = keyword_lower in author_name
		category_match = category_name is None or category_name.lower() == category_label
		availability_match = available is None or (book.available_copies > 0) == available
		return (title_match or author_match) and category_match and availability_match

	return [book for book in BOOKS if matches(book)]


def paginate_offset_limit(items: Sequence[Any], offset: int, limit: int) -> Dict[str, Any]:
	total = len(items)
	sliced = list(items[offset : offset + limit])
	next_offset = offset + limit if offset + limit < total else None
	prev_offset = max(offset - limit, 0) if offset > 0 else None
	return {
		"items": sliced,
		"meta": {
			"strategy": "offset-limit",
			"total": total,
			"offset": offset,
			"limit": limit,
			"next_offset": next_offset,
			"prev_offset": prev_offset,
		},
	}


def paginate_page(items: Sequence[Any], page: int, per_page: int) -> Dict[str, Any]:
	total = len(items)
	total_pages = (total + per_page - 1) // per_page
	start = (page - 1) * per_page
	end = start + per_page
	sliced = list(items[start:end])
	return {
		"items": sliced,
		"meta": {
			"strategy": "page-based",
			"total": total,
			"page": page,
			"per_page": per_page,
			"total_pages": total_pages,
			"has_next": page < total_pages,
			"has_prev": page > 1,
		},
	}


def paginate_cursor(items: Sequence[Any], cursor: Optional[int], limit: int, key_fn: Callable[[Any], int]) -> Dict[str, Any]:
	sorted_items = sorted(items, key=key_fn)
	if cursor is not None:
		sorted_items = [item for item in sorted_items if key_fn(item) > cursor]

	sliced = sorted_items[:limit]
	next_cursor = key_fn(sliced[-1]) if len(sliced) == limit else None
	return {
		"items": sliced,
		"meta": {
			"strategy": "cursor",
			"cursor": cursor,
			"limit": limit,
			"next_cursor": next_cursor,
		},
	}


@app.get("/health")
@swag_from(HEALTH_DOC)
def health_check() -> Any:
	"""
	Health check endpoint.
	"""
	return jsonify({"status": "ok"})


@app.get("/books")
@swag_from(LIST_BOOKS_DOC)
def list_books() -> Any:
	"""
	Basic endpoint to show all books without pagination logic.
	"""
	return jsonify({"count": len(BOOKS), "data": [serialize_book(book) for book in BOOKS]})


@app.get("/books/search/offset")
@swag_from(SEARCH_OFFSET_DOC)
def search_books_offset() -> Any:
	"""
	Search books with offset/limit pagination.
	Example: /books/search/offset?q=harry&offset=0&limit=3
	"""
	keyword = request.args.get("q", "")
	category = request.args.get("category")
	available = request.args.get("available")
	available_bool = None if available is None else available.lower() == "true"

	offset, error = get_int_query_param("offset", default=0, min_value=0, max_value=10_000)
	if error:
		return jsonify(error[0]), error[1]

	limit, error = get_int_query_param("limit", default=5, min_value=1, max_value=100)
	if error:
		return jsonify(error[0]), error[1]

	matched = search_books(keyword, category, available_bool)
	payload = paginate_offset_limit(matched, offset, limit)
	payload["data"] = [serialize_book(book) for book in payload.pop("items")]
	return jsonify(payload)


@app.get("/books/search/page")
@swag_from(SEARCH_PAGE_DOC)
def search_books_page() -> Any:
	"""
	Search books with page-based pagination.
	Example: /books/search/page?q=harry&page=1&per_page=3
	"""
	keyword = request.args.get("q", "")
	category = request.args.get("category")
	available = request.args.get("available")
	available_bool = None if available is None else available.lower() == "true"

	page, error = get_int_query_param("page", default=1, min_value=1, max_value=10_000)
	if error:
		return jsonify(error[0]), error[1]

	per_page, error = get_int_query_param("per_page", default=5, min_value=1, max_value=100)
	if error:
		return jsonify(error[0]), error[1]

	matched = search_books(keyword, category, available_bool)
	payload = paginate_page(matched, page, per_page)
	payload["data"] = [serialize_book(book) for book in payload.pop("items")]
	return jsonify(payload)


@app.get("/books/search/cursor")
@swag_from(SEARCH_CURSOR_DOC)
def search_books_cursor() -> Any:
	"""
	Search books with cursor pagination.
	Cursor in this example is the last seen book ID.
	Example: /books/search/cursor?q=harry&cursor=4&limit=2
	"""
	keyword = request.args.get("q", "")
	category = request.args.get("category")
	available = request.args.get("available")
	available_bool = None if available is None else available.lower() == "true"

	cursor_raw = request.args.get("cursor")
	cursor = None
	if cursor_raw is not None:
		try:
			cursor = int(cursor_raw)
		except ValueError:
			return jsonify({"error": "Query param 'cursor' must be an integer."}), 400

	limit, error = get_int_query_param("limit", default=5, min_value=1, max_value=100)
	if error:
		return jsonify(error[0]), error[1]

	matched = search_books(keyword, category, available_bool)
	payload = paginate_cursor(matched, cursor, limit, key_fn=lambda book: book.id)
	payload["data"] = [serialize_book(book) for book in payload.pop("items")]
	return jsonify(payload)


@app.get("/members")
@swag_from(LIST_MEMBERS_DOC)
def list_members() -> Any:
	"""
	List all members.
	"""
	return jsonify({"count": len(MEMBERS), "data": [asdict(member) for member in MEMBERS]})


@app.get("/members/<int:member_id>/loans")
@swag_from(LIST_MEMBER_LOANS_DOC)
def list_member_loans(member_id: int) -> Any:
	"""
	Nested resource endpoint to demonstrate resource tree design.
	Example: /members/1/loans
	"""
	member = MEMBER_BY_ID.get(member_id)
	if not member:
		return jsonify({"error": "Member not found."}), 404

	member_loans = [loan for loan in LOANS if loan.member_id == member_id]
	return jsonify(
		{
			"member": asdict(member),
			"count": len(member_loans),
			"data": [serialize_loan(loan) for loan in member_loans],
		}
	)


@app.post("/members/<int:member_id>/loans")
@swag_from(CREATE_MEMBER_LOAN_DOC)
def create_member_loan(member_id: int) -> Any:
	"""
	Create a new loan for a member.
	"""
	member = MEMBER_BY_ID.get(member_id)
	if not member:
		return jsonify({"error": "Member not found."}), 404

	payload = request.get_json(silent=True) or {}
	book_id = payload.get("book_id")
	due_date = payload.get("due_date")

	if not isinstance(book_id, int) or not isinstance(due_date, str):
		return jsonify({"error": "Body must include integer 'book_id' and string 'due_date' (YYYY-MM-DD)."}), 400

	book = BOOK_BY_ID.get(book_id)
	if not book:
		return jsonify({"error": "Book not found."}), 404

	if book.available_copies <= 0:
		return jsonify({"error": "Book is currently unavailable."}), 409

	try:
		date.fromisoformat(due_date)
	except ValueError:
		return jsonify({"error": "Invalid due_date. Expected format: YYYY-MM-DD."}), 400

	new_loan = Loan(
		id=(max([loan.id for loan in LOANS], default=0) + 1),
		member_id=member_id,
		book_id=book_id,
		borrowed_at=date.today().isoformat(),
		due_date=due_date,
	)
	LOANS.append(new_loan)
	book.available_copies -= 1

	return jsonify({"message": "Loan created.", "data": serialize_loan(new_loan)}), 201


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000, debug=True)

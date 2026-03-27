from pathlib import Path

from flask import Flask, jsonify, request, send_file


app = Flask(__name__)

BASE_DIR = Path(__file__).parent
DOC_FILES = {
	"openapi": {
		"file": BASE_DIR / "openapi-comparison" / "OpenAPI" / "openapi.yaml",
		"mimetype": "application/yaml",
	},
	"raml": {
		"file": BASE_DIR / "openapi-comparison" / "RAML" / "api.raml",
		"mimetype": "application/yaml",
	},
	"api-blueprint": {
		"file": BASE_DIR / "openapi-comparison" / "API_Blueprint" / "api.apib",
		"mimetype": "text/plain",
	},
	"typespec": {
		"file": BASE_DIR / "openapi-comparison" / "TypeSpec" / "api.tsp",
		"mimetype": "text/plain",
	},
}

DOC_ALIASES = {
	"openapi": "openapi",
	"open-api": "openapi",
	"openapi.yaml": "openapi",
	"openapi.yml": "openapi",
	"raml": "raml",
	"api.raml": "raml",
	"api-blueprint": "api-blueprint",
	"api_blueprint": "api-blueprint",
	"apiblueprint": "api-blueprint",
	"api.apib": "api-blueprint",
	"api blueprint": "api-blueprint",
	"typespec": "typespec",
	"type-spec": "typespec",
	"type_spec": "typespec",
	"typesec": "typespec",
	"api.tsp": "typespec",
	"type spec": "typespec",
}


def normalize_doc_format(raw_value: str | None):
	if not raw_value:
		return None

	cleaned = raw_value.strip().lower().replace("/", "").replace("\\", "")
	return DOC_ALIASES.get(cleaned)


books = [
	{
		"id": 1,
		"title": "Clean Code",
		"author": "Robert C. Martin",
		"published_year": 2008,
	},
	{
		"id": 2,
		"title": "Designing Data-Intensive Applications",
		"author": "Martin Kleppmann",
		"published_year": 2017,
	},
]


def next_book_id() -> int:
	if not books:
		return 1
	return max(book["id"] for book in books) + 1


def find_book(book_id: int):
	return next((book for book in books if book["id"] == book_id), None)


@app.get("/api/books")
def list_books():
	query = request.args.get("q", "").strip().lower()
	if not query:
		return jsonify(books)

	filtered = [
		book
		for book in books
		if query in book["title"].lower() or query in book["author"].lower()
	]
	return jsonify(filtered)


@app.get("/api/books/<int:book_id>")
def get_book(book_id: int):
	book = find_book(book_id)
	if book is None:
		return jsonify({"message": "Book not found"}), 404
	return jsonify(book)


@app.post("/api/books")
def create_book():
	data = request.get_json(silent=True) or {}
	required_fields = ["title", "author", "published_year"]

	missing = [field for field in required_fields if field not in data]
	if missing:
		return (
			jsonify({"message": f"Missing required fields: {', '.join(missing)}"}),
			400,
		)

	if not isinstance(data["published_year"], int):
		return jsonify({"message": "published_year must be an integer"}), 400

	book = {
		"id": next_book_id(),
		"title": str(data["title"]).strip(),
		"author": str(data["author"]).strip(),
		"published_year": data["published_year"],
	}
	books.append(book)
	return jsonify(book), 201


@app.put("/api/books/<int:book_id>")
def update_book(book_id: int):
	book = find_book(book_id)
	if book is None:
		return jsonify({"message": "Book not found"}), 404

	data = request.get_json(silent=True) or {}
	allowed_fields = {"title", "author", "published_year"}
	update_fields = allowed_fields.intersection(data.keys())

	if not update_fields:
		return (
			jsonify({"message": "At least one of title, author, published_year is required"}),
			400,
		)

	if "published_year" in data and not isinstance(data["published_year"], int):
		return jsonify({"message": "published_year must be an integer"}), 400

	for field in update_fields:
		value = data[field]
		if field in {"title", "author"}:
			value = str(value).strip()
		book[field] = value

	return jsonify(book)


@app.delete("/api/books/<int:book_id>")
def delete_book(book_id: int):
	book = find_book(book_id)
	if book is None:
		return jsonify({"message": "Book not found"}), 404

	books.remove(book)
	return jsonify({"message": "Book deleted", "id": book_id})


@app.get("/openapi.yaml")
def openapi_spec():
	spec_path = Path(__file__).with_name("openapi.yaml")
	return send_file(spec_path, mimetype="application/yaml")


@app.get("/api-specs")
def list_api_specs():
	requested_format = request.args.get("format")
	normalized = normalize_doc_format(requested_format)
	if requested_format is not None:
		if normalized is None:
			return (
				jsonify(
					{
						"message": "Invalid format. Supported: openapi, raml, api-blueprint, typespec",
						"examples": [
							"/api-specs/openapi",
							"/api-specs/raml",
							"/api-specs/api-blueprint",
							"/api-specs/typespec",
							"/api-specs?format=openapi.yaml",
							"/api-specs?format=api.raml",
							"/api-specs?format=api.apib",
							"/api-specs?format=api.tsp",
						],
					}
				),
				404,
			)

		doc = DOC_FILES[normalized]
		file_path = doc["file"]
		if not file_path.exists():
			return jsonify({"message": f"Document not found: {file_path.name}"}), 404

		return send_file(file_path, mimetype=doc["mimetype"])

	return jsonify(
		{
			"message": "Available API specification documents",
			"docs": {
				name: f"/api-specs/{name}"
				for name in DOC_FILES
			},
			"query_examples": [
				"/api-specs?format=openapi",
				"/api-specs?format=raml",
				"/api-specs?format=api-blueprint",
				"/api-specs?format=typespec",
				"/api-specs?format=openapi.yaml",
				"/api-specs?format=api.raml",
				"/api-specs?format=api.apib",
				"/api-specs?format=api.tsp",
			],
		}
	)


@app.get("/api-specs/<string:doc_format>")
def get_api_spec_file(doc_format: str):
	normalized = normalize_doc_format(doc_format)
	doc = DOC_FILES.get(normalized) if normalized else None
	if doc is None:
		return (
			jsonify(
				{
					"message": "Invalid format. Supported: openapi, raml, api-blueprint, typespec",
					"examples": [
						"/api-specs/openapi",
						"/api-specs/raml",
						"/api-specs/api-blueprint",
						"/api-specs/typespec",
					],
				}
			),
			404,
		)

	file_path = doc["file"]
	if not file_path.exists():
		return jsonify({"message": f"Document not found: {file_path.name}"}), 404

	return send_file(file_path, mimetype=doc["mimetype"])


@app.get("/docs")
def swagger_ui():
	return """
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Book API Docs</title>
  <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist/swagger-ui.css\" />
</head>
<body>
  <div id=\"swagger-ui\"></div>
  <script src=\"https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js\"></script>
  <script>
	window.onload = () => {
	  window.ui = SwaggerUIBundle({
		url: '/openapi.yaml',
		dom_id: '#swagger-ui'
	  });
	};
  </script>
</body>
</html>
"""


if __name__ == "__main__":
	app.run(debug=True)

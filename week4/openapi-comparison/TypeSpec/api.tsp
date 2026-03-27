import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.OpenAPI;

/**
 * Book Management API - TypeSpec Format
 * 
 * TypeSpec là một ngôn ngữ mô tả API được tạo bởi Microsoft.
 * Format này cho phép định nghĩa models và services một cách tường minh,
 * và có thể generate OpenAPI specs tự động.
 */

@service(
  {
    title: "Book Management API",
    version: "1.0.0",
  }
)
@info({
  title: "Book Management API",
  version: "1.0.0",
  description: "API quản lý sách sử dụng TypeSpec format",
})
@baseUri("http://localhost:5000")
namespace BookManagementAPI;

/**
 * Book Model - Mô tả cấu trúc một cuốn sách
 */
model Book {
  /** ID của sách - readonly, auto-generated */
  @doc("ID của sách")
  id: int32;

  /** Tiêu đề sách */
  @doc("Tiêu đề sách")
  title: string;

  /** Tác giả sách */
  @doc("Tác giả sách")
  author: string;

  /** Năm xuất bản */
  @doc("Năm xuất bản")
  published_year: int32;
}

/**
 * Request để tạo sách mới
 */
model CreateBookRequest {
  /** Tiêu đề sách (required, min length: 1) */
  @doc("Tiêu đề sách")
  @minLength(1)
  title: string;

  /** Tác giả sách (required, min length: 1) */
  @doc("Tác giả sách")
  @minLength(1)
  author: string;

  /** Năm xuất bản (required, min: 0) */
  @doc("Năm xuất bản")
  @minValue(0)
  published_year: int32;
}

/**
 * Request để cập nhật sách
 * Ít nhất một trường phải được cung cấp
 */
model UpdateBookRequest {
  /** Tiêu đề sách (optional) */
  @doc("Tiêu đề sách")
  @minLength(1)
  title?: string;

  /** Tác giả sách (optional) */
  @doc("Tác giả sách")
  @minLength(1)
  author?: string;

  /** Năm xuất bản (optional, min: 0) */
  @doc("Năm xuất bản")
  @minValue(0)
  published_year?: int32;
}

/**
 * Response lỗi từ API
 */
model ErrorResponse {
  /** Mô tả lỗi */
  @doc("Mô tả lỗi")
  message: string;

  /** HTTP status code */
  @doc("HTTP status code")
  statusCode?: int32;

  /** Timestamp khi lỗi xảy ra */
  @doc("Timestamp khi lỗi xảy ra")
  timestamp?: string;
}

/**
 * Response từ delete request
 */
model DeleteResponse {
  /** Thông báo thành công */
  @doc("Thông báo thành công")
  message: string;

  /** ID của sách đã xóa */
  @doc("ID của sách đã xóa")
  id: int32;
}

/**
 * BooksService - Quản lý tất cả operation liên quan đến sách
 */
@tag("Books")
@route("/api/books")
interface BooksService {
  /**
   * List Books - Lấy danh sách tất cả sách
   * Support tìm kiếm theo tên hoặc tác giả
   * 
   * @returns Array of books
   * @example
   * GET /api/books
   * Response 200: [{ id: 1, title: "Clean Code", author: "Robert Martin", published_year: 2008 }]
   */
  @doc("Lấy danh sách tất cả sách")
  @get
  listBooks(
    @query @doc("Từ khóa tìm kiếm") q?: string
  ): Book[];

  /**
   * Create Book - Tạo sách mới
   * 
   * @param body Request body
   * @returns Created book object with id
   * @example
   * POST /api/books
   * {
   *   "title": "Design Patterns",
   *   "author": "Gang of Four",
   *   "published_year": 1994
   * }
   * Response 201: { id: 2, title: "Design Patterns", author: "Gang of Four", published_year: 1994 }
   */
  @doc("Tạo sách mới")
  @post
  @statusCode(201)
  createBook(
    @body body: CreateBookRequest
  ): Book;

  /**
   * Get Book by ID - Lấy chi tiết sách theo ID
   * 
   * @param book_id Book ID (path parameter, required, min: 1)
   * @returns Book object
   * @example
   * GET /api/books/1
   * Response 200: { id: 1, title: "Clean Code", author: "Robert Martin", published_year: 2008 }
   */
  @doc("Lấy chi tiết sách theo ID")
  @get
  @route("/{book_id}")
  getBook(
    @path @doc("ID của sách") @minValue(1) book_id: int32
  ): Book;

  /**
   * Update Book - Cập nhật thông tin sách
   * Ít nhất một trường phải được cung cấp
   * 
   * @param book_id Book ID (path parameter, required, min: 1)
   * @param body Request body (at least 1 field required)
   * @returns Updated book object
   * @example
   * PUT /api/books/1
   * {
   *   "title": "Clean Code 2nd Edition"
   * }
   * Response 200: { id: 1, title: "Clean Code 2nd Edition", author: "Robert Martin", published_year: 2008 }
   */
  @doc("Cập nhật thông tin sách")
  @put
  @route("/{book_id}")
  updateBook(
    @path @doc("ID của sách") @minValue(1) book_id: int32,
    @body body: UpdateBookRequest
  ): Book;

  /**
   * Delete Book - Xóa sách theo ID
   * 
   * @param book_id Book ID (path parameter, required, min: 1)
   * @returns Deletion confirmation
   * @example
   * DELETE /api/books/1
   * Response 200: { message: "Book deleted", id: 1 }
   */
  @doc("Xóa sách theo ID")
  @delete
  @route("/{book_id}")
  @statusCode(200)
  deleteBook(
    @path @doc("ID của sách") @minValue(1) book_id: int32
  ): DeleteResponse;
}

/**
 * Error responses
 */
@error
model BadRequest {
  @statusCode statusCode: 400;
  @body body: ErrorResponse;
}

@error
model NotFound {
  @statusCode statusCode: 404;
  @body body: ErrorResponse;
}

@error
model InternalServerError {
  @statusCode statusCode: 500;
  @body body: ErrorResponse;
}

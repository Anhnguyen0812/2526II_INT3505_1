/**
 * API Design Patterns - Dashboard JS Client
 */

document.addEventListener("DOMContentLoaded", () => {
    // API base URL
    const BASE_URL = window.location.origin;

    // Elements
    const articlesList = document.getElementById("articles-list");
    const articleForm = document.getElementById("article-form");
    const articleIdInput = document.getElementById("article-id");
    const articleTitleInput = document.getElementById("article-title");
    const articleStatusInput = document.getElementById("article-status");
    const articleContentInput = document.getElementById("article-content");
    const formTitle = document.getElementById("form-title");
    const btnSubmitArticle = document.getElementById("btn-submit-article");
    const btnCancelEdit = document.getElementById("btn-cancel-edit");
    const btnFilter = document.getElementById("btn-filter");
    const searchQuery = document.getElementById("search-query");
    const filterStatus = document.getElementById("filter-status");
    const paginationControls = document.getElementById("pagination-controls");

    const subscribeForm = document.getElementById("subscribe-form");
    const subUrlInput = document.getElementById("sub-url");
    const subscriptionsList = document.getElementById("subscriptions-list");
    const btnAutofillReceiver = document.getElementById("btn-autofill-receiver");

    const notificationsList = document.getElementById("notifications-list");
    const btnClearNotifications = document.getElementById("btn-clear-notifications");

    const simTamper = document.getElementById("sim-tamper");
    const simDuplicate = document.getElementById("sim-duplicate");
    const systemTime = document.getElementById("system-time");

    // Current page state (HATEOAS state)
    let currentArticlesUrl = `${BASE_URL}/articles?page=1&limit=5`;

    // Initialize System Time
    setInterval(() => {
        const d = new Date();
        systemTime.textContent = d.toLocaleTimeString("vi-VN");
    }, 1000);

    // --- 1. Articles Operations (CRUD & Query) ---

    // Fetch articles from specified endpoint (Query Pattern & HATEOAS pagination)
    async function fetchArticles(url = currentArticlesUrl) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Không thể tải danh sách bài viết");
            
            const data = await response.json();
            currentArticlesUrl = url; // Save current url state
            renderArticles(data.items);
            renderPagination(data.links, data.count);
        } catch (error) {
            console.error(error);
            articlesList.innerHTML = `<tr><td colspan="5" class="text-center text-danger">⚠️ Lỗi: ${error.message}</td></tr>`;
        }
    }

    // Render articles to table
    function renderArticles(items) {
        if (!items || items.length === 0) {
            articlesList.innerHTML = `<tr><td colspan="5" class="text-center">Chưa có bài viết nào phù hợp.</td></tr>`;
            return;
        }

        articlesList.innerHTML = items.map(item => {
            const links = item.links || {};
            const createdDate = new Date(item.created_at).toLocaleString("vi-VN");
            
            // Build dynamic HATEOAS action buttons based on links returned in response
            let actionButtons = "";
            if (links.self) {
                actionButtons += `<button class="hateoas-btn" onclick="editArticle(${item.id})" title="GET ${links.self}">🔍 Xem/Sửa</button>`;
            }
            if (links.delete) {
                actionButtons += `<button class="hateoas-btn btn-delete" onclick="deleteArticle(${item.id})" title="DELETE ${links.delete}">🗑️ Xóa</button>`;
            }

            return `
                <tr>
                    <td><code>#${item.id}</code></td>
                    <td class="font-medium">${escapeHtml(item.title)}</td>
                    <td>
                        <span class="badge ${item.status === 'published' ? 'status-ok' : 'pattern-tag'}">
                            ${item.status}
                        </span>
                    </td>
                    <td><small>${createdDate}</small></td>
                    <td>
                        <div class="hateoas-actions">
                            ${actionButtons}
                        </div>
                    </td>
                </tr>
            `;
        }).join("");
    }

    // Render pagination controls (HATEOAS)
    function renderPagination(links, totalCount) {
        if (!links) {
            paginationControls.innerHTML = "";
            return;
        }

        let html = `<span>Tổng số: <strong>${totalCount}</strong> bài viết</span>`;
        html += `<div class="pagination-buttons">`;

        // If 'prev' link is provided by backend, enable Back button
        if (links.prev) {
            html += `<button class="btn btn-secondary btn-sm" onclick="goToPage('${links.prev}')">← Trước</button>`;
        } else {
            html += `<button class="btn btn-secondary btn-sm" disabled>← Trước</button>`;
        }

        // If 'next' link is provided by backend, enable Next button
        if (links.next) {
            html += `<button class="btn btn-secondary btn-sm" onclick="goToPage('${links.next}')">Sau →</button>`;
        } else {
            html += `<button class="btn btn-secondary btn-sm" disabled>Sau →</button>`;
        }

        html += `</div>`;
        paginationControls.innerHTML = html;
    }

    // Make window functions globally accessible for inline onclick handlers
    window.goToPage = (url) => {
        fetchArticles(url);
    };

    window.editArticle = async (id) => {
        try {
            const response = await fetch(`${BASE_URL}/articles/${id}`);
            if (!response.ok) throw new Error("Không thể tải bài viết");
            const item = await response.json();
            
            // Set form to edit mode
            articleIdInput.value = item.id;
            articleTitleInput.value = item.title;
            articleStatusInput.value = item.status;
            articleContentInput.value = item.content || "";
            
            formTitle.textContent = `📝 Chỉnh Sửa Bài Viết #${item.id}`;
            btnSubmitArticle.textContent = "Cập Nhật Bài Viết & Phát Sự Kiện";
            btnCancelEdit.classList.remove("hidden");
            
            // Scroll form into view
            articleForm.scrollIntoView({ behavior: "smooth" });
        } catch (error) {
            alert(`Lỗi: ${error.message}`);
        }
    };

    window.deleteArticle = async (id) => {
        if (!confirm(`Bạn có chắc chắn muốn xóa bài viết #${id}? (Thao tác này sẽ phát đi sự kiện article.deleted)`)) return;
        
        try {
            // Check simulation options
            const tamper = simTamper.checked;
            const duplicate = simDuplicate.checked;
            const url = `${BASE_URL}/articles/${id}?tamper=${tamper}&duplicate=${duplicate}`;
            
            const response = await fetch(url, { method: "DELETE" });
            if (!response.ok) throw new Error("Lỗi khi xóa bài viết");
            
            fetchArticles();
            showLocalToast("Xóa bài viết thành công!");
        } catch (error) {
            alert(`Lỗi: ${error.message}`);
        }
    };

    // Filter articles (Query Pattern)
    btnFilter.addEventListener("click", () => {
        const query = encodeURIComponent(searchQuery.value.trim());
        const status = filterStatus.value;
        const newUrl = `${BASE_URL}/articles?page=1&limit=5&q=${query}&status=${status}`;
        fetchArticles(newUrl);
    });

    // Reset Form
    function resetArticleForm() {
        articleIdInput.value = "";
        articleForm.reset();
        formTitle.textContent = "✍️ Viết Bài Mới";
        btnSubmitArticle.textContent = "Tạo Bài Viết & Phát Sự Kiện";
        btnCancelEdit.classList.add("hidden");
    }

    btnCancelEdit.addEventListener("click", resetArticleForm);

    // Form submission (Create / Update CRUD)
    articleForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const title = articleTitleInput.value.trim();
        const status = articleStatusInput.value;
        const content = articleContentInput.value;
        const id = articleIdInput.value;

        const payload = { title, status, content };
        
        // Simulation options
        const tamper = simTamper.checked;
        const duplicate = simDuplicate.checked;

        let url = `${BASE_URL}/articles`;
        let method = "POST";

        if (id) {
            url = `${BASE_URL}/articles/${id}`;
            method = "PUT";
        }

        url += `?tamper=${tamper}&duplicate=${duplicate}`;

        try {
            const response = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || "Lỗi xử lý bài viết");
            }

            resetArticleForm();
            fetchArticles();
            showLocalToast(id ? "Cập nhật bài viết thành công!" : "Tạo bài viết mới thành công!");
        } catch (error) {
            alert(`Lỗi: ${error.message}`);
        }
    });


    // --- 2. Webhook Subscriptions Operations ---

    // Fetch and render subscriptions
    async function fetchSubscriptions() {
        try {
            const response = await fetch(`${BASE_URL}/webhooks/subscriptions`);
            if (!response.ok) throw new Error("Lỗi tải danh sách webhook");
            const data = await response.json();
            renderSubscriptions(data.items);
        } catch (error) {
            console.error(error);
        }
    }

    function renderSubscriptions(items) {
        if (!items || items.length === 0) {
            subscriptionsList.innerHTML = `<tr><td colspan="3" class="text-center">Chưa có webhook subscriber nào được đăng ký.</td></tr>`;
            return;
        }

        subscriptionsList.innerHTML = items.map(sub => {
            const eventsHtml = sub.events.map(ev => `<span class="sub-event-tag">${ev}</span>`).join("");
            return `
                <tr>
                    <td>
                        <div style="font-weight:600; color:var(--text-main); font-family:monospace; word-break:break-all;">
                            ${escapeHtml(sub.url)}
                        </div>
                        <div class="sub-events-list">
                            ${eventsHtml}
                        </div>
                    </td>
                    <td>
                        <div class="secret-key-cell" onclick="toggleSecretDisplay(this, '${sub.secret}')" title="Nhấp để hiển thị">
                            ••••••••••••••••
                        </div>
                    </td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick="deleteSubscription('${sub.id}')">Hủy đăng ký</button>
                    </td>
                </tr>
            `;
        }).join("");
    }

    window.toggleSecretDisplay = (element, secret) => {
        if (element.textContent.trim() === "••••••••••••••••") {
            element.textContent = secret;
            element.style.color = "var(--primary)";
        } else {
            element.textContent = "••••••••••••••••";
            element.style.color = "var(--text-dark)";
        }
    };

    window.deleteSubscription = async (subId) => {
        if (!confirm("Bạn muốn xóa webhook subscriber này?")) return;
        try {
            const response = await fetch(`${BASE_URL}/webhooks/subscriptions/${subId}`, {
                method: "DELETE"
            });
            if (!response.ok) throw new Error("Lỗi khi xóa subscription");
            fetchSubscriptions();
            showLocalToast("Hủy đăng ký Webhook thành công!");
        } catch (error) {
            alert(error.message);
        }
    };

    // Register Webhook
    subscribeForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const url = subUrlInput.value.trim();
        
        // Collect checked events
        const checkedEvents = [];
        document.querySelectorAll('input[name="sub-events"]:checked').forEach(cb => {
            checkedEvents.push(cb.value);
        });

        if (checkedEvents.length === 0) {
            alert("Vui lòng chọn ít nhất một sự kiện để đăng ký!");
            return;
        }

        try {
            const response = await fetch(`${BASE_URL}/webhooks/subscriptions`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url, events: checkedEvents })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error || "Lỗi đăng ký");
            }

            subUrlInput.value = "";
            fetchSubscriptions();
            showLocalToast("Đăng ký Webhook thành công!");
        } catch (error) {
            alert(`Đăng ký thất bại: ${error.message}`);
        }
    });

    // Auto-fill and register the local demo webhook receiver
    btnAutofillReceiver.addEventListener("click", async () => {
        const receiverUrl = `${BASE_URL}/webhooks/receiver`;
        try {
            const response = await fetch(`${BASE_URL}/webhooks/subscriptions`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    url: receiverUrl,
                    events: ["article.created", "article.updated", "article.deleted"]
                })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error || "Lỗi đăng ký");
            }

            fetchSubscriptions();
            showLocalToast("Đăng ký Webhook Receiver demo thành công!");
        } catch (error) {
            alert(`Lỗi: ${error.message}`);
        }
    });


    // --- 3. Notification Center (Webhook Receiver Logs) ---
    
    let knownNotificationsCount = 0;

    // Fetch notifications (Short Polling)
    async function fetchNotifications(silent = false) {
        try {
            const response = await fetch(`${BASE_URL}/notifications`);
            if (!response.ok) throw new Error("Lỗi tải thông báo");
            
            const data = await response.json();
            const items = data.items || [];
            
            renderNotifications(items);

            // Play sound/effect if a new notification is detected (not on page load)
            if (!silent && items.length > knownNotificationsCount) {
                showLocalToast("🔔 Nhận được sự kiện Webhook mới!");
            }
            knownNotificationsCount = items.length;
        } catch (error) {
            console.error(error);
        }
    }

    function renderNotifications(items) {
        if (!items || items.length === 0) {
            notificationsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔔</div>
                    <p>Chưa nhận được sự kiện nào. Hãy tạo bài viết hoặc cập nhật để kích hoạt webhook phát sự kiện.</p>
                </div>
            `;
            return;
        }

        // Render in reverse order (newest first)
        const html = items.slice().reverse().map(noti => {
            let statusClass = "noti-verified";
            let statusLabel = "Signature Verified (Thành công)";
            
            if (noti.status === "signature_error") {
                statusClass = "noti-error";
                statusLabel = "Security Failure (Lỗi chữ ký)";
            } else if (noti.status === "duplicate") {
                statusClass = "noti-duplicate";
                statusLabel = "Duplicate Blocked (Tính lặp lại)";
            }

            const formattedTime = new Date(noti.timestamp).toLocaleTimeString("vi-VN");

            return `
                <div class="notification-item ${statusClass}">
                    <div class="notification-meta">
                        <span class="noti-tag">${statusLabel}</span>
                        <span class="noti-time">${formattedTime}</span>
                    </div>
                    <div class="noti-message">${escapeHtml(noti.message)}</div>
                    <div>
                        <button class="noti-details-btn" onclick="togglePayload(this)">Xem chi tiết Payload</button>
                        <pre class="noti-payload">${escapeHtml(JSON.stringify(noti, null, 2))}</pre>
                    </div>
                </div>
            `;
        }).join("");

        notificationsList.innerHTML = html;
    }

    window.togglePayload = (btn) => {
        const pre = btn.nextElementSibling;
        if (pre.style.display === "block") {
            pre.style.display = "none";
            btn.textContent = "Xem chi tiết Payload";
        } else {
            pre.style.display = "block";
            btn.textContent = "Ẩn chi tiết Payload";
        }
    };

    // Clear notifications log
    btnClearNotifications.addEventListener("click", async () => {
        try {
            const response = await fetch(`${BASE_URL}/notifications/clear`, {
                method: "POST"
            });
            if (!response.ok) throw new Error("Lỗi khi xóa thông báo");
            fetchNotifications(true);
            showLocalToast("Xóa logs thành công!");
        } catch (error) {
            alert(error.message);
        }
    });

    // --- 4. Utilities ---

    function escapeHtml(unsafe) {
        if (!unsafe) return "";
        return String(unsafe)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Local in-app toast notification helper
    function showLocalToast(msg) {
        // Create toast element
        const toast = document.createElement("div");
        toast.className = "local-toast";
        toast.textContent = msg;
        
        // Append styles dynamically if not present
        if (!document.getElementById("toast-styles")) {
            const style = document.createElement("style");
            style.id = "toast-styles";
            style.textContent = `
                .local-toast {
                    position: fixed;
                    bottom: 2rem;
                    right: 2rem;
                    background: rgba(16, 22, 42, 0.95);
                    border: 1px solid var(--primary);
                    box-shadow: 0 4px 20px rgba(56, 189, 248, 0.25);
                    color: white;
                    padding: 0.85rem 1.5rem;
                    border-radius: var(--radius-md);
                    font-size: 0.88rem;
                    font-weight: 500;
                    z-index: 9999;
                    animation: slideIn 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28);
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transition = "opacity 0.5s ease";
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }

    // --- 5. Bootstrapping ---
    
    // Initial fetches
    fetchArticles();
    fetchSubscriptions();
    fetchNotifications(true);

    // Short poll notifications logs (every 1.5 seconds)
    setInterval(() => {
        fetchNotifications(true);
    }, 1500);
});

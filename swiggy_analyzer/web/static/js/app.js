// Swiggy Analyzer Web UI JavaScript

let selectedItems = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    checkStatus();
    loadRecommendations();
    loadOrders();
    loadBasket();
});

// Check authentication status
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        const badge = document.getElementById('status-badge');
        if (data.authenticated) {
            badge.className = 'badge bg-success me-2';
            badge.innerHTML = '<i class="bi bi-circle-fill"></i> Connected to Swiggy';
        } else {
            badge.className = 'badge bg-secondary me-2';
            badge.innerHTML = '<i class="bi bi-circle-fill"></i> Test Mode';
        }
    } catch (error) {
        console.error('Error checking status:', error);
        const badge = document.getElementById('status-badge');
        if (badge) {
            badge.className = 'badge bg-danger me-2';
            badge.innerHTML = '<i class="bi bi-x-circle-fill"></i> Connection Error';
        }
    }
}

// Update score label
function updateScoreLabel() {
    const slider = document.getElementById('min-score-slider');
    const label = document.getElementById('score-value');
    label.textContent = slider.value;
}

// Load recommendations
async function loadRecommendations() {
    const container = document.getElementById('recommendations-list');
    const loading = document.getElementById('recommendations-loading');

    loading.style.display = 'block';
    container.innerHTML = '';
    selectedItems = [];

    try {
        const minScore = document.getElementById('min-score-slider').value;
        const response = await fetch(`/api/recommendations?min_score=${minScore}&max_items=20`);
        const data = await response.json();

        loading.style.display = 'none';

        if (!data.success) {
            container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }

        if (data.recommendations.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-inbox"></i>
                    <p>No recommendations found. Try lowering the min score or syncing more orders.</p>
                </div>
            `;
            return;
        }

        let html = '';
        data.recommendations.forEach(rec => {
            const scoreClass = rec.score >= 80 ? 'score-high' :
                              rec.score >= 60 ? 'score-medium' : 'score-low';
            const unavailable = !rec.available ? 'unavailable' : '';

            html += `
                <div class="card recommendation-card ${scoreClass}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1 ${unavailable}">
                                <h6 class="mb-1">${rec.item_name}</h6>
                                <p class="text-muted small mb-2">${rec.reasoning}</p>
                                <div class="d-flex gap-2 flex-wrap">
                                    <span class="badge bg-secondary">Qty: ${rec.suggested_quantity}</span>
                                    ${rec.current_price ? `<span class="badge bg-info">₹${rec.current_price.toFixed(2)}</span>` : ''}
                                    ${!rec.available ? '<span class="badge bg-danger">Unavailable</span>' : ''}
                                </div>
                            </div>
                            <div class="text-end">
                                <span class="badge ${scoreClass} score-badge">${rec.score}</span>
                                ${rec.available ? `
                                    <button class="btn btn-sm btn-success btn-add-to-basket mt-2"
                                            onclick="addSingleItem('${rec.item_id}', '${rec.item_name}', ${rec.suggested_quantity}, ${rec.score})">
                                        <i class="bi bi-plus-circle"></i> Add
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        // Add button to add all
        if (data.recommendations.some(r => r.available)) {
            html = `
                <button class="btn btn-primary w-100 mb-3" onclick="addAllRecommendations()">
                    <i class="bi bi-cart-plus"></i> Add All Available Items
                </button>
            ` + html;
        }

        container.innerHTML = html;

    } catch (error) {
        loading.style.display = 'none';
        container.innerHTML = `<div class="alert alert-danger">Error loading recommendations: ${error.message}</div>`;
    }
}

// Load orders
async function loadOrders() {
    const container = document.getElementById('orders-list');
    const loading = document.getElementById('orders-loading');

    loading.style.display = 'block';
    container.innerHTML = '';

    try {
        const response = await fetch('/api/orders');
        const data = await response.json();

        loading.style.display = 'none';

        if (!data.success) {
            container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }

        if (data.orders.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-inbox"></i>
                    <p>No order history found. Sync your orders first.</p>
                </div>
            `;
            return;
        }

        let html = '';
        data.orders.forEach(order => {
            const date = new Date(order.order_date);
            const dateStr = date.toLocaleDateString('en-IN', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });

            html += `
                <div class="card order-card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="mb-0">${dateStr}</h6>
                            <span class="badge bg-primary">${order.items.length} items</span>
                        </div>
                        <div class="small">
                            ${order.items.map(item => `
                                <div class="d-flex justify-content-between py-1">
                                    <span>${item.item_name}</span>
                                    <span class="text-muted">×${item.quantity}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;

    } catch (error) {
        loading.style.display = 'none';
        container.innerHTML = `<div class="alert alert-danger">Error loading orders: ${error.message}</div>`;
    }
}

// Load basket
async function loadBasket() {
    const container = document.getElementById('basket-list');

    // Show loading spinner
    container.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

    try {
        const response = await fetch('/api/basket');
        const data = await response.json();

        if (!data.success) {
            const errorMsg = data.mode === 'error'
                ? `${data.error}<br><small>Check your connection or authentication</small>`
                : data.error || 'Unknown error';
            container.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> ${errorMsg}</div>`;
            return;
        }

        const items = data.basket.items || [];
        const total = data.basket.total || 0;

        // Show mode indicator
        let modeNote = '';
        if (data.mode === 'real') {
            modeNote = '<div class="alert alert-success mb-3"><i class="bi bi-check-circle"></i> Connected to Swiggy - Real basket</div>';
        } else if (data.mode === 'test') {
            modeNote = '<div class="alert alert-info mb-3"><i class="bi bi-info-circle"></i> Test Mode - Mock basket (not real Swiggy basket)</div>';
        }

        if (items.length === 0) {
            container.innerHTML = modeNote + `
                <div class="empty-state">
                    <i class="bi bi-basket"></i>
                    <p>Your basket is empty</p>
                    <p class="text-muted small">Add items from recommendations above</p>
                </div>
            `;
            return;
        }

        let html = modeNote + '<div class="row">';
        items.forEach(item => {
            const itemPrice = item.price || 50;
            const itemTotal = itemPrice * item.quantity;
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card shadow-sm">
                        <div class="card-body">
                            <h6 class="mb-2">${item.name}</h6>
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="text-muted">Qty: ${item.quantity}</span>
                                <span class="badge bg-primary">₹${itemPrice.toFixed(2)}</span>
                            </div>
                            <hr class="my-2">
                            <div class="d-flex justify-content-between">
                                <span><strong>Total:</strong></span>
                                <span><strong>₹${itemTotal.toFixed(2)}</strong></span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        if (total > 0 || items.length > 0) {
            // Calculate total if not provided
            const calculatedTotal = total > 0 ? total : items.reduce((sum, item) => {
                return sum + ((item.price || 50) * item.quantity);
            }, 0);

            html += `
                <div class="alert alert-success mt-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span><strong>Basket Total:</strong></span>
                        <span class="fs-4"><strong>₹${calculatedTotal.toFixed(2)}</strong></span>
                    </div>
                    <small class="text-muted">${items.length} item(s) in basket</small>
                </div>
            `;
        }

        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading basket:', error);
        container.innerHTML = `<div class="alert alert-danger">Error loading basket: ${error.message}</div>`;
    }
}

// Add single item to basket
async function addSingleItem(itemId, itemName, quantity, score) {
    try {
        const response = await fetch('/api/basket/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                items: [{
                    item_id: itemId,
                    item_name: itemName,
                    quantity: quantity,
                    score: score
                }]
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Success', `Added ${itemName} to basket!`, 'success');
            loadBasket();
        } else {
            showNotification('Error', data.error, 'danger');
        }

    } catch (error) {
        showNotification('Error', error.message, 'danger');
    }
}

// Add all recommendations
async function addAllRecommendations() {
    const container = document.getElementById('recommendations-list');
    const cards = container.querySelectorAll('.recommendation-card:not(.unavailable)');

    const items = [];
    cards.forEach(card => {
        // Extract item data from the card's button onclick
        const btn = card.querySelector('.btn-add-to-basket');
        if (btn) {
            const onclick = btn.getAttribute('onclick');
            const match = onclick.match(/addSingleItem\('([^']+)',\s*'([^']+)',\s*(\d+),\s*([\d.]+)\)/);
            if (match) {
                items.push({
                    item_id: match[1],
                    item_name: match[2],
                    quantity: parseInt(match[3]),
                    score: parseFloat(match[4])
                });
            }
        }
    });

    if (items.length === 0) {
        showNotification('Info', 'No items to add', 'info');
        return;
    }

    try {
        const response = await fetch('/api/basket/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ items })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Success', `Added ${items.length} items to basket!`, 'success');
            loadBasket();
        } else {
            showNotification('Error', data.error, 'danger');
        }

    } catch (error) {
        showNotification('Error', error.message, 'danger');
    }
}

// Clear basket
async function clearBasket() {
    if (!confirm('Are you sure you want to clear the basket?')) {
        return;
    }

    try {
        const response = await fetch('/api/basket/clear', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Success', 'Basket cleared!', 'success');
            loadBasket();
        } else {
            showNotification('Error', data.error, 'danger');
        }

    } catch (error) {
        showNotification('Error', error.message, 'danger');
    }
}

// Sync orders
async function syncOrders() {
    const btn = document.getElementById('sync-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Syncing...';

    try {
        const response = await fetch('/api/sync', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Success', `Synced ${data.orders_synced} orders!`, 'success');
            checkStatus();
            loadOrders();
            loadRecommendations();
        } else {
            showNotification('Error', data.error, 'danger');
        }

    } catch (error) {
        showNotification('Error', error.message, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-arrow-repeat"></i> Sync';
    }
}

// Show notification toast
function showNotification(title, message, type) {
    const toast = document.getElementById('notification-toast');
    const toastBody = toast.querySelector('.toast-body');
    const toastHeader = toast.querySelector('.toast-header');

    // Set color based on type
    toast.className = `toast bg-${type} text-white`;
    toastHeader.className = `toast-header bg-${type} text-white`;

    toastBody.textContent = message;

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

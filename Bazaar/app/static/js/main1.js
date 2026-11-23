// =====================================================
// DOM ELEMENTS
// =====================================================
const exploreButton = document.querySelector("#explore-button");

const wishlistButton = document.querySelector("#wishlist-button");

const cartButton = document.querySelector("#cartButton");

const historyButton = document.querySelector("#historyButton");

const outStockButton = document.querySelector("#outStockButton");

const expiredButton =document.querySelector("#expiredButton");    



const exploreSection = document.querySelector("#discover-section");

const wishlistSection = document.querySelector("#wishlist-section");

const cartSection = document.querySelector("#cart-section");

const historySection = document.querySelector("#history-section");

const outStockSection = document.querySelector("#outofStock-section");

const expiredSection =document.querySelector("#expired-section");    


const pageSections = document.querySelectorAll(".pagesection");

const navButtons = document.querySelectorAll(".navButtons");


const modal = document.querySelector("#view-modal");


const productsContainer =document.querySelector("#productscontainer");

const wishlistContainer = document.querySelector('#wishlist-container');

const cartContainer = document.querySelector('#cart-container');

const orderContainer = document.querySelector('#order-container');

const outofStockContainer = document.querySelector('#outofStock-container');
const expiredContainer = document.querySelector('#expired-container');
//pagination search filter sort
const searchInput = document.querySelector('#search');
const submitButton = document.querySelector('#submit');
const clearButton = document.querySelector('#clear');
const orderBy = document.querySelector('#orderby');
const loadMoreButton = document.querySelector('#load-more');

const loadMoreOutStockButton = document.querySelector('#load-more-outStock');
const loadMoreExpiredButton = document.querySelector('#load-more-expired');
const brandsDropdownButton = document.querySelector('#brands-dropdownButton');
const brandsDropdown = document.querySelector('#brands-dropdown');

const categoryDropdownButton = document.querySelector('#catagories-dropdownButton');
const categoryDropdown = document.querySelector('#catagories-dropdown');


const nextPageButton = document.querySelector('#manualNext');
const previousPageButton = document.querySelector('#manualPrevious');
// =====================================================
// GLOBAL DATA
// =====================================================

let products = [];
let allreviews = [];
let wishlist = [];
let allproducts = [];
let allwishlistreviews = [];
let cart = [];
let outStock = [];
let expired = [];
let currentPage = 1;
let currentWishlistPage = 1;
let currentOutStockPage = 1;
let currentExpiredPage = 1;
let outStockReviews = [];
let expiredReviews = [];
////add to cart MODAL
const cartViewModal = document.querySelector("#cartViewModal");
const cartModal = document.querySelector("#cartModal");
const incrementButton = document.querySelector('#incrementButton');
const decrementButton = document.querySelector('#decrementButton');
const moveCartButton = document.querySelector('#moveCart');
const closeCartModal = document.querySelector('#closeCart')

//csrf_token //
const csrfToken = document.querySelector('meta[name="csrf_token"]').content;

/*ESCAPE HTML */
function escapeHTML(value){
    let text = String(value ?? "");
    text = text.replaceAll('&','&amp;');
    text = text.replaceAll('<','&lt;');
    text = text.replaceAll('>','&gt;');
    text = text.replaceAll('"','&quot;');
    text = text.replaceAll("'",'&#39;');

    return text;
}

function safeImageUrl(value){
    if(typeof value !== "string" || !value.trim()){
        return "/static/img/placeholder.png";
    }
    try{
        const url = new URL(value.trim(),window.location.origin);
        if(url.protocol !== "https:" && url.protocol !== "http:"){
            return "/static/img/placeholder.png";
        }
        return url.href;

    }
    catch(error){
        return "/static/img/placeholder.png";
    }

}


/* flash messages */
document.querySelectorAll(".flash-message").forEach(message => {
    const duration = message.classList.contains("error")
        ? 6000
        : 3000;

    setTimeout(() => {
        message.classList.add("hide");

        setTimeout(() => message.remove(), 500);
    }, duration);
});

document.querySelectorAll(".flash-close").forEach(button => {
    button.addEventListener("click", () => {
        const message = button.closest(".flash-message");
        if (message) message.remove();
    });
});

/* SECTION NAVIGATION. */
function showSection(section) {

    pageSections.forEach(function(pagesection) {

        pagesection.classList.remove("active");

    });

    section.classList.add("active");
}


function clicked(buttonClicked) {
    navButtons.forEach(function(navButton) {

        navButton.classList.remove("clicked");

    });

    buttonClicked.classList.add("clicked");
}


// =====================================================
// BUILD QUERY PARAMETERS
// =====================================================
function get_params(page){
    const params = new URLSearchParams();
    const search = searchInput.value.trim();
    if (search){
        params.set('search', search);
    }

    const selectedBrands = document.querySelectorAll('input[name = "brands"]:checked');
    selectedBrands.forEach(function(brand){
        params.append('brands', brand.value);
    });

    const selectedCategories = document.querySelectorAll('input[name="categories"]:checked');
    selectedCategories.forEach(function(category){
        params.append('categories', category.value);
    });

    const sortby = orderBy.value.trim()
    if (sortby){
        params.set('sortby', sortby);
    }

    params.set('page',page);
    return params;
}




async function load_products(reset=false) {
    try{
        if(reset){
            currentPage = 1;
            products = [];
            allreviews = [];
            cart = [];
            productsContainer.innerHTML = "";
        }

        const params = get_params(currentPage);
        const response = await fetch(`/api/products?${params.toString()}`);
        const data = await response.json();
        if(!response.ok){
            throw new Error(`HTTP Error: ${response.status} ${data.error}`);
        }
        const current_products = data.products;
        const reviews = data.reviews;
        const has_more = data.has_more;
        const data_page = data.page;
        const cart_items = data.cart_items;
        const wishlist_items = data.wishlist_items;
        const fetched_allproducts = data.allproducts;
        allproducts = fetched_allproducts;

        products.push(...current_products);
        allreviews.push(...reviews);
        cart = cart_items;
        wishlist = wishlist_items;
        render_products(current_products,productsContainer);

        if(has_more){
            loadMoreButton.style.display = 'block';
        }
        else{
            loadMoreButton.style.display = 'none';
        }

        console.log("currentPage: ", data_page);
        console.log("total matching products: ", data.total)



    }
    catch(error){
        console.log("ERROR: ", error);
    }
}

async function load_wishlist(reset = false) {

    if (reset) {
        wishlistContainer.innerHTML = "";
        allwishlistreviews = [];
    }

    try {
        const response = await fetch("/api/wishlist");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }

        wishlist = data.wishlist_items;

        const fetched_products = data.products;
        allwishlistreviews = data.wishlist_reviews;

        const wishlist_products = fetched_products.filter(function(product) {
            return wishlist.includes(product.id);
        });

        wishlistContainer.innerHTML = "";

        render_products(wishlist_products, wishlistContainer);

    } catch (error) {
        console.error("Wishlist error:", error);
    }
}

async function load_cart() {

    try{
        const response = await fetch(`/api/cart`);
        const data = await response.json();
        if(!response.ok){
            throw new Error(data.error || `http error ${response.status}`);
        }
        cart = data.cart_items;
        const grandTotal = data.grand_total; 
        render_cart_items(cart,grandTotal); 
    }
    catch(error){
        console.log("error: ",error);
    }
}

async function load_outStock(reset=false) {
    try{
        if(reset){
            currentOutStockPage = 1;
            outStock = [];
            outStockReviews = [];
            outofStockContainer.innerHTML = "";
        }

        const params = get_params(currentOutStockPage);
        const response = await fetch(`/bazaar/admin/outofStock?${params.toString()}`);
        const data = await response.json();
        if(!response.ok){
            throw new Error(`HTTP Error: ${response.status} ${data.error}`);
        }
        const reviews = data.reviews;
        const has_more = data.has_more;
        const data_page = data.page;
        const current_products = data.products;

        outStock.push(...current_products);
        outStockReviews.push(...reviews);
        render_products_offshelf(current_products,outofStockContainer);

        if(has_more){
            loadMoreOutStockButton.style.display = 'block';
        }
        else{
            loadMoreOutStockButton.style.display = 'none';
        }

        console.log("currentPage: ", data_page);
        console.log("total matching products: ", data.total)



    }
    catch(error){
        console.log("ERROR: ", error);
    }
}

async function load_expired(reset=false) {
    try{
        if(reset){
            currentExpiredPage = 1;
            expired = [];
            expiredReviews = [];
            expiredContainer.innerHTML = "";
        }

        const params = get_params(currentExpiredPage);
        const response = await fetch(`/bazaar/admin/Expired?${params.toString()}`);
        const data = await response.json();
        if(!response.ok){
            throw new Error(`HTTP Error: ${response.status} ${data.error}`);
        }
        const reviews = data.reviews;
        const has_more = data.has_more;
        const data_page = data.page;
        const current_products = data.products;

        expired.push(...current_products);
        expiredReviews.push(...reviews);
        render_products_offshelf(current_products,expiredContainer);

        if(has_more){
            loadMoreExpiredButton.style.display = 'block';
        }
        else{
            loadMoreExpiredButton.style.display = 'none';
        }

        console.log("currentPage: ", data_page);
        console.log("total matching products: ", data.total)



    }
    catch(error){
        console.log("ERROR: ", error);
    }
}

function render_products_offshelf(products,container) {
    products.forEach(function(product) {

        const card =document.createElement("div");

        card.classList.add("productCard");
        card.id = `product-${product.id}`;


        let price_html = "";


        if (product.discount_percent === 0) {
            price_html = `Price : ${product.price}`;
        }

        else if (product.discount_percent > 0) {

            const new_price =product.price - (product.price * product.discount_percent) / 100;

            price_html = `
                <del>
                    Price : ${escapeHTML(product.price)}
                </del>

                <span>
                    ${escapeHTML(new_price.toFixed(2))}
                </span>

                <span>
                    DISCOUNT :
                    ${escapeHTML(product.discount_percent)}%
                </span>
            `;

        }



        let rating_tag = "";
        if(!product.avg_rating){
            rating_tag = "NIL";
        }else{
            rating_tag = `${product.avg_rating}`;
        }


        card.innerHTML = `

            <div class="img">

                <img
                    src="${escapeHTML(safeImageUrl(product.image_url))}"
                    alt="product image"
                >

            </div>


            <p>
                ${escapeHTML(product.name)}
            </p>

            <p>
                BRAND:
                ${escapeHTML(product.brand_name)}
            </p>


            <p>
                CATEGORY:
                ${escapeHTML(product.category_name)}
            </p>


            <p>
                ${price_html}
            </p>


            <p>
                NO OF AVAILABLE:
                ${escapeHTML(product.quantity)}
            </p>


            <p>
                AVG RATING:
                ${escapeHTML(rating_tag)}
            </p>


            <button
                class="viewProduct"
                id = "product-${product.id}"
                type="button"
                data-id="${product.id}"
            >
                VIEW PRODUCT
            </button>

        `;


        container.append(card);
    });
}

function render_cart_items(cart,grandTotal){
    cartContainer.innerHTML = "";
    let table_data = "";
    let table_body = ""



    if(cart.length === 0){
        table_body = `
            <tr>
                <td colspan="10" class="empty-cart">
                    No products available in cart.
                </td>
            </tr>        
        `;
    }
    else{
        cart.forEach(function(item){
            const status = item.availability_status;
            table_body += `
                <tr id="cart-${item.product_id}">
                    <td>
                        ${escapeHTML(item.product_name)}<span class="availability-status">${escapeHTML(status)}</span>
                    </td>
                    <td>${escapeHTML(item.brand_name)}</td>
                    <td class="row-quantity" id="product-${item.product_id}">${escapeHTML(item.quantity_selected)}</td>
                    <td><button class="incrementCart" id="incrementButton-${item.product_id}" type="button" data-id=${item.product_id} data-quantity = ${item.quantity} data-selected = ${item.quantity_selected}>+</button></td>
                    <td><button class="decrementCart" id="decrementButton-${item.product_id}" type="button" data-id=${item.product_id} data-quantity = ${item.quantity} data-selected = ${item.quantity_selected} >-</button></td>
                    <td>₹${escapeHTML(item.price)}</td>
                    <td>${escapeHTML(item.discount_percent)}%</td>
                    <td>${escapeHTML(item.discounted_unit_price)}</td>                                        
                    <td>₹${escapeHTML(item.total_price)}</td>
                    <td><button type="button"  id="cartUpdate-${item.product_id}" class="updateCart" data-id=${item.product_id}  data-quantity = ${item.quantity} data-price = ${item.price} data-discount = ${item.discount_percent}>UPDATE QUANTITY</button></td>
                    <td>
                        <button
                            type="button"
                            id="col-${item.product_id}"
                            class="removeCartbutton"
                            data-id="${item.product_id}",
                            data-price = "${item.price}",
                            data-discount = "${item.discount_percent}">
                            REMOVE FROM CART
                        </button>
                    </td>
                </tr>                
            `;
        });
    }

    table_data = `
        <div class="cart-table-wrapper">
            <table class="cart-table">
                <thead>
                    <tr>
                        <th>PRODUCT NAME</th>
                        <th>BRAND</th>
                        <th>QUANTITY</th>
                        <th>INCREMENT</th>
                        <th>DECREMENT</th>
                        <th>PRICE</th>
                        <th>DISCOUNT</th>
                        <th>DISCOUNTED PRICE</th>
                        <th>TOTAL PRICE</th>
                        <th>UPDATE</th>
                        <th>REMOVE</th>
                    </tr>
                </thead>

                <tbody>
                    ${table_body}
                </tbody>
            </table>
        </div>

        ${cart.length > 0 ? `
            <div class="cart-summary">
                <div class="cart-summary-header">
                    <h3>ORDER SUMMARY</h3>
                    <span>${cart.length} products</span>
                </div>

                <div class="cart-total-row">
                    <span>GRAND TOTAL</span>
                    <strong id="display_grandTotal">
                        ₹${escapeHTML(grandTotal)}
                    </strong>
                </div>
                <p id="checkout-error" role="alert"></p>
                <button
                    id="order-place"
                    class="order-place"
                    type="button">
                    PLACE ORDER →
                </button>
            </div>`
        : ""}
    `;

    cartContainer.innerHTML = table_data;



}



function render_products(products,container) {
    const isWishlist = container === wishlistContainer;
    products.forEach(function(product) {

        const card =document.createElement("div");

        card.classList.add("productCard");
        card.id = `product-${product.id}`;


        let price_html = "";


        if (product.discount_percent === 0) {
            price_html = `Price : ${product.price}`;
        }

        else if (product.discount_percent > 0) {

            const new_price =product.price - (product.price * product.discount_percent) / 100;

            price_html = `
                <del>
                    Price : ${escapeHTML(product.price)}
                </del>

                <span>
                    ${escapeHTML(new_price.toFixed(2))}
                </span>

                <span>
                    DISCOUNT :
                    ${escapeHTML(product.discount_percent)}%
                </span>
            `;

        }
        let wishlist_tag = "";

        if (wishlist.includes(product.id)) {
            wishlist_tag = "REMOVE FROM WISHLIST";
        } else {
            wishlist_tag = "ADD TO WISHLIST";
        }


        let rating_tag = "";
        if(!product.avg_rating){
            rating_tag = "NIL";
        }else{
            rating_tag = `${product.avg_rating}`;
        }


        card.innerHTML = `

            <div class="img">

                <img
                    src="${escapeHTML(safeImageUrl(product.image_url))}"
                    alt="product image"
                >

            </div>


            <p>
                ${escapeHTML(product.name)}
            </p>

            ${isWishlist ? `
                <p>
                    STATUS: ${escapeHTML(product.availability_status)}
                </p>
            ` : ""}

            <p>
                BRAND:
                ${escapeHTML(product.brand_name)}
            </p>


            <p>
                CATEGORY:
                ${escapeHTML(product.category_name)}
            </p>


            <p>
                ${price_html}
            </p>


            <p>
                NO OF AVAILABLE:
                ${escapeHTML(product.quantity)}
            </p>


            <p>
                AVG RATING:
                ${escapeHTML(rating_tag)}
            </p>


            <button
                class="viewProduct"
                id = "product-${product.id}"
                type="button"
                data-id="${product.id}"
            >
                VIEW PRODUCT
            </button>


            <button
                class="wishlist"
                type="button"
                data-id="${product.id}"
            >
                ${wishlist_tag}
            </button>

        `;


        container.append(card);
    });
}
brandsDropdownButton.addEventListener('click',function(){
    brandsDropdown.classList.toggle("hidden");
});

categoryDropdownButton.addEventListener('click',function(){
    categoryDropdown.classList.toggle("hidden");
});
loadMoreButton.addEventListener('click', function(){
    currentPage += 1;
    load_products(false);
});

loadMoreOutStockButton?.addEventListener('click', function(){
    currentOutStockPage += 1;
    load_outStock(false);
});

loadMoreExpiredButton?.addEventListener('click', function(){
    currentExpiredPage += 1;
    load_expired(false);
});

submitButton.addEventListener('click', function(){
    load_products(true);
});

clearButton.addEventListener('click', function(){
    searchInput.value = "";
    orderBy.value = "";

    document.querySelectorAll('input[name="brands"]').forEach(function(brand){
        brand.checked = false;
    });

    document.querySelectorAll('input[name="categories"]').forEach(function(category){
        category.checked = false;
    });

    load_products(true);
});

function updateQuantityButtons() {
    const modalIncrementButton = modal.querySelector("#incrementButton");
    const modalDecrementButton = modal.querySelector("#decrementButton");
    const quantityDisplay = modal.querySelector("#quantity");
    const moveCartButton = modal.querySelector("#moveCart");

    if (!modalIncrementButton || !modalDecrementButton ||
        !quantityDisplay || !moveCartButton) {
        return;
    }

    const selected = Number(quantityDisplay.textContent);
    const available = Number(modalIncrementButton.dataset.quantity);

    modalIncrementButton.disabled = selected >= available;
    modalDecrementButton.disabled = selected <= 1;

    moveCartButton.disabled = selected < 1 || selected > available;
}

async function editCartQuantity(productID, newQuantity) {
    const response = await fetch("/api/cart_edit", {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },

        body: JSON.stringify({
            product_id: productID,
            new_quantity: newQuantity
        })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Failed to update cart");
    }

    await load_cart();
    return data;
}

async function place_order(){
    const errorElement = document.querySelector("#checkout-error");

    if (errorElement) {
        errorElement.textContent = "";
    }    
    try{
        const response = await fetch('/api/orderPlace', {
            method: "POST",
            headers: {
                "Content-Type" : "application/json",
                "X-CSRFToken": csrfToken
            },
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Failed to update cart");
        }
        return true;        

    }
    catch(error){

        console.error("Checkout failed:", error);

        const errorElement = document.querySelector("#checkout-error");

        if (errorElement) {
            errorElement.textContent = error.message;
        }

        return false;
    }
}

async function load_orders(){
    try{
        const response = await fetch(`/api/orders`);
        const data = await response.json();
        if(!response.ok){
            throw new Error(data.error || `HTTP ERROR: ${response.status}`);
        }
        const orders = data.orders_dict;
        render_orders(orders);


    }
    catch(error){
        console.log("error : ",error);
    }
}


function render_orders(orders) {

    orderContainer.innerHTML = ``;

    Object.entries(orders).sort(function(a, b){
            return Number(b[0]) - Number(a[0]);
        })
        .forEach(function([order_id, items]) {

        let order_card = ``;
        let table_body = ``;

        items.forEach(function(item) {
            table_body += `
                <tr>
                    <td>${escapeHTML(item.product_name)}</td>
                    <td>₹${escapeHTML(item.unit_price)}</td>
                    <td>${escapeHTML(item.quantity)}</td>
                    <td>${escapeHTML(item.discount_percent)}%</td>
                    <td>₹${escapeHTML(item.line_total)}</td>
                </tr>
            `;
        });

        order_card = `
            <div class="order-card">
                <div class="order-table-wrapper">
                    <table class="order-table">
                        <caption>ORDER_ID: ${escapeHTML(order_id)}</caption>

                        <thead>
                            <tr>
                                <th>PRODUCT NAME</th>
                                <th>UNIT PRICE</th>
                                <th>QUANTITY</th>
                                <th>DISCOUNT</th>
                                <th>LINE TOTAL</th>
                            </tr>
                        </thead>

                        <tbody>
                            ${table_body}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        orderContainer.innerHTML += order_card;

    });

}


// =====================================================
// EVENT DELEGATION
// =====================================================


cartContainer.addEventListener('click', async function(event){
    if (event.target.classList.contains("incrementCart")) {
        const product_id = Number(event.target.dataset.id)

        const quantityDisplay = cartContainer.querySelector(`#product-${product_id}`);


        let selected = Number(quantityDisplay.textContent);
        const available = Number(event.target.dataset.quantity);

        if (selected < available) {
            selected++;
            quantityDisplay.textContent = selected;
        }

    }

    if (event.target.classList.contains("decrementCart")) {
        const product_id = Number(event.target.dataset.id)

        const quantityDisplay = cartContainer.querySelector(`#product-${product_id}`);


        let selected = Number(quantityDisplay.textContent);

        if (selected > 1) {
            selected--;
            quantityDisplay.textContent = selected;
        }


    }
    if (event.target.classList.contains("updateCart")) {
        const button = event.target;
        const productID = Number(button.dataset.id);

        const row = button.closest("tr");
        const quantityDisplay = row.querySelector(".row-quantity");
        const selected = Number(quantityDisplay.textContent);

        button.disabled = true;

        try {
            await editCartQuantity(productID, selected);
            console.log("Cart updated successfully");
        } catch (error) {
            console.error("Cart update failed:", error);
            await load_cart(); 
        } finally {
            if (button.isConnected) {
                button.disabled = false;
            }
        }
    }
    if (event.target.classList.contains("order-place")) {
        const button = event.target;
        button.disabled = true;

        try {
            const success = await place_order();

            if (success) {
                console.log("Order placed successfully");
                await load_cart();
                await load_orders();
            }
        } finally {
            if (button.isConnected) {
                button.disabled = false;
            }
        }
    }
});


modal.addEventListener("submit", async function(event) {

    if (event.target.id !== "reviewForm") {
        return;
    }

    event.preventDefault();

    const form = event.target;
    const productID = Number(
        modal.querySelector("#addReview").dataset.id
    );

    const formData = new FormData(form);

    const reviewData = {
        product_id: Number(productID),
        rating: Number(formData.get("rating")),
        review_text: formData.get("review_text").trim(),
        order_id : Number(formData.get("orderID").trim())
    };

    const submitButton = form.querySelector(
        'button[type="submit"]'
    );

    const message = form.querySelector("#reviewMessage");

    submitButton.disabled = true;
    message.textContent = "";

    try {
        const response = await fetch("/api/reviews", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify(reviewData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Review submission failed");
        }

        message.textContent = "Review submitted successfully!";

        form.reset();
        form.classList.add("hidden");
        await load_products();
        const viewProductModalButton = document.querySelector(`#product-${productID}`);
        viewProductModalButton?.click();


    } catch (error) {
        message.textContent = error.message;
    } finally {
        submitButton.disabled = false;
    }
});


document.addEventListener("click", async function(event) {
    // ---------------------------------
    // NAVIGATION
    // ---------------------------------

    if (event.target === exploreButton) {
        showSection(exploreSection);
        await load_products(true);

        clicked(exploreButton);

    }


    if (event.target === wishlistButton) {

        showSection(wishlistSection);
        await load_wishlist(true);

        clicked(wishlistButton);


    }


    if (event.target === cartButton) {

        showSection(cartSection);
        await load_cart();

        clicked(cartButton);

    }

    if (event.target === historyButton) {

        showSection(historySection);

        clicked(historyButton);
        await load_orders();

    }    
    if (event.target === outStockButton) {

        showSection(outStockSection);
        await load_outStock(true);

        clicked(outStockButton);

    }

    if (event.target === expiredButton) {

        showSection(expiredSection);

        clicked(expiredButton);
        await load_expired(true);

    } 
    // ---------------------------------
    // VIEW PRODUCT
    // ---------------------------------

    if (event.target.classList.contains( "viewProduct")) 
    {
        const product_id =Number(event.target.dataset.id);


        let product = allproducts.find(function(product_required) {
            return product_required.id === product_id;
        }) ||
        outStock.find(function(product_required) {
            return product_required.id === product_id;
        }) ||
        expired.find(function(product_required) {
            return product_required.id === product_id;
        })  


        if (!product) {
            console.log("Product not found");
            return;
        }


        const container = document.querySelector("#modal-content");


        container.innerHTML = "";


        // ---------------------------------
        // PRICE
        // ---------------------------------

        let price_html = "";


        if (product.discount_percent === 0) {
            price_html = `Price : ${escapeHTML(product.price)}`;
        }

        else if (product.discount_percent > 0) {

            const new_price = product.price - (product.price * product.discount_percent) / 100;
            price_html = `

                <del>
                    Price :
                    ${escapeHTML(product.price)}
                </del>

                <span>
                    ${escapeHTML(new_price.toFixed(2))}
                </span>

                <span>
                    DISCOUNT :
                    ${escapeHTML(product.discount_percent)}%
                </span>
            `;

        }


        // ---------------------------------
        // PRODUCT REVIEWS
        // ---------------------------------
        const reviewMap = new Map();

        [...allreviews, ...allwishlistreviews, ...outStockReviews, ...expiredReviews].forEach(function(review) {
            if (review.product_id === product_id) {
                reviewMap.set(review.id, review);
            }
        });

        const product_reviews = [...reviewMap.values()];

        let reviews_html = "";


        if (product_reviews.length === 0) {
            reviews_html = `

                <p class="no-reviews">

                    No reviews yet.

                </p>
            `;
        }
        else {
            product_reviews.forEach(function(review) {
                reviews_html += `
                    <div class="review">

                        <div class="details">

                            <span>
                                ${escapeHTML(review.reviewer_name)}
                            </span>


                            <span>
                                Rating:
                                ${escapeHTML(review.rating)}
                            </span>


                            <span>

                                ${
                                    review.is_verified
                                    ?
                                    "Verified Purchase"
                                    :
                                    "Not Verified"
                                }

                            </span>

                        </div>

                        <div class="comment">

                            ${escapeHTML(review.review_text)}

                        </div>

                    </div>
                `;

            });
        }


        // ---------------------------------
        // MODAL HTML
        // ---------------------------------
        const cartItem = cart.find(function(item) {
            return item.product_id === product_id;
        });

        const alreadyInCart = Boolean(cartItem);

        const selectedQuantity = alreadyInCart
            ? Number(cartItem.quantity_selected)
            : 1;

        const cart_tag = alreadyInCart
            ? "UPDATE CART"
            : "ADD TO CART";
        const new_price =product.price - (product.price * product.discount_percent) / 100;
        let m_date;
        let e_date;

        if(product.manufactured_date){
            m_date = new Date(product.manufactured_date).toDateString();
        }
        else{
            m_date = "NA";
        }
        if(product.expiry_date){
            e_date = new Date(product.expiry_date).toDateString();

        }
        else{
            e_date = "NA";
        }        
        container.innerHTML = `

            <button
                class="modal-close"
                type="button"
                aria-label="close"
            >
                &times;
            </button>


            <div class="img">

                <img
                    src="${escapeHTML(safeImageUrl(product.image_url))}"
                >
            </div>


            <div class="details">
                <p>
                    ${escapeHTML(product.name)}
                </p>
                <p>
                    BRAND:
                    ${escapeHTML(product.brand_name)}
                </p>


                <p>
                    CATEGORY:
                    ${escapeHTML(product.category_name)}
                </p>


                <p>
                    ${price_html}
                </p>


                <p>
                    AVG RATING:
                    ${escapeHTML(product.avg_rating)}
                </p>                

                <p>
                    NO OF AVAILABLE:
                    ${escapeHTML(product.quantity)}
                </p>
                <p>
                    QUANTITY:
                    ${escapeHTML(product.unit_size)} ${escapeHTML(product.unit)}
                </p>
                <p>
                    MANUFACTURE DATE:
                    ${escapeHTML(m_date)}              
                </p>                
                <p>
                    EXPIRY DATE:
                    ${escapeHTML(e_date)}
                </p>
                <p>
                    SHELF LIFE :
                    ${escapeHTML(product.shelf_life_days || "NA")} 
                </p>       
            </div>
            <div class="quantity-control">
                <div>
                    <button class="incrementButton" id="incrementButton" type="button" data-id=${product_id} data-quantity = ${escapeHTML(product.quantity)} data-selected = ${selectedQuantity}>+</button>
                </div>
                <div class=quantity-selected>
                    <span id= "quantity" data-id=${product_id} data-price=${escapeHTML(new_price.toFixed(2))}>${selectedQuantity}</span>
                </div>
                <div>
                    <button class="decrementButton" id="decrementButton" type="button" data-id=${product_id} data-quantity = ${escapeHTML(product.quantity)} data-selected = ${selectedQuantity} >-</button>
                </div>
            </div>
            <button id="moveCart" class="moveCart" type="button" data-totalprice=${escapeHTML(new_price.toFixed(2))} data-id=${product_id}  data-quantity = ${escapeHTML(product.quantity)} data-price = ${escapeHTML(product.price)} data-discount = ${escapeHTML(product.discount_percent)}>${cart_tag}</button>
            <div class="reviews-section">

                <h3>    
                    REVIEWS
                </h3>
                <button id="addReview" class="addReview" type="button" data-id=${product_id}>ADD A REVIEW</button>

                <form id="reviewForm" class="review-form hidden">

                    <h3>Write a Review</h3>
                    <label for="orderIDReview">ENTER THE order_id for VERIFIED BADGE</label>
                    <input type="text" name="orderID" id="orderIDReview" placeholder="MENTION THE ORDER_ID...">

                    <label for="reviewRating">Rating</label>
                    <select id="reviewRating" name="rating" required>
                        <option value="">Select rating</option>
                        <option value="5">5 - Excellent</option>
                        <option value="4">4 - Good</option>
                        <option value="3">3 - Average</option>
                        <option value="2">2 - Poor</option>
                        <option value="1">1 - Very Poor</option>
                    </select>


                    <label for="reviewText">Your Review</label>
                    <textarea
                        id="reviewText"
                        name="review_text"
                        rows="5"
                        maxlength="2000"
                        placeholder="REVIEW...?"
                        required
                    ></textarea>

                    <div class="review-form-actions">
                        <button type="submit">SUBMIT REVIEW</button>
                        <button type="button" id="cancelReview">CANCEL</button>
                    </div>

                    <p id="reviewMessage" role="status"></p>

                </form>


                ${reviews_html}

            </div>
        `;
        updateQuantityButtons();
        modal.classList.add("open");
    }


    // ---------------------------------
    // CLOSE MODAL BUTTON
    // ---------------------------------

    if (event.target.classList.contains("modal-close")
    ) {

        modal.classList.remove(
            "open"
        );

    }


    // ---------------------------------
    // CLICK OUTSIDE MODAL
    // ---------------------------------

    if (event.target === modal) {

        modal.classList.remove(
            "open"
        );

    }
    if(event.target.classList.contains("wishlist")){

        const productID = Number(event.target.dataset.id);
        console.log(`product selected ${productID} ${event.target.textContent}`)

        if (event.target.textContent.trim() === 'ADD TO WISHLIST'){
            console.log(`product to be added ${productID}`)
            try{
                const response = await fetch(`/api/wishlist/add`,{
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        "id" : productID 
                    })
                });

                const data = await response.json();
                if(!response.ok){
                    throw new Error(data.error || `HTTP ${response.status}`);
                }

                if (!wishlist.includes(productID)) {
                    wishlist.push(productID);
                }

                event.target.textContent = "REMOVE FROM WISHLIST";                
                console.log(`product added ${productID}`)
            }
            catch(error){
                console.log(error);
            } 
        }
        else if(event.target.textContent.trim() === 'REMOVE FROM WISHLIST'){
            console.log(`product selected to be removed from wishlist${productID}`)
            const card = wishlistContainer.querySelector(`#product-${event.target.dataset.id}`);
            try{
                const response = await fetch(`/api/wishlist/remove`,{
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        "id" : productID 
                    })
                });

                const data = await response.json();
                if(!response.ok){
                    throw new Error(data.error || `HTTP ${response.status}`);
                }
                console.log(`product removed from wishlist${productID}`)
                // After successful removal
                wishlist = wishlist.filter(id => id !== productID);

                event.target.textContent = "ADD TO WISHLIST";
                if (card) {
                    card.remove();
                }
            }
            catch(error){
                console.log(error);
            }             
        }
    }
    if(event.target.classList.contains("cart")){
        const productID = Number(event.target.dataset.id);
        selectedProduct = products.find(function(product){
            return product.id === productID;
        })
        const available_quantity = selectedProduct.quantity;
    }

    if (event.target.classList.contains("incrementButton")) {

        const quantityDisplay = modal.querySelector("#quantity");

        let selected = Number(quantityDisplay.textContent);
        const available = Number(event.target.dataset.quantity);

        if (selected < available) {
            selected++;
            quantityDisplay.textContent = selected;
        }

        updateQuantityButtons();
    }

    if (event.target.classList.contains("decrementButton")) {

        const quantityDisplay = modal.querySelector("#quantity");

        let selected = Number(quantityDisplay.textContent);

        if (selected > 1) {
            selected--;
            quantityDisplay.textContent = selected;
        }

        updateQuantityButtons();
    }


    if (event.target.classList.contains("moveCart")) {

        const button = event.target;

        const productID = Number(button.dataset.id);

        const selected = Number(
            modal.querySelector("#quantity").textContent
        );

        const discount_percent = Number(button.dataset.discount)
        const available = Number(button.dataset.quantity);
        const price = Number(button.dataset.price);

        if (selected < 1 || selected > available) {
            console.log("Invalid quantity");
            return;
        }

        // Check whether the product already exists in the cart.
        const alreadyInCart = cart.some(function(item) {
            return item.product_id === productID;
        });

        button.disabled = true;

        try {

            if (alreadyInCart) {

                // UPDATE EXISTING CART ITEM
                await editCartQuantity(productID, selected);

                console.log("Cart quantity updated");

            } else {

                // ADD NEW PRODUCT TO CART


                const response = await fetch("/api/cart_add", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        "product_id": productID,
                        "selected": selected
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.error || "Failed to add product"
                    );
                }

                await load_cart();

                console.log("Product added to cart");
            }

            button.textContent = "UPDATE CART";

        } catch (error) {

            console.error("Cart operation failed:", error);

        } finally {

            updateQuantityButtons();
        }
    }


    if (event.target.classList.contains("removeCartbutton")) {

        const productID = Number(event.target.dataset.id);

        try {
            const response = await fetch("/api/cart_remove", {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    product_id: productID
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to remove product");
            }

            await load_cart();

        } catch (error) {
            console.error("error:", error);
        }
    }
    if (event.target.classList.contains("addReview")) {
        const form = modal.querySelector("#reviewForm");
        form.classList.remove("hidden");
    }

    if (event.target.id === "cancelReview") {
        const form = modal.querySelector("#reviewForm");
        form.reset();
        form.classList.add("hidden");
    }    
});


// =====================================================
// INITIAL LOAD
// =====================================================

load_products(true);
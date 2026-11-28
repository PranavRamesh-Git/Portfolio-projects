
const modal = document.querySelector("#view-modal");
const closeModal = document.querySelector("#close-modal");
const summary = document.querySelector("#summary");

const discoverButton = document.querySelector("#discoverButton");
const mybooksButton = document.querySelector("#mybooksButton");


const discoverSection = document.querySelector("#discover-section");
const mybooksSection = document.querySelector("#mybooks-section");


const pageSections = document.querySelectorAll(".pagesection");

const discoverContainer = document.querySelector("#books-container");
const mybooksContainer = document.querySelector("#mybooks-container");

const searchInput = document.querySelector("#search");
const orderBy = document.querySelector("#orderby");
const applyButton = document.querySelector("#submit");
const clearButton = document.querySelector("#clear");

let allBooks = [];
let myBooks = [];

// ---------------- FLASH MESSAGES ----------------

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

// ---------------- SECTION SWITCHING ----------------

function showSection(section) {
    pageSections.forEach(page => {
        page.classList.remove("active");
    });

    section.classList.add("active");
}

discoverButton.addEventListener("click", () => {
    showSection(discoverSection);
    discoverContainer.innerHTML = "";
    discoverBooks();
});

mybooksButton.addEventListener("click", () => {
    showSection(mybooksSection);
    load_mybooks();
    

});



// ---------------- LOADING / ERROR ----------------

function showLoading(container) {
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Loading books...</p>
        </div>
    `;
}

function showError(container, message) {
    container.textContent = message;
}

// ---------------- DISCOVER BOOKS ----------------

async function discoverBooks() {
    const searchValue = searchInput.value.trim();
    const sortValue = orderBy.value;

    if (!searchValue) {
        discoverContainer.textContent = "Please enter a book or author.";
        return;
    }

    showLoading(discoverContainer);

    try {
        const params = new URLSearchParams({
            search: searchValue,
            orderby: sortValue
        });

        const response = await fetch(`/api/discover?${params}`);

        if (response.status === 401) {
            window.location.href = "/bookworm/login";
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }

        allBooks = data.all_books || [];
        myBooks = data.mybooks || [];

        renderBooks(allBooks, discoverContainer, myBooks);

    } catch (error) {
        console.error("Error fetching books:", error);
        showError(discoverContainer, "Unable to load books. " + error.message);
    }
}

async function load_mybooks() {
    showLoading(mybooksContainer);
    try{
        const response = await fetch(`/api/mybooks`);
        if (response.status === 401) {
            window.location.href = "/bookworm/login";
            return;
        }        
        const data = await response.json();

        if(!response.ok){
            throw new Error(data.error ||  "Unable to load My Books");
        }

        if (!data.status) {
            mybooksContainer.textContent =
                "You haven't added any books yet.";

            return;
        }

        myBooks = data.mybooks;

        rendermybooks(myBooks,mybooksContainer);

    }
    catch(error){
        console.error(
            "Error loading My Books:",
            error
        );

        showError(
            mybooksContainer,
            "Unable to load your books."
        );
    }
}

// ---------------- RENDER BOOKS ----------------

function renderBooks(books, container, mybooks) {
    container.innerHTML = "";

    if (books.length === 0) {
        container.textContent = "No books found.";
        return;
    }

    books.forEach(book => {
        const savedBook = mybooks.find(mybook =>
            mybook.google_book_id === book.google_book_id
        );

        const readingStatus = savedBook
            ? "MY BOOKS"
            : "ADD TO MYBOOKS";

        const card = document.createElement("div");
        card.className = "book-card";

        const imageBox = document.createElement("div");
        imageBox.className = "img";

        const image = document.createElement("img");
        image.src = book.cover_url || "/static/images/NA.png";
        image.alt = "Book cover";
        image.loading = "lazy";

        image.onerror = function() {
            this.onerror = null;
            this.src = "/static/images/NA.png";
        };

        imageBox.append(image);

        const title = document.createElement("p");
        title.textContent = `TITLE: ${book.title || "Unknown"}`;

        const author = document.createElement("p");
        author.textContent = `AUTHOR: ${
            book.authors?.length
                ? book.authors.join(", ")
                : "Unknown author"
        }`;

        const published = document.createElement("p");
        published.textContent = `PUBLISHED: ${
            book.published_date || "Unknown"
        }`;

        const summaryButton = document.createElement("button");
        summaryButton.type = "button";
        summaryButton.className = "view-summary";
        summaryButton.dataset.id = book.google_book_id;
        summaryButton.textContent = "VIEW SUMMARY";

        const statusButton = document.createElement("button");
        statusButton.type = "button";
        statusButton.className = "my-list";
        statusButton.dataset.id = book.google_book_id;
        statusButton.textContent = readingStatus;

        card.append(
            imageBox,
            title,
            author,
            published,
            summaryButton,
            statusButton
        );

        container.append(card);
    });
}

function rendermybooks(books, container) {
    container.innerHTML = "";

    if (books.length === 0) {
        container.textContent = "No books found.";
        return;
    }

    books.forEach(book => {
        const readingStatus = book.reading_status
            ? "MY BOOKS"
            : "ADD TO MYBOOKS";

        const card = document.createElement("div");
        card.className = "book-card";

        const imageBox = document.createElement("div");
        imageBox.className = "img";

        const image = document.createElement("img");
        image.src = book.image_url || "/static/images/NA.png";
        image.alt = "Book cover";
        image.loading = "lazy";
        imageBox.append(image);

        const title = document.createElement("p");
        title.textContent = `TITLE: ${book.title || "Unknown"}`;

        const author = document.createElement("p");
        author.textContent = `AUTHOR: ${
            book.authors?.length
                ? book.authors.join(", ")
                : "Unknown author"
        }`;

        const published = document.createElement("p");
        published.textContent = `PUBLISHED: ${
            book.published_date || "Unknown"
        }`;

        const summaryButton = document.createElement("button");
        summaryButton.type = "button";
        summaryButton.className = "view-summary";
        summaryButton.dataset.id = book.google_book_id;
        summaryButton.textContent = "VIEW SUMMARY";

        const statusSelect = document.createElement("select");
        statusSelect.className = "reading-status";
        statusSelect.dataset.id = book.book_id;

        const statuses = [
            "ON MY BOOKS",
            "ON READING LIST",
            "CURRENTLY READING",
            "FINISHED",
            "DROPPED",
            "REREADING"
        ];

        statuses.forEach(status => {
            const option = document.createElement("option");
            option.value = status;
            option.textContent = status;

            statusSelect.append(option);
        });

        statusSelect.value = book.reading_status || "ON MY BOOKS";
        statusSelect.dataset.current_status = statusSelect.value.trim();

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "remove-book";
        removeButton.dataset.id = book.book_id;
        removeButton.textContent = "REMOVE";

        card.append(
            imageBox,
            title,
            author,
            published,
            summaryButton,
            statusSelect,
            removeButton
        );

        container.append(card);
    });
}

// ---------------- SEARCH BUTTONS ----------------

applyButton.addEventListener("click", discoverBooks);

clearButton.addEventListener("click", () => {
    searchInput.value = "";
    orderBy.value = "relevance";

    allBooks = [];
    myBooks = [];

    discoverContainer.textContent = "Search for books to begin.";
});

searchInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        discoverBooks();
    }
});

// ---------------- VIEW SUMMARY ----------------

document.addEventListener("click", event => {
    if (!event.target.classList.contains("view-summary")) {
        return;
    }

    const googleId = event.target.dataset.id;

    const selectedBook = allBooks.find(book =>
        book.google_book_id === googleId
    ) || myBooks.find(book =>
        book.google_book_id === googleId       
    );

    if (!selectedBook) return;

    summary.textContent =
        selectedBook.summary || selectedBook.description || "No description available.";

    modal.classList.add("open");
});


mybooksContainer.addEventListener("click", async function(event) {
    if(event.target.classList.contains("remove-book")){
        const book_id = Number(event.target.dataset.id);
        const response = await fetch('/api/mybooks/remove',{
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "book_id": book_id
            })
        });

        if(response.status === 401){
            window.href.location = "/bookworm/login";
            return;
        }

        const data = await response.json();

        if(!response.ok){
            console.log(data.error);
        }
        const card = event.target.closest(".book-card");
        card.remove();
    }


});

mybooksContainer.addEventListener('change', async function(event){
    if(event.target.classList.contains("reading-status")){
        const select = event.target;
        const book_id = Number(event.target.dataset.id);
        const oldStatus = select.dataset.current_status ;
        const newStatus = select.value;
        console.log(book_id);
        console.log(oldStatus);
        console.log(newStatus);

        const response = await fetch(`/api/mybooks/status_change`, {
            method: "PATCH",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "book_id": book_id,
                "reading_status": oldStatus,
                "new_status": newStatus
            })
        })

        const data = await response.json();
        if(!response.ok){
            console.log(data.error);
        }
        
    }

});

// ---------------- CLOSE MODAL ----------------

closeModal.addEventListener("click", () => {
    modal.classList.remove("open");
});

modal.addEventListener("click", event => {
    if (event.target === modal) {
        modal.classList.remove("open");
    }
});


document.addEventListener("click", async function (event) {

    if (!event.target.classList.contains("my-list")) {
        return;
    }

    const button = event.target;

    const google_book_id = button.dataset.id;

    const selectedBook = allBooks.find(book =>
        book.google_book_id === google_book_id
    );

    if (!selectedBook) {
        console.error("Book not found in allBooks");
        return;
    }

    const summary =
        selectedBook.description || "No description available.";

    const title =
        selectedBook.title || "NA";

    const image_url =
        selectedBook.cover_url || "/static/images/NA.png";

    try {
        button.disabled = true;

        const response = await fetch("/api/discover/addtoMybooks", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                google_book_id: google_book_id,
                title: title,
                summary: summary,
                image_url: image_url
            })
        });

        if (response.status === 401) {
            window.location.href = "/bookworm/login";
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Failed to save book"
            );
        }

        // Update UI only after successful server response
        button.textContent = "MY BOOKS";

        // Update local JS state
        myBooks.push({
            google_book_id: google_book_id,
            reading_status: "ON READING LIST"
        });

        console.log(data.message);

    } catch (error) {

        console.error(
            "Add to My Books error:",
            error
        );

        alert(error.message);

    } finally {

        button.disabled = false;
    }
});


// ---------------- INITIAL STATE ----------------

discoverContainer.textContent = "Search for books to begin.";

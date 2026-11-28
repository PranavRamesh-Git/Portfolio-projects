import { useEffect, useState } from "react";
import BookCard from "../components/BookCard";
import Modal from "../components/Modal"

function Discover() {
    const [allBooks, setAllBooks] = useState([]);
    const [myBooks, setMyBooks] = useState([]);

    const [search, setSearch] = useState("");
    const [orderby, setOrderBy] = useState("relevance");

    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("Please enter a book or author.");

    const [bookDetails, setBookDetails] = useState(null);
    const [shelfActionError,setShelfActionError] = useState("");
    const [savingBookId,setSavingBookId] = useState(null);
    const [csrfToken,setCsrfToken] = useState(null);

    useEffect(()=> {
        async function get_Csrf(){
            try {
                const response = await fetch("/api/csrf-token");

                if (!response.ok) {
                    throw new Error("Failed to fetch CSRF token");
                }

                const data = await response.json();

                setCsrfToken(data.csrf_token);

            } catch (error) {
                console.error("CSRF ERROR:", error);
                setError(error.message);
            }
        }
        get_Csrf()
    },[])

    async function discoverBooks() {
        if (!search.trim()) {
            setAllBooks([]);
            setMyBooks([]);
            setMessage("Please enter a book or author.");
            return;
        }

        setLoading(true);
        setMessage("");

        try {
            const params = new URLSearchParams();

            params.set("search", search.trim());
            params.set("orderby", orderby);

            const response = await fetch(`/api/discover?${params}`);

            if (response.status === 401) {
                window.location.href = "/bookworm/login";
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            setAllBooks(data.all_books ?? []);
            setMyBooks(data.mybooks ?? []);

            if ((data.all_books ?? []).length === 0) {
                setMessage("No books found.");
            }

        } catch (error) {
            console.error("Error fetching books:", error);

            setAllBooks([]);
            setMyBooks([]);
            setMessage("Error fetching books.");

        } finally {
            setLoading(false);
        }
    }

    function clearFilters() {
        setSearch("");
        setOrderBy("relevance");
        setAllBooks([]);
        setMyBooks([]);
        setMessage("Please enter a book or author.");
    }

    function onViewDetails(book) {
        setBookDetails(book.summary || book.description || "No description available.");

        
    }
    function onClose(){
        setBookDetails(null);
    }
    async function shelfActions(book) {
        const isSaved = book.shelfStatus;

        const url = isSaved
            ? "/api/mybooks/remove"
            : "/api/discover/addtoMybooks";

        const payload = isSaved
            ? {
                google_book_id: book.google_book_id
            }
            : {
                google_book_id: book.google_book_id,
                title: book.title,
                summary: book.description || "",
                image_url: book.cover_url || "/static/images/NA.png"
            };

        setShelfActionError("");
        setSavingBookId(book.google_book_id);

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(payload)
            });

            if (response.status === 401) {
                window.location.href = "/bookworm/login";
                return;
            }

            const data = await response.json();

            if (!response.ok || data.error) {
                throw new Error(
                    data.error || `HTTP ${response.status}`
                );
            }
            /* we get data.success for removing a book */
            if (isSaved && !data.success) {
                throw new Error("Unable to remove book");
            }
            /* data.message when we add a book */
            if (!isSaved && !data.message) {
                throw new Error("Unable to add book");
            }

            setAllBooks(function(previousBooks) {

                const updatedBooks = previousBooks.map(function(currentBook) {

                    if (currentBook.google_book_id === book.google_book_id) {

                        return {...currentBook,shelfStatus: !isSaved};

                    } else {

                        return currentBook;

                    }

                });

                return updatedBooks;

            });

        } catch (error) {
            console.error("Shelf action failed:", error);
            setShelfActionError(error.message);

        } finally {
            setSavingBookId(null);
        }
    }

    return (
        <section
            id="discover-section"
            className="pagesection active"
        >
            <h1>DISCOVER BOOKS</h1>

            <div className="searchFilters">
                <div className="search">
                    <input
                        id="search"
                        name="search"
                        placeholder="SEARCH BOOKS, AUTHORS..."
                        type="text"
                        value={search}
                        onChange={(event) =>
                            setSearch(event.target.value)
                        }
                    />
                </div>

                <div className="filters">
                    <select
                        name="orderby"
                        id="orderby"
                        value={orderby}
                        onChange={(event) =>
                            setOrderBy(event.target.value)
                        }
                    >
                        <option value="relevance">
                            RELEVANCE
                        </option>
                        <option value="newest">
                            NEWEST
                        </option>
                    </select>

                    <div className="applySearch">
                        <button
                            id="submit"
                            type="button"
                            onClick={discoverBooks}
                            disabled={loading}
                        >
                            APPLY
                        </button>

                        <button
                            id="clear"
                            type="button"
                            onClick={clearFilters}
                        >
                            CLEAR
                        </button>
                    </div>
                </div>
            </div>

            <div
                className="books-container"
                id="books-container"
            >
                {loading ? (
                    <h3>LOADING...</h3>
                ) : allBooks.length > 0 ? (
                    allBooks.map(book => (
                        <BookCard key={book.google_book_id} book={book}  onViewDetails={onViewDetails} shelfActions={shelfActions} isSaving={savingBookId === book.google_book_id}/>
                        
                    ))
                ) : (
                    <h3>{message}</h3>
                )}
            </div>
            {shelfActionError && (
                <p className="flash-message error">
                    {shelfActionError}
                </p>
            )} 
        
            <Modal bookDetails={bookDetails} onClose={onClose} />
        </section>
    );
}

export default Discover;
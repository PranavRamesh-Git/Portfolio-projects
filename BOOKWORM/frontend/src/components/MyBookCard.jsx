function MyBookCard({book,onViewDetails,statusActions,shelfActions}) {
    return (
        <div className="book-card">
            <div className="img">
                <img
                    src={book.image_url ||  './NA.png'}
                    alt={`Cover of ${book.title || "Unknown book"}`}
                />
            </div>

            <p>Title: {book.title || "Unknown"}</p>

            <p>
                Author: {Array.isArray(book.authors)
                    ? book.authors.join(", ")
                    : book.authors || "NA"}
            </p>

            <p>Published: {book.published_date || "Unknown"}</p>

            <button
                type="button"
                className="view-summary"
                onClick={() => onViewDetails(book)}
            >
                VIEW SUMMARY
            </button>

            <label htmlFor={`reading-status-${book.google_book_id}`}>
                Reading status
            </label>

            <select
                id={`reading-status-${book.google_book_id}`}
                className="reading-status"
                name="reading_status"
                value={book.reading_status || "ON MY BOOKS"}
                onChange={(event) =>
                    statusActions(book, event.target.value)
                }
            >
                <option value="ON MY BOOKS">ON MY BOOKS</option>
                <option value="ON READING LIST">ON READING LIST</option>
                <option value="CURRENTLY READING">CURRENTLY READING</option>
                <option value="FINISHED">FINISHED</option>
                <option value="DROPPED">DROPPED</option>
                <option value="REREADING">REREADING</option>
            </select>

            <button
                type="button"
                className="my-list"
                onClick={() => shelfActions(book)}
            >
                REMOVE
            </button>
        </div>
    );
}

export default MyBookCard;
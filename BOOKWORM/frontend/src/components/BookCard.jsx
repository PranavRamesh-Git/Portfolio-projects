function BookCard({book,onViewDetails,shelfActions,isSaving=false}){
    return (
        <div className="book-card">
            <div className="img">
                <img src={book.cover_url || './NA.png'} alt="Book cover"/>
            </div>
            <p>Title: { book.title || "Unknown" }</p>
            <p>Author: {book.authors?.join(" ,") || "NA"}</p>
            <p>Published: {book.published_date || "Unknown"}</p>
            <button type="button" className="view-summary" data-id={book.google_book_id} onClick={()=>{onViewDetails(book)}}  >VIEW SUMMARY</button>
            <button type="button" className="my-list" data-id={book.google_book_id} onClick={()=>{shelfActions(book)}}>{ isSaving?  "SAVING..." : book.shelfStatus ? "ON MY BOOKS"  : "ADD TO MYBOOKS" }</button>
        </div>
    );

}

export default BookCard;
import { use } from "react";
import { useState,useEffect } from "react";
import Modal from '../components/Modal';
import MyBookCard from "../components/MyBookCard";

function MyBooks (){
    const [myBooks, setMyBooks] = useState([]);
    const [myLoading, setMyLoading] = useState(false);
    const [message, setMessage] = useState("You haven't added any books yet");
    const [bookDetails, setBookDetails] = useState(null);
    const [shelfActionError,setShelfActionError] = useState("");
    const [statusActionError,setStatusActionError] = useState("");
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

    useEffect(()=>{
        async function load_mybooks() {
            setMyLoading(true);
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

                if (data.status) {
                    setMyBooks(data.mybooks);
                }
            }
            catch(error){
                console.error("Error loading My Books:",error);
                setMessage("UNABLE TO LOAD ANY BOOKS")


            }
            finally{
                setMyLoading(false);
            }
        }
        load_mybooks()
    },[])



    function onViewDetails(book) {
        setBookDetails(book.summary || book.description || "No description available.");

        
    }
    function onClose(){
        setBookDetails(null);
    }  

    async function removeShelf(book) {
        setShelfActionError("");
        try{
            const response = await fetch(`/api/mybooks/remove`,{
                method: "POST",
                headers:{
                    "content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    "google_book_id": book.google_book_id
                })

            });
            const data = await response.json();
            if(!response.ok){
                throw new Error(data.error || `HTTP ERROR: ${response.status}`);
            }
            if (!data.success){
                throw new Error("Unable to remove book");
            }
            setMyBooks(function(previousBooks) {

                const updatedBooks = previousBooks.filter(
                    function(currentBook) {
                        return currentBook.google_book_id !== book.google_book_id;
                    }
                );

                return updatedBooks;
            });
        }
        catch(error){
            console.log("Error");
            setShelfActionError(error.message);

        }
        
    }
    async function statusActions(book,newStatus) {
        setStatusActionError("");
        try{
            const response = await fetch(`/api/mybooks/status_change`,{
                method: "PATCH",
                headers: {
                    "content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    "google_book_id": book.google_book_id,
                    "reading_status": book.reading_status,
                    "new_status": newStatus
                })
            });
            const data = await response.json();
            if(!response.ok){
                throw new Error(data.error || `HTTP ERROR: ${response.status}`);
            }
            if (!data.success){
                throw new Error("Unable to remove book");
            }
            setMyBooks(function(previousBooks){
                const updatedBooks = previousBooks.map(function(currentBook){
                    if(book.google_book_id === currentBook.google_book_id){
                        return {...currentBook,reading_status:newStatus}
                    }
                    else{
                        return currentBook;
                    }
                })
                return updatedBooks;

            })
        }
        catch(error){
            console.log("Error");
            setStatusActionError(error.message);
        }
        
    }
    return (
        <section id="mybooks-section" className="pagesection active">
            <h1>MY BOOKS</h1>
            <div className="books-container" id="mybooks-container">
                {myLoading ? (
                    <h3>LOADING...</h3>
                ) : myBooks.length > 0 ? (
                    myBooks.map(book => (
                        <MyBookCard key={book.google_book_id} book={book}  onViewDetails={onViewDetails} statusActions={statusActions} shelfActions={removeShelf}/>
                        
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
            {statusActionError && (
                <p className="flash-message error">
                    {statusActionError}
                </p>
            )}        
            <Modal bookDetails={bookDetails} onClose={onClose} />            
        </section>
    );
}

export default MyBooks;
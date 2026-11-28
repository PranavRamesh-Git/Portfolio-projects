function Navbar({activePage,setActivePage}){
    return (
        <>
            <nav className="navbar">
                <button type="button" onClick={()=>setActivePage("discover")}>DISCOVER</button>
                <button type="button" onClick={()=> setActivePage("mybooks")}>MY BOOKS</button>
                <a href="/bookworm/logout">LOGOUT</a>
            </nav>
        </>
    );

}
export default Navbar;
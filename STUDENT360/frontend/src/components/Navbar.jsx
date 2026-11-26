function Navbar ({ activePage,setActivePage}){
    return (
        <header className="header">
            <div className="title">
                <h1 className="title">STUDENT-360</h1>
            </div>
            <nav className="navbar">
                <div className="btn">
                    <button type="button"  className={ activePage === "students" ? "nav-opt active" : "nav-opt"} onClick={()=>setActivePage("students")}>
                        STUDENT PROFILES
                    </button>
                </div>
                <div className="btn">
                    <button type="button"  className={ activePage === "analytics"  ? "nav-opt active" : "nav-opt"} onClick={()=>setActivePage("analytics")}>
                        ANALYTICS
                    </button>
                </div>
                <a href="/student360/logout" className="logout">
                    LOGOUT
                </a>
            </nav>
        </header>
    );
}
export default Navbar;
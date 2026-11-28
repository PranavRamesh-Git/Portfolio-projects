import { useState,useEffect } from 'react';
import Navbar from './components/Navbar';
import Discover from './pages/Discover';
import MyBooks from './pages/MyBooks';
import './style.css';

function App(){
  const [activePage,setActivePage] = useState("discover");
  const [msg,setMsg] = useState("");

  return (
    <>
      <header>
        <Navbar activePage={activePage} setActivePage={setActivePage} />
        { msg && (
          <div className="flash-message {{ category }}">
              { msg }
              <button className="flash-close" type="button" aria-label="close" onClick={()=>setMsg("")}>&times;</button>                        
          </div>
        )}
      </header>
      <main>
        {activePage === "discover" ? <Discover />  : <MyBooks />}

      </main>
    </>  

  );

}
export default App

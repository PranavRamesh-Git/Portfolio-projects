import { useState,useEffect } from "react";
import Navbar from "./components/Navbar";
import StudentProfiles from "./pages/StudentProfiles";
import StudentMarksheet from "./components/StudentMarksheet";
import StudentAnalytics from "./pages/StudentAnalytics";
import "./style.css";

function App() {
  const [activePage,setActivePage] = useState("students");
  const [classes,setClasses] = useState([]);
  const [error,setError] = useState("");

  useEffect(() => {
    async function get_classAccess() {
        try {
            const response = await fetch(`/api/class_access`);
            const data = await response.json();
            if(!response.ok){ 
                throw new Error(data.error || "Failed to fetch classes");
            }
            setClasses(data.classes);
            console.log(data.classes);
        }
        catch(err){
            console.log("ERROR: ",err);
            setError(err.message);
        }        
    }
    get_classAccess();    
  },[]);

  return (
    <>
      <Navbar activePage={activePage} setActivePage={setActivePage}/>
      {error && (
          <p className="flash-message error">
              {error}
          </p>
      )}
      <main>
        {activePage === "students" ? (
            <StudentProfiles classes={classes}/>
          ) : (
            <StudentAnalytics/>
          )}
      </main>    
    </>

  );

}

export default App;
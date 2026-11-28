import { useState,useEffect } from "react";
import MarksAnalytics from "../components/MarksAnalytics"
function StudentAnalytics(){
    const [activeGrade,setActiveGrade] = useState(null);
    const [activeOption,setActiveOption] = useState(null);
    const grades = ["6","7","8","9","10","11","12"]
    const classSections = {
        "12": ["12A", "12B", "12C", "12D"],
        "11": ["11A", "11B", "11C", "11D"],
        "10": ["10A", "10B", "10C"],
        "9": ["9A", "9B", "9C"],
        "8": ["8A", "8B", "8C"],
        "7": ["7A", "7B", "7C"],
        "6": ["6A", "6B", "6C"]
    };
    const [rankedList,setRankedList] = useState(null);
    const [overall,setOverall] = useState(null);
    const [subData,setSubData] = useState(null);
    const [analyticsError,setAnalyticsError] = useState("");

    const [csrfToken, setCsrfToken] = useState(null);

    useEffect(() => {

        async function getCsrfToken() {
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

        getCsrfToken();

    }, []);    


    function makeActive(grade){
        setActiveGrade(grade);
        setActiveOption(null);
        setOverall(null);
        setRankedList(null);
        setSubData(null);
        setAnalyticsError("");    
    }
    function makeActiveOverall(option){
        setActiveOption(option);
        getOverall(option);
        
    }    
    function makeActiveSection(option){
        setActiveOption(option);
        getSectionSpecific(option,activeGrade);
        
    }
    async function getOverall(activeOption) {
        setOverall(null);
        setRankedList(null);
        setSubData(null);
        setAnalyticsError("");
        try{
            const response = await fetch(`/api/analytics/ClassOverall`,{
                method: "POST",
                headers: {
                    "Content-Type": 'application/json',
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    "assessment_class" : activeOption
                })

            });
            const data = await response.json();
            if(!response.ok){
                throw new Error(data.error || `${response.status}`);
            }
            if(data.status === "success"){
                setOverall(data.overall);
                setRankedList(data.ranked_list);
                setSubData(data.subData);                                
            }
            else{
                throw new Error("Unable to load the analytics");
            }
        }
        catch(error){
            console.log("ERROR: ",error);
            setAnalyticsError(error.message);
        }        
    }
    async function getSectionSpecific(activeOption,activeGrade) {
        setOverall(null);
        setRankedList(null);
        setSubData(null);
        setAnalyticsError("");    
        try{
            const response = await fetch(`/api/analytics/SectionSpecific`,{
                method: "POST",
                headers: {
                    "Content-Type": 'application/json',
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    "assessment_class" : activeGrade,
                    "class_name" : activeOption
                })

            });
            const data = await response.json();
            if(!response.ok){
                throw new Error(data.error || `${response.status}`);
            }
            if(data.status === "success"){
                setOverall(data.overall);
                setRankedList(data.ranked_list);
                setSubData(data.subData);                                
            }
            else{
                throw new Error("Unable to load the analytics");
            }
        }
        catch(error){
            console.log("ERROR: ",error);
            setAnalyticsError(error.message);
        }     
    }

    return (
        <section id="analytics-page"  className="analytics-page active">
            <h2>ANALYTICS</h2> 
            <nav id="analytics-classes" className="analytics-classes">
                {grades.map(function(grade){
                    return (
                        <button key={grade} className={activeGrade === grade ? "class-btn active" : "class-btn"} id={`cl${grade}`}onClick={()=> makeActive(grade)}>CLASS {grade}</button>
                    );
                    
                })}
            </nav>
            <div className="section-specific" id="section-specific">
                { activeGrade && (
                    <div id={`cl${activeGrade}`} className="opt active">
                        <button type="button" className={activeGrade === activeOption ?"overall active" : "overall"} onClick={()=> makeActiveOverall(activeGrade)}>CLASS {activeGrade}</button>
                        {classSections[activeGrade].map(function(section){
                            return (
                                <button type="button" key={section} className={activeOption === section ? "classes active" : "classes"} onClick={()=>makeActiveSection(section)}>CLASS {section}</button>
                            );
                        })}

                    </div>
                )}                                        
            </div> 
            {analyticsError && (
                <p className="flash-message error">{analyticsError}</p>
            )} 
            {overall && subData && rankedList && ( <MarksAnalytics overall={overall} rankedList={rankedList} subData={subData}/> )}                         
     
        </section>
    );
}

export default StudentAnalytics;


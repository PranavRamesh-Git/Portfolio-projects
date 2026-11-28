import { useState,useEffect } from "react";
import StudentCard from "../components/StudentCard";
import StudentDetailsModal from "../components/StudentModal";
import StudentMarksheet from "../components/StudentMarksheet";
import MarksAnalytics from "../components/MarksAnalytics";
function StudentProfiles({ classes }) {

    // STATE VARIABLES
    const [className, setClassName] = useState("");
    const [search, setSearch] = useState("");
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(false);

    const [message, setMessage] = useState(
        "SELECT YOUR CLASS OR SEARCH FOR A STUDENT"
    );

    const [studentDetails, setStudentDetails] = useState(null);
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [detailsError,setDetailsError] = useState("");

    const[totalMarks,setTotalMarks] = useState(null);
    const[stats,setStats] = useState(null);
    const[subs,setSubs] = useState(null);
    const[subMarks,setSubMarks] = useState(null);
    const [marksheetLoading, setMarksheetLoading] = useState(false);
    const [marksheetError,setMarksheetError] = useState("");

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


    // FETCH STUDENTS FROM FLASK
    async function load_students() {

        if (!className && !search.trim()) {
            setStudents([]);
            setMessage("SELECT A CLASS OR SEARCH FOR A STUDENT");
            return;
        }

        setLoading(true);
        setMessage("");

        const params = new URLSearchParams();

        if (className) {
            params.set("class_name", className);
        }

        if (search.trim()) {
            params.set("search", search.trim());
        }

        try {

            const response = await fetch(
                `/api/students?${params.toString()}`
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || `HTTP ERROR: ${response.status}`
                );
            }

            setStudents(data.students);

            if (data.students.length === 0) {
                setMessage("NO STUDENT RECORDS AVAILABLE");
            }

        } catch (error) {

            console.error("ERROR:", error);

            setStudents([]);
            setMessage("ERROR, TRY AGAIN LATER!");

        } finally {

            setLoading(false);
        }
    }
    async function viewStudentDetails(student) {
        setStudentDetails(null);
        setDetailsError("");
        setDetailsLoading(true);


        try{
            const response = await fetch(`/api/studentDetails`,{
                method: "POST",
                headers: {
                    "Content-Type": 'application/json',
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    "student_id" : student.student_id,
                    "class_name" : student.class_name
                })

            });
            const data = await response.json();
            if(!response.ok){
                throw new Error(data.error || `${response.status}`);
            }
            if(data.status !== "success"){
                throw new Error("Failed to load student details");
            }
            setStudentDetails(data.student_details);
        }
        catch(error){
            console.log("ERROR: ",error);
            setDetailsError(error.message);
        }
        finally{
            setDetailsLoading(false);
        }        
    }
    async function viewStudentMarksheet(student){
        setTotalMarks(null);
        setSubMarks(null);
        setStats(null);
        setSubs(null);
        setMarksheetError("");
        setMarksheetLoading(true);

        try{
            const response = await fetch(`/api/studentMarksheet`,{
                method: "POST",
                headers: {
                    "Content-Type": 'application/json',
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    "student_id" : student.student_id,
                    "class_name" : student.class_name
                })

            });
            const data = await response.json();
            if(!response.ok){
                throw new Error(data.error || `${response.status}`);
            }
            if(data.status !== "success"){
                throw new Error("UNABLE TO LOAD MARKS");
                
            }
            else{
                setTotalMarks(data.totalMarks);
                setSubMarks(data.subMarks);
                setStats(data.stats);
                setSubs(data.subs);                
            }
        }
        catch(error){
            console.log("ERROR: ",error);
            setMarksheetError(error.message);
        }
        finally{
            setMarksheetLoading(false);
        }        
    }


    // CLEAR SEARCH AND CLASS FILTERS
    function clearFilters() {

        setSearch("");
        setClassName("");
        setStudents([]);

        setMessage(
            "SELECT YOUR CLASS OR SEARCH FOR A STUDENT"
        );
    }


    // JSX
    return (

        <section
            id="students-page"
            className="students-page active"
        >

            <h2>YOUR STUDENTS</h2>


            {/* CLASS DROPDOWN */}

            <div className="class-filter">

                <span className="filter-title">
                    YOUR CLASSES
                </span>

                <select
                    name="class_name"
                    id="class_name"
                    value={className}
                    onChange={(event) =>
                        setClassName(event.target.value)
                    }
                >

                    <option value="">SELECT CLASS</option>

                    {classes.map(function(item) {

                        return (
                            <option key={item} value={item}>
                                {item}
                            </option>
                        );

                    })}

                </select>

            </div>


            {/* STUDENT SEARCH */}

            <div className="searchbar">

                <input
                    type="text"
                    className="profile-search"
                    id="profile-search"
                    placeholder="SEARCH ..."
                    name="search"
                    value={search}
                    onChange={(event) =>
                        setSearch(event.target.value)
                    }
                />

            </div>


            {/* APPLY AND CLEAR BUTTONS */}

            <div className="buttons">

                <button
                    type="button"
                    id="clear-filters"
                    onClick={clearFilters}
                >
                    CLEAR
                </button>

                <button
                    type="button"
                    id="search-filters"
                    onClick={load_students}
                    disabled={loading}
                >
                    APPLY
                </button>

            </div>


            {/* STUDENT CARDS */}

            <div
                className="profile-container"
                id="profile-container"
            >

                {loading ? (

                    <h3>LOADING STUDENTS...</h3>

                ) : students.length > 0 ? (

                    students.map(function(student) {

                        return (
                            <StudentCard
                                key={student.student_id}
                                student={student}
                                onViewDetails={viewStudentDetails}
                                onViewMarksheet={viewStudentMarksheet}
                            />
                        );

                    })

                ) : (

                    <h3>{message}</h3>

                )}

            </div>
            {detailsLoading && (
                <p>LOADING STUDENT DETAILS...</p>
            )}

            {detailsError && (
                <p className="flash-message error">
                    {detailsError}
                </p>
            )} 
            {marksheetLoading && <p>LOADING MARKSHEET...</p>}

            {marksheetError && (
                <p className="flash-message error">{marksheetError}</p>
            )}                       
            <StudentDetailsModal studentDetails = {studentDetails} onClose = {() => setStudentDetails(null)}/>
            <StudentMarksheet totalMarks={totalMarks} subMarks={subMarks} subs={subs} stats={stats} onClose={() => setSubMarks(null)}/>

        </section>
    );
}

export default StudentProfiles;

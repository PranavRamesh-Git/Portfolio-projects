function StudentDetailsModal({studentDetails, onClose}) {
    if (!studentDetails){
        return null;        
    }

    return (
        <div className="modal-overlay active" id="student-modal">
            <div className="student-modal">
                <div id="student-modal-container">
                    <h2>STUDENT DETAILS</h2>

                    <p>EMAIL: {studentDetails.email}</p>
                    <p>PHONE NO: {studentDetails.phone_no}</p>
                    <p>DOB: {studentDetails.dob ? new Date(studentDetails.dob).toLocaleDateString("en-GB") : "NA" }</p>

                    <p>SUBJECTS:</p>

                    <ul className="list-container">
                        <li>{studentDetails.sub1}</li>
                        <li>{studentDetails.sub2}</li>
                        <li>{studentDetails.sub3}</li>
                        <li>{studentDetails.sub4}</li>
                        <li>{studentDetails.sub5}</li>
                    </ul>                    
                </div>
                <button type="button" className="close-modal" id="modal-close-btn" onClick={onClose}>CLOSE</button>
            </div>
        </div>
    );
}
export default StudentDetailsModal;

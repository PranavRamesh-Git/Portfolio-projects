function StudentCard({student, onViewDetails,onViewMarksheet}) {
    return(
        <div className="student-profileCard">
            <h3>NAME: {student.full_name}</h3>
            <h3>ROLL_NO: {student.roll_number}</h3>
            <h3>CLASS: {student.class_name}</h3>
            <div>
            <button type="button" className="view-student-btn" data-id={student.student_id} data-class_name={student.class_name} onClick={()=>onViewDetails(student)}>
                VIEW PROFILE
            </button>
            </div>
            <button type="button" className="view-marksheet-btn" data-id={student.student_id} data-class_name={student.class_name} onClick={()=>onViewMarksheet(student)}>
                VIEW MARKSHEET
            </button>
        </div>       
    )
}
export default StudentCard
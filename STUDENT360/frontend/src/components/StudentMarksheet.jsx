
function StudentMarksheet({ totalMarks, subMarks, stats, subs, onClose }) {

    if (!subMarks) {
        return null;
    }

    return (
        <div className="marksheet-modal-overlay active" id="marksheet-modal">

            <div className="marksheet-modal">

                <h2>STUDENT MARKSHEET</h2>

                <div id="marksheet-modal-container">

                    {/* PERSONAL STATISTICS */}
                    <div className="personal-stats">

                        <p>
                            TOTAL PERCENTAGE: {stats?.total_percentage ?? "N/A"}
                        </p>

                        <p>
                            OVERALL RANK: {stats?.overall_rank ?? "N/A"}
                        </p>

                        <p>
                            CLASS RANK: {stats?.class_rank ?? "N/A"}
                        </p>

                    </div>


                    {/* SUBJECT-WISE TOTAL MARKS */}
                    <h3>SUBJECT-WISE TOTAL MARKS</h3>

                    <table className="marks-table">

                        <thead>
                            <tr>
                                <th>SUBJECT ID</th>
                                <th>SUBJECT</th>
                                <th>PERCENTAGE</th>
                            </tr>
                        </thead>

                        <tbody>
                            {Object.values(subMarks).map(function(mark, index) {
                                return (
                                    <tr key={mark.subject_id ?? index}>
                                        <td>{mark.subject_id}</td>
                                        <td>{mark.subject}</td>
                                        <td>{mark.subject_percentage}</td>
                                    </tr>
                                );
                            })}
                        </tbody>

                    </table>


                    {/* ASSESSMENT-WISE MARKS */}
                    <h3>ASSESSMENT-WISE MARKS</h3>

                    {subs.map(function(subject) {

                        return (
                            <div className="subject-assessments" key={subject}>

                                <h3>{subject}</h3>

                                <table className="marks-table">

                                    <thead>
                                        <tr>
                                            <th>ASSESSMENT NAME</th>
                                            <th>MARKS OBTAINED</th>
                                            <th>MAX MARKS</th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {(totalMarks?.[subject] || []).map(function(mark, index) {

                                            return (
                                                <tr key={index}>
                                                    <td>{mark.assessment_name}</td>
                                                    <td>{mark.marks_obtained}</td>
                                                    <td>{mark.max_marks}</td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>

                                </table>

                            </div>
                        );
                    })}

                </div>

                <button
                    type="button"
                    className="close-modal"
                    id="marksheet-modal-close-btn"
                    onClick={onClose}
                >
                    CLOSE
                </button>

            </div>
        </div>
    );
}

export default StudentMarksheet;

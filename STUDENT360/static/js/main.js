/*  SECTIONS */
const profileSection = document.querySelector('#students-page');
const analyticsSection = document.querySelector('#analytics-page');

/* Main nav options */
const profileButton = document.querySelector('#student-profile');
const analyticsButton = document.querySelector('#analytics');
const navButtons = document.querySelectorAll('.nav-opt');

const submitClassbtn = document.querySelector("#search-filters");
const clrClassbtn = document.querySelector("#clear-filters");

/* STUDENTS PAGE */
const search = document.querySelector('#profile-search');
const class_name = document.querySelector('#class_name');
const studentProfileContainer = document.querySelector('#profile-container');

if(class_name.value === ""){
    studentProfileContainer.innerHTML = "SELECT A CLASS OR SEARCH ";
}

/* STUDENT DETAILS MODAL */
const studentDetailsModal = document.querySelector('#student-modal');
const closeDetailsModal = document.querySelector('#modal-close-btn');

/* MARKSHEET DETAILS MODAL */
const studentMarksheetModal = document.querySelector('#marksheet-modal');
const closeMarksheetModal = document.querySelector('#marksheet-modal-close-btn');


/* ANALYTICS PAGE */
const classbtn = document.querySelectorAll('.class-btn');
const class12Nav = document.querySelector('#class-12');
const class11Nav = document.querySelector('#class-11');
const class10Nav = document.querySelector('#class-10');
const class9Nav = document.querySelector('#class-9');
const class8Nav = document.querySelector('#class-8');
const class7Nav = document.querySelector('#class-7');
const class6Nav = document.querySelector('#class-6');

const classOptions = document.querySelectorAll('.opt');
const class12options = document.querySelector("#cl12");
const class11options = document.querySelector('#cl11');
const class10options = document.querySelector('#cl10');
const class9options = document.querySelector('#cl9');
const class8options = document.querySelector('#cl8');
const class7options = document.querySelector('#cl7');
const class6options = document.querySelector('#cl6');

/* BUTTONS FOR DISPLAYING ANALAYTICS OF EACH CLASS */
const btnAnalayticsSpecific = document.querySelectorAll('.classes');
const btnAnalayticsOverall = document.querySelectorAll('.overall');

function showAnalyticsOptions(section){
    classOptions.forEach(function(opt){
        opt.classList.remove("active");
    })
    section.classList.add("active");

}

function showClassBtnClicked (btn){
    classbtn.forEach(function(btn){
        btn.classList.remove("active");
    })
    btn.classList.add("active");
}

/* ANALYTICS SECTION ANALYTICS CONTAINER  */
const overallContainer = document.querySelector('#overall');
const subWiseContainer = document.querySelector('#subWise');

/* ANALYTICS SECTION STUDENTS CONTAINER  */
const rankedListContainer = document.querySelector('#student-list');

analyticsSection.addEventListener('click',async function(event){
    if(event.target === class12Nav){
        showAnalyticsOptions(class12options);
        showClassBtnClicked(class12Nav);

    }
    if(event.target === class11Nav){
        showAnalyticsOptions(class11options);
        showClassBtnClicked(class11Nav);        
    }
    if(event.target === class10Nav){
        showAnalyticsOptions(class10options);
        showClassBtnClicked(class10Nav);        
    }
    if(event.target === class9Nav){
        showAnalyticsOptions(class9options);
        showClassBtnClicked(class9Nav);        
    }
    if(event.target === class8Nav){
        showAnalyticsOptions(class8options);
        showClassBtnClicked(class8Nav);        
    }
    if(event.target === class7Nav){
        showAnalyticsOptions(class7options);
        showClassBtnClicked(class7Nav);        
    }
    if(event.target === class6Nav){
        showAnalyticsOptions(class6options);
        showClassBtnClicked(class6Nav);        
    }
    if(event.target.classList.contains("overall")){
        const class_id = event.target.dataset.id
        try{
            const response = await fetch(`/api/analytics/ClassOverall`,{
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "assessment_class" : class_id
                })

            });
            const data = await response.json();
            if(!response.ok){
                throw new Error(data.error || `${response.status}`);
            }
            if(data.status === "success"){
                render_analytics(data.ranked_list,data.overall,data.subData);

                btnAnalayticsSpecific.forEach(function(btn) {
                    btn.classList.remove("active");
                });
                btnAnalayticsOverall.forEach(function(btn){
                    btn.classList.remove("active");
                });                
                btnAnalayticsOverall.forEach(function(btn){
                    if(btn === event.target){
                        event.target.classList.add("active");
                    }
                });                
            }
            else{
                return;
            }
        }
        catch(error){
            console.log("ERROR: ",error);
        }

    }
    if(event.target.classList.contains("classes")){
        const class_id = event.target.dataset.id;
        const assessment_class = event.target.dataset.grade;
        
        try{
            const response = await fetch(`/api/analytics/SectionSpecific`,{
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "assessment_class" : assessment_class,
                    "class_name" : class_id
                })

            });
            const data = await response.json();
            if(!response.ok){
                throw new Error(data.error || `${response.status}`);
            }
            if(data.status === "success"){
                render_analytics(data.ranked_list,data.overall,data.subData);

                btnAnalayticsOverall.forEach(function(btn) {
                    btn.classList.remove("active");
                });                

                btnAnalayticsSpecific.forEach(function(btn){
                    btn.classList.remove("active");
                });                
                btnAnalayticsSpecific.forEach(function(btn){
                    if(btn === event.target){
                        event.target.classList.add("active");
                    }
                });
            }
            else{
                return;
            }
            

        }
        catch(error){
            console.log("ERROR: ",error);
        }

    }                         
})

function render_analytics(ranked_list,overall,subData){
    overallContainer.innerHTML = "";
    overallContainer.innerHTML = `
        <h2>OVERALL MARKS ANALYTICS: </h2>
        <p>HIGHEST : ${escapeHTML(overall.max_percent)}</p>
        <p>LOWEST : ${escapeHTML(overall.min_percent)}</p>
        <p>AVERAGE : ${escapeHTML(overall.avg_percent)}</p>
    `;
    subWiseContainer.innerHTML = "";
    subWiseContainer.innerHTML += `<h2>SUBJECT WISE MARKS ANALYSIS</h2>`
    Object.entries(subData).forEach(function([subject, data]){
        subWiseContainer.innerHTML += `
            <h2>${escapeHTML(subject)}</h2>
            <p>HIGHEST : ${escapeHTML(data.max_percent)}</p>
            <p>LOWEST : ${escapeHTML(data.min_percent)}</p>
            <p>AVERAGE : ${escapeHTML(data.avg_percent)}</p>            
        `
    });
    rankedListContainer.innerHTML = "";
    ranked_list.forEach(function(ranked){
        rankedListContainer.innerHTML += `
            <div>
                <p>${escapeHTML(ranked.full_name)} - ${escapeHTML(ranked.total_percentage)} RANK: ${escapeHTML(ranked.rank)}</p>
            </div>
        `;

    });
}

/* NAV THROUGH SECTIONS */
function showSection(section){
    if (section === profileSection){
        analyticsSection.classList.remove("active");
        profileSection.classList.add("active");
    }
    else if (section === analyticsSection){
        profileSection.classList.remove("active");
        analyticsSection.classList.add("active");
    }
}

function showNavBtnClicked (navBtn){
    navButtons.forEach(function(btn){
        btn.classList.remove("active");
    })
    navBtn.classList.add("active");
}


function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, function(char) {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[char];
    });
}

async function load_students() {
    const c_name = class_name.value.trim();
    const search_value = search.value.trim();
    const params = new URLSearchParams();

    if(c_name){
        params.set("class_name",c_name);
        studentProfileContainer.innerHTML = "Loading.......";
    }
    if(search_value){
        params.set("search",search_value);
    }
    else if (! c_name && !search_value){
        studentProfileContainer.innerHTML = "SELECT A CLASS OR SEARCH ";
        return;
    }
    try{
        const response = await fetch(`/api/students?${params.toString()}`);
        const data = await response.json();
        if(!response.ok){
            throw new Error(data.error || `HTTP ERROR: ${response.status}`);
        }
        const students = data.students;
        if(students.length === 0){
            studentProfileContainer.innerHTML = "NO STUDENT RECORDS AVAILABLE";
            return;
        }
        render_profile(students);  
    }
    catch(error){
        console.log("ERROR: ",error);
        studentProfileContainer.innerHTML = "ERROR, TRY AGAIN LATER!!";

    }
  
}

function render_profile(students){
    studentProfileContainer.innerHTML = "";
    students.forEach(function(student){
        const card = document.createElement('div');
        card.className = "student-profileCard";
        card.id = student.student_id;

        const name = document.createElement('h3');
        name.textContent = `Name : ${student.full_name}`;

        const rollNO = document.createElement('h3');
        rollNO.textContent = `ROLL NO : ${student.roll_number}`;

        const classdetails = document.createElement('h3');
        classdetails.textContent = `CLASS : ${student.class_name}`;        


        const profileButton = document.createElement('button');
        profileButton.textContent = `VIEW STUDENT DETAILS`;
        profileButton.className = "view-student-btn";
        profileButton.dataset.id = student.student_id;
        profileButton.dataset.class_name = student.class_name;
        
        const marksheetButton = document.createElement('button');
        marksheetButton.textContent = `VIEW MARKSHEET`;
        marksheetButton.className = "view-marksheet-btn";
        marksheetButton.dataset.id = student.student_id;
        marksheetButton.dataset.class_name = student.class_name;

        card.append(name,rollNO,classdetails,profileButton,marksheetButton);
        studentProfileContainer.appendChild(card);
    });
}

/* EVENT DELEGATION */
document.addEventListener('click',async function(event){
    if(event.target === profileButton){
        showSection(profileSection);
        showNavBtnClicked(profileButton);

    }
    if(event.target === analyticsButton){
        showSection(analyticsSection);
        showNavBtnClicked(analyticsButton);

    }
    if(event.target === submitClassbtn){
        await load_students();
    }
    if(event.target === clrClassbtn){
        class_name.value = "";
        search.value = "";
        await load_students();
        studentProfileContainer.innerHTML = "SELECT A CLASS OR SEARCH ";

    }
    if(event.target.classList.contains('view-student-btn')){
        const student_id = Number(event.target.dataset.id);
        const c_name = event.target.dataset.class_name;

        try{
            const response = await fetch(`/api/studentDetails`,{
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "student_id" : student_id,
                    "class_name" : c_name
                })

            });
            const data = await response.json();
            if(!response.ok){
                throw new Error(data.error || `${response.status}`);
            }
            if(data.status === "success"){
                render_details_modal(data.student_details);
            }
            else{
                return;
            }
            

        }
        catch(error){
            console.log("ERROR: ",error);
        }
    }
    if(event.target === closeDetailsModal){
        studentDetailsModal.classList.remove("active");
        const container = document.querySelector("#student-modal-container");
        container.innerHTML = "";        
    }

    if(event.target.classList.contains('view-marksheet-btn')){
        const student_id = Number(event.target.dataset.id);
        const c_name = event.target.dataset.class_name;

        try{
            const response = await fetch(`/api/studentMarksheet`,{
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "student_id" : student_id,
                    "class_name" : c_name
                })

            });
            const data = await response.json();
            if(!response.ok){
                throw new Error(data.error || `${response.status}`);
            }
            if(data.status === "success"){
                render_marksheet_modal(data.totalMarks,data.subMarks,data.stats,data.subs);
            }
            else{
                return;
            }
            

        }
        catch(error){
            console.log("ERROR: ",error);
        }
    }
    if(event.target === closeMarksheetModal){
        studentMarksheetModal.classList.remove("active");
        const container = document.querySelector("#marksheet-modal-container");
        container.innerHTML = "";        
    }                
})

function render_details_modal(student_details) {

    const container = document.querySelector("#student-modal-container");

    const dob = student_details.dob
        ? new Date(student_details.dob).toLocaleDateString("en-GB")
        : "N/A";

    container.innerHTML = `
        <h2>STUDENT DETAILS</h2>

        <p>EMAIL: ${escapeHTML(student_details.email)}</p>
        <p>PHONE NO: ${escapeHTML(student_details.phone_no)}</p>
        <p>DOB: ${escapeHTML(dob)}</p>

        <p>SUBJECTS:</p>

        <ul class="list-container">
            <li>${escapeHTML(student_details.sub1)}</li>
            <li>${escapeHTML(student_details.sub2)}</li>
            <li>${escapeHTML(student_details.sub3)}</li>
            <li>${escapeHTML(student_details.sub4)}</li>
            <li>${escapeHTML(student_details.sub5)}</li>
        </ul>
    `;

    studentDetailsModal.classList.add("active");
}



function render_marksheet_modal(totalMarks, subMarks, stats, subs) {

    const container = document.querySelector("#marksheet-modal-container");

    // 1. SUBJECT-WISE TOTAL MARKS TABLE
    let tbody = "";

    Object.values(subMarks).forEach(function(mark) {
        tbody += `
            <tr>
                <td>${escapeHTML(mark.subject_id)}</td>
                <td>${escapeHTML(mark.subject)}</td>
                <td>${escapeHTML(mark.subject_percentage)}</td>
            </tr>
        `;
    });

    const marksTable = `
        <table class="marks-table">
            <thead>
                <tr>
                    <th>SUBJECT ID</th>
                    <th>SUBJECT</th>
                    <th>PERCENTAGE</th>
                </tr>
            </thead>
            <tbody>
                ${tbody}
            </tbody>
        </table>
    `;


    // 2. ASSESSMENT TABLES FOR ALL SUBJECTS
    let assessmentTables = "";

    subs.forEach(function(subject) {

        let body = "";

        const assessments = totalMarks[subject] || [];

        assessments.forEach(function(mark) {
            body += `
                <tr>
                    <td>${escapeHTML(mark.assessment_name)}</td>
                    <td>${escapeHTML(mark.marks_obtained)}</td>
                    <td>${escapeHTML(mark.max_marks)}</td>
                </tr>
            `;
        });

        assessmentTables += `
            <div class="subject-assessments">

                <h3>${escapeHTML(subject)}</h3>

                <table class="marks-table">
                    <thead>
                        <tr>
                            <th>ASSESSMENT NAME</th>
                            <th>MARKS OBTAINED</th>
                            <th>MAX MARKS</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${body}
                    </tbody>
                </table>

            </div>
        `;
    });


    // 3. COMPLETE MODAL HTML
    container.innerHTML = `
        <div class="personal-stats">
            <p>TOTAL PERCENTAGE: ${escapeHTML(stats?.total_percentage ?? "N/A")}</p>
            <p>OVERALL RANK: ${escapeHTML(stats?.overall_rank ?? "N/A")}</p>
            <p>CLASS RANK: ${escapeHTML(stats?.class_rank ?? "N/A")}</p>
        </div>

        <h3>SUBJECT-WISE TOTAL MARKS</h3>
        ${marksTable}

        <h3>ASSESSMENT-WISE MARKS</h3>
        ${assessmentTables}
    `;

    // 4. OPEN MODAL
    document.querySelector("#marksheet-modal").classList.add("active");
}



/* FLASH MESSAGES */

const flashMessages = document.querySelectorAll(".flash-message");

flashMessages.forEach((message) => {

    let duration = 4000;

    if (message.classList.contains("success")) {
        duration = 3000;

    } else if (message.classList.contains("error")) {
        duration = 6000;
    }


    setTimeout(() => {

        message.classList.add("hide");

        setTimeout(() => {
            message.remove();
        }, 500);

    }, duration);

});


const closeButtons = document.querySelectorAll(".flash-close");

closeButtons.forEach((button) => {

    button.addEventListener("click", () => {

        const message = button.parentElement;

        message.classList.add("hide");

        setTimeout(() => {
            message.remove();
        }, 500);

    });

});


const dashboardSection = document.querySelector('#dashboard-section');
const readingSection = document.querySelector('#reading-section');
const alertsSection = document.querySelector('#alerts-section');
const quickCheckSection = document.querySelector('#quickCheck-section');


const pageSections = document.querySelectorAll('.pagesection')


/* Main nav options */
const dashboardNavButton = document.querySelector('#dashboard-button');
const readingsNavButton = document.querySelector('#reading-button');
const alertsNavButton = document.querySelector('#alerts-button');
const quickCheckNavButton = document.querySelector('#quickCheck-button');

const navButtons = document.querySelectorAll('.navButtons');
/* MODALS */

const modal = document.querySelector('#facility-dashboard');
const closeModal = document.querySelector('#close-modal');

/* reading Container */

const readingContainer = document.querySelector('#readings-container');

/* ALERTS CONTAINER */

const alertsContainer = document.querySelector('#alerts-container');
function escapeHTML(value){
    let text = String(value ?? "");
    text = text.replaceAll('&','&amp;');
    text = text.replaceAll('<','&lt;');
    text = text.replaceAll('>','&gt;');
    text = text.replaceAll('"','&quot;');
    text = text.replaceAll("'",'&#39;');
    return text
}
/* QUICK CHECK SECTION */

const quickcheckCode = document.querySelector("#quickcheck-code");
const quickcheckBreach = document.querySelector("#quickcheck-breach");
const quickcheckSearch = document.querySelector("#quickcheck-search");

const quickcheckResults = document.querySelector("#quickcheck-results");
const quickcheckMessage = document.querySelector("#quickcheck-message");

const quickcheckPagination = document.querySelector("#quickcheck-pagination");
const quickcheckPrev = document.querySelector("#quickcheck-prev");
const quickcheckNext = document.querySelector("#quickcheck-next");
const quickcheckPageInfo = document.querySelector("#quickcheck-page-info");

let quickcheckCurrentPage = 1;


// Fetch readings from DRF
async function fetchQuickCheck(page = 1) {

    const sensorCode = quickcheckCode.value.trim();
    const breach = quickcheckBreach.value;

    const params = new URLSearchParams();

    if (sensorCode) {
        params.set("sensor_code", sensorCode);
    }

    if (breach !== "all") {
        params.set("is_breach", breach);
    }

    params.set("page", page);

    quickcheckMessage.textContent = "Loading readings...";
    quickcheckPagination.hidden = true;

    try {

        const response = await fetch(
            `/api/v1/readings/?${params.toString()}`
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        quickcheckCurrentPage = page;

        renderQuickCheck(data);

    } catch (error) {

        quickcheckResults.innerHTML = "";
        quickcheckMessage.textContent = "Unable to load readings.";

        console.error(error);
    }
}


//  Display readings in the table
function renderQuickCheck(data) {

    quickcheckResults.innerHTML = "";

    if (data.results.length === 0) {

        quickcheckMessage.textContent = "No readings found.";
        return;
    }

    quickcheckMessage.textContent =
        `${data.count} matching readings found`;

    const table = document.createElement("table");
    table.className = "readings-table";

    table.innerHTML = `
        <thead>
            <tr>
                <th>SENSOR CODE</th>
                <th>VALUE</th>
                <th>BREACH STATUS</th>
                <th>RECORDED AT</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;

    const tbody = table.querySelector("tbody");

    data.results.forEach(function(reading) {

        const row = document.createElement("tr");

        row.className = reading.is_breach
            ? "alert-row"
            : "normal-row";

        const cells = [
            reading.sensor_code,
            reading.value,
            reading.is_breach ? "BREACH" : "NORMAL",
            new Date(reading.recorded_at).toLocaleString("en-IN")
        ];

        cells.forEach(function(value) {

            const td = document.createElement("td");
            td.textContent = value;
            row.appendChild(td);

        });

        tbody.appendChild(row);
    });

    const wrapper = document.createElement("div");
    wrapper.className = "readings-table-wrapper";

    wrapper.appendChild(table);
    quickcheckResults.appendChild(wrapper);

    // Pagination
    quickcheckPagination.hidden = false;

    quickcheckPageInfo.textContent =
        `Page ${quickcheckCurrentPage} of ${Math.ceil(data.count / 10)}`;

    quickcheckPrev.disabled = !data.previous;
    quickcheckNext.disabled = !data.next;
}



quickcheckSearch?.addEventListener("click", function() {

    fetchQuickCheck(1);
});


quickcheckPrev?.addEventListener("click", function() {

    fetchQuickCheck(quickcheckCurrentPage - 1);
});


quickcheckNext?.addEventListener("click", function() {

    fetchQuickCheck(quickcheckCurrentPage + 1);
});


/* DASHBOARD */

function render_stats(data) {

    const statsContainer = document.querySelector("#stats-container");
    const machinesContainer = document.querySelector("#machines-container");
    const remarksContainer = document.querySelector("#remarks");

    // Clear previous facility results
    statsContainer.innerHTML = "";
    machinesContainer.innerHTML = "";
    remarksContainer.innerHTML = "";
    // Machine count card
    statsContainer.innerHTML += `
        <div class="stat-card">
            <h3>TOTAL MACHINES</h3>
            <h2>${data.machine_count}</h2>
        </div>
    `;

    // Sensor count card
    statsContainer.innerHTML += `
        <div class="stat-card">
            <h3>TOTAL SENSORS</h3>
            <h2>${data.sensor_count}</h2>
        </div>
    `;

    // Sensor type cards
    data.sensors.forEach(function(sensor) {
        statsContainer.innerHTML += `
            <div class="stat-card">
                <h3>${escapeHTML(sensor.sensor_type)} SENSORS</h3>
                <h2>${sensor.total}</h2>
            </div>
        `;
    });

    // Machine cards
    if (data.machines.length === 0) {
        machinesContainer.innerHTML =
            `<p>No machines found for this facility.</p>`;
    }

    data.machines.forEach(function(machine) {

        const lastDate = machine.last_maintenance
            ? new Date(machine.last_maintenance).toLocaleDateString("en-GB")
            : "N/A";

        const nextDate = machine.next_maintenance
            ? new Date(machine.next_maintenance).toLocaleDateString("en-GB")
            : "N/A";

        const status = String(machine.status ?? "").toLowerCase();

        machinesContainer.innerHTML += `
            <div class="machine-container">

                <div class="machine-card-header">
                    <div>
                        <h3>${escapeHTML(machine.asset_tag)}</h3>
                        <p>${escapeHTML(machine.name)}</p>
                    </div>

                    <span class="status-badge ${escapeHTML(status)}">
                        ${escapeHTML(machine.status)}
                    </span>
                </div>

                <div class="machine-details">
                    <p>
                        <strong>TYPE:</strong>
                        ${escapeHTML(machine.machine_type)}
                    </p>
                    <p>
                        <strong>MANUFACTURER:</strong>
                        ${escapeHTML(machine.manufacturer)}
                    </p>
                    <p>
                        <strong>LOCATION:</strong>
                        ${escapeHTML(machine.plant_location)}
                    </p>                    

                    <p>
                        <strong>MODEL NUMBER:</strong>
                        ${escapeHTML(machine.model_number)}
                    </p>
                    <p>
                        <strong>SERIAL NUMBER:</strong>
                        ${escapeHTML(machine.serial_number)}
                    </p>                        


                    <p>
                        <strong>LAST MAINTENANCE:</strong>
                        ${escapeHTML(lastDate)}
                    </p>

                    <p>
                        <strong>NEXT MAINTENANCE:</strong>
                        ${escapeHTML(nextDate)}
                    </p>
                </div>
                    <div class="remarks">
                        <h4>REMARKS</h4>

                        <p class="remarks-text">
                            ${escapeHTML(machine.remarks || "NO REMARKS")}
                        </p>

                        <div class="remarks-buttons">
                            <button type="button"
                                    class="edit-remarks"
                                    data-id="${machine.id}">
                                EDIT
                            </button>
                        </div>
                    </div>
            </div>
        `;


    });

    modal.classList.add("active");
}

/* READINGS */

function renderReadings(sensor_readings) {

    readingContainer.innerHTML = "";

    sensor_readings.forEach(function(item) {

        let card = `
            <div class="sensor-card">

                <div class="machine-details">
                    <p>MACHINE NAME: ${escapeHTML(item.machine__name)}</p>
                    <p>MACHINE TYPE: ${escapeHTML(item.machine__machine_type)}</p>
                    <p>ASSET TAG: ${escapeHTML(item.machine__asset_tag)}</p>
                    <p>CRITICALITY: ${escapeHTML(item.machine__criticality)}</p>
                    <p>STATUS: ${escapeHTML(item.machine__status)}</p>
                </div>

                <div class="sensor-details">
                    <p>SENSOR CODE: ${escapeHTML(item.code)}</p>
                    <p>SENSOR TYPE: ${escapeHTML(item.sensor_type)}</p>
                    <p>MIN THRESHOLD: ${escapeHTML(item.min_threshold ?? "N/A")}</p>
                    <p>MAX THRESHOLD: ${escapeHTML(item.max_threshold ?? "N/A")}</p>
                    <p>UNIT: ${escapeHTML(item.unit)}</p>
                </div>
        `;

        let tbody = "";

        item.readings.forEach(function(reading) {

            // Determine row color individually
            const classColorCode = reading.is_breach
                ? "alert-row"
                : "normal-row";

            // Format recorded time
            const recorded = new Date(
                reading.recorded_at
            ).toLocaleString("en-IN", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: false
            });

            // Format received time
            const received = new Date(
                reading.received_at
            ).toLocaleString("en-IN", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: false
            });

            tbody += `
                <tr class="${classColorCode}">
                    <td>${escapeHTML(reading.value)} ${escapeHTML(item.unit)}</td>
                    <td>${escapeHTML(recorded)}</td>
                    <td>${escapeHTML(received)}</td>
                </tr>
            `;
        });

        if (item.readings.length === 0) {
            tbody = `
                <tr>
                    <td colspan="3">No readings available</td>
                </tr>
            `;
        }

        const readingsTable = `
            <div class="readings-table-wrapper">
                <table class="readings-table">
                    <thead>
                        <tr>
                            <th>READING</th>
                            <th>RECORDED AT</th>
                            <th>RECEIVED AT</th>
                        </tr>
                    </thead>

                    <tbody>
                        ${tbody}
                    </tbody>
                </table>
            </div>
        `;

        card += readingsTable;
        card += `</div>`;

        readingContainer.insertAdjacentHTML(
            "beforeend",
            card
        );
    });
}
/*RENDERING ALERTS */
function render_alerts(sensor_alerts){
    alertsContainer.innerHTML = "";
    let tbody = "";
    sensor_alerts.forEach(function(alert){
        let created ;
        let acknowledged_at;
        let resolved_at;
        if (alert.created_at){
            created= new Date(alert.created_at).toLocaleString("en-IN", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: false
            });
        }
        else{
            created = "";
        }
        if (alert.acknowledged_at){
            acknowledged_at= new Date(alert.acknowledged_at).toLocaleString("en-IN", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: false
            });
        }
        else{
            acknowledged_at = "";
        }
        if (alert.resolved_at){
            resolved_at= new Date(alert.resolved_at).toLocaleString("en-IN", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: false
            });
        }
        else{
            resolved_at = "";
        }
           
        tbody += `
            <tr>
                <td>${escapeHTML(alert.sensor__machine__asset_tag)}</td>
                <td>${escapeHTML(alert.sensor__machine__machine_type)}</td>
                <td>${escapeHTML(alert.sensor__machine__status)}</td>
                <td>${escapeHTML(alert.sensor__machine__name)}</td>
                <td>${escapeHTML(alert.sensor__machine__criticality)}</td>
                <td>${escapeHTML(alert.sensor__code)}</td>
                <td>${escapeHTML(alert.sensor__sensor_type)}</td>
                <td>${escapeHTML(alert.sensor__unit)}</td>
                <td>${escapeHTML(alert.sensor__min_threshold)}</td>
                <td>${escapeHTML(alert.sensor__max_threshold)}</td>
                <td>${escapeHTML(alert.reading_value)}</td> 
                <td>${escapeHTML(alert.occurrence_count)}</td>                               
                <td>${escapeHTML(alert.alert_type)}</td>
                <td>${escapeHTML(alert.severity)}</td>
                <td>${escapeHTML(alert.status)}</td>
                <td>${escapeHTML(alert.message)}</td>
                <td>${escapeHTML(created)}</td>
                <td>${escapeHTML(acknowledged_at)}</td>
                <td>${escapeHTML(alert.acknowledged_by)}</td>
                <td>${escapeHTML(resolved_at)}</td>
                <td>${escapeHTML(alert.resolution_note)}</td>
                <td><button class="edit-alerts" data-sensorid=${alert.sensor_id} data-readingid=${alert.reading_id} data-alertid=${alert.id}>EDIT</button></td>
            </tr>          
        `
    })

    const alertsTable = `
        <div class="alerts-table-wrapper">
            <table class="alerts-table">
                <thead>
                    <tr>
                        <th>ASSET TAG</th>
                        <th>MACHINE TYPE</th>
                        <th>MACHINE STATUS</th>
                        <th>MACHINE NAME</th>
                        <th>MACHINE CRITICALITY</th>
                        <th>CODE</th>
                        <th>SENSOR TYPE</th>
                        <th>UNIT</th>
                        <th>MIN THRESHOLD</th>
                        <th>MAX THRESHOLD</th>
                        <th>VALUE</th>
                        <th>OCCURRENCE COUNT</th>
                        <th>ALERT TYPE</th>
                        <th>SEVERITY</th>
                        <th>STATUS</th>
                        <th>MESSAGE</th>
                        <th>CREATED AT</th>
                        <th>ACKNOWLEDGED AT</th>
                        <th>ACKNOWLEDGED BY</th>
                        <th>RESOLVED AT</th>
                        <th>RESOLUTION NOTE</th>
                        <th>EDIT</th>
                    </tr>
                </thead>
                <tbody>
                    ${tbody}
                </tbody>
            </table>
        </div>
    `;
    alertsContainer.innerHTML = alertsTable;
}

/* flash messages */
document.querySelectorAll(".flash-message").forEach(message => {
    const duration = message.classList.contains("error")
        ? 6000
        : 3000;

    setTimeout(() => {
        message.classList.add("hide");

        setTimeout(() => message.remove(), 500);
    }, duration);
});

document.querySelectorAll(".flash-close").forEach(button => {
    button.addEventListener("click", () => {
        const message = button.closest(".flash-message");
        if (message) message.remove();
    });
});

/* SECTION NAVIGATION. */
function showSection(section) {

    pageSections.forEach(function(pagesection) {

        pagesection.classList.remove("active");

    });

    section.classList.add("active");
}


function showNavBtnClicked(buttonClicked) {
    navButtons.forEach(function(navButton) {

        navButton.classList.remove("clicked");

    });

    buttonClicked.classList.add("clicked");
}

/* EVENT DELEGATION */
document.addEventListener('click',async function(event){
    if(event.target === dashboardNavButton){
        showSection(dashboardSection);
        showNavBtnClicked(dashboardNavButton);

    }
    if(event.target === readingsNavButton){
        showSection(readingSection);
        showNavBtnClicked(readingsNavButton);

    }    
    if(event.target === alertsNavButton){
        showSection(alertsSection);
        showNavBtnClicked(alertsNavButton);

    }
    if(event.target === quickCheckNavButton){
        showSection(quickCheckSection);
        showNavBtnClicked(quickCheckNavButton);

    }    
    if(event.target.classList.contains("view-stats")){
        const facility_id = Number(event.target.dataset.id);

        const csrfToken = document.querySelector('#csrf-form input[name="csrfmiddlewaretoken"]').value;
        try {
            const response = await fetch("/api/dashboard/", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },

                body: JSON.stringify({
                    facility_id: facility_id
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || `HTTP ERROR: ${response.status}`
                );
            }

    
            render_stats(data);

        } catch (error) {
            console.error("ERROR:", error);
        }
    }
    if(event.target === closeModal){
        modal.classList.remove("active");
    }
    if(event.target.classList.contains("view-reading")){
        const facility_id = Number(event.target.dataset.id);

        const csrfToken = document.querySelector('#csrf-form input[name="csrfmiddlewaretoken"]').value;
        try {
            const response = await fetch("/api/readings/", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },

                body: JSON.stringify({
                    facility_id: facility_id
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || `HTTP ERROR: ${response.status}`
                );
            }
            if(data.status === "NIL"){
                readingContainer.innerHTML = " NO READINGS OBTAINED";
            }
            else if(data.status === "success"){
                renderReadings(data.sensor_readings);
            }

        } catch (error) {
            console.error("ERROR:", error);
        }
    } 
    if(event.target.classList.contains("view-alerts")){
        const facility_id = Number(event.target.dataset.id);

        const csrfToken = document.querySelector('#csrf-form input[name="csrfmiddlewaretoken"]').value;
        try {
            const response = await fetch("/api/alerts/", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },

                body: JSON.stringify({
                    facility_id: facility_id
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || `HTTP ERROR: ${response.status}`
                );
            }
            if(data.status === "NIL"){
                alertsContainer.innerHTML = " NO ALERTS OBTAINED";
            }
            else if(data.status === "success"){
                render_alerts(data.sensor_alerts);
            }

        } catch (error) {
            console.error("ERROR:", error);
        }
    }
    if (event.target.classList.contains("edit-remarks")) {

        const machineId = event.target.dataset.id;

        window.location.href = `/machines/${machineId}/edit/`;
    }
    if (event.target.classList.contains("edit-alerts")) {

        const alertid = event.target.dataset.alertid;

        window.location.href = `/alerts/${alertid}/edit/`;
    }          
})

modal?.addEventListener("click", function(event) {
    if (event.target === modal) {
        modal.classList.remove("active");
    }
});

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        modal?.classList.remove("active");
    }
});
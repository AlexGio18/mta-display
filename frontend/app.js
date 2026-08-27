const API_URL =
    "/api/stations/prospect-park/departures";


async function loadDepartures() {

    const status = document.getElementById("status");
    const statusDot = document.getElementById("status-dot");

    try {

        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data = await response.json();

        renderDepartures(data);

        status.textContent = "Live";
        statusDot.classList.add("connected");

    } catch (error) {

        console.error(
            "Failed to load departures:",
            error
        );

        status.textContent = "Connection error";
        statusDot.classList.remove("connected");
    }
}


function renderDepartures(data) {

    const container =
        document.getElementById("departures");

    const updated =
        document.getElementById("updated");

    updated.textContent =
        formatTime(data.updated_at);


    if (data.departures.length === 0) {

        container.innerHTML = `
            <div class="no-trains">
                No upcoming trains
            </div>
        `;

        return;
    }

    // Group departures by route
    const grouped = {};

    data.departures.forEach(departure => {

        if (!grouped[departure.route]) {
            grouped[departure.route] = [];
        }

        if (grouped[departure.route].length < 5) {
                grouped[departure.route].push(departure);
        }
    });


      // Create a section for each route
    container.innerHTML =
        Object.entries(grouped)
            .map(([route, departures]) => {

                return `
                    <section class="route-group">

                        <div class="route-header">
                            <div class="route ${route}">
                                ${route}
                            </div>
                            <div>
                                ${route} Train
                            </div>
                        </div>

                        <div class="route-departures">

                            ${departures
                                .map(departure => {

                                    return `
                                        <div class="departure">

                                            <div class="train-info">

                                                <div class="destination">
                                                    ${departure.destination}
                                                </div>

                                                <div class="direction">
                                                    ${departure.direction}
                                                </div>

                                            </div>

                                            <div class="arrival">

                                                ${departure.minutes}
                                                <span>min</span>

                                                ${formatDelay(
                                                    departure.delay_minutes
                                                )}

                                            </div>

                                        </div>
                                    `;

                                })
                                .join("")}

                        </div>

                    </section>
                `;

            })
            .join("");
}

function formatDelay(delayMinutes) {

    if (delayMinutes === null ||
        delayMinutes === undefined ||
        delayMinutes === 0) {

        return "";
    }

    if (delayMinutes > 0) {

        return `
            <div class="delay">
                ${delayMinutes} min late
            </div>
        `;
    }

    return "";
}

function formatTime(dateString) {

    const date =
        new Date(dateString);

    return date.toLocaleTimeString(
        [],
        {
            hour: "numeric",
            minute: "2-digit",
            second: "2-digit"
        }
    );
}


function updateClock() {

    const now = new Date();

    document.getElementById("clock")
        .textContent =
        now.toLocaleTimeString(
            [],
            {
                hour: "numeric",
                minute: "2-digit"
            }
        );
}


updateClock();

setInterval(
    updateClock,
    1000
);


loadDepartures();

setInterval(
    loadDepartures,
    30000
);

/* CONTAINERS and navbuttons */

const moviesContainer = document.querySelector('#movie-container');
const tvContainer = document.querySelector('#tv-container');

const trendingMoviesContainer = document.querySelector('#trending-container-movies');
const trendingTVContainer = document.querySelector('#trending-container-tv');

const trendingMoviesButton = document.querySelector('#trending-movies');
const trendingTVButton = document.querySelector('#trending-tv');
const durationSelect = document.querySelector("#duration");

const libraryContainer = document.querySelector('#libraryContainer');
const libraryMoviesContainer = document.querySelector('#library-container-movies');
const libraryTVContainer = document.querySelector('#library-container-tv');

const libraryMoviesButton = document.querySelector('#library-movies');
const libraryTVButton = document.querySelector('#library-tv');


const socialSearchContainer = document.querySelector('#search-section');
const socialRequestsContainer = document.querySelector('#connections-requests');
const notificationsContainer = document.querySelector('#notification-Container');

const socialSearchButton = document.querySelector('#search-users');
const socialRequestsButton = document.querySelector('#view-connection-requests');


const profileContainer = document.querySelector('#profile-container');

const recommendedSentContainer = document.querySelector('#recommendations-sent-container');
const recommendedGetContainer = document.querySelector('#recommendations-received-container');

/* MOVIES */

const loadMoreMovieButton = document.querySelector("#load-more-button-movies");

const searchMovies = document.querySelector("#searchMovie");
const genreMovies = document.querySelectorAll('input[name="genre"]');

const submitMoviesButton = document.querySelector("#sbt-movies");
const clearMoviesButton = document.querySelector("#clr-movies");

let movieFilters = {
    search: "",
    genre: ""
};


/* MODAL */

const modal = document.querySelector("#modal");
const closeModal = document.querySelector("#close-modal");


/* TV */

const loadMoreTVButton = document.querySelector("#load-more-button-tv");
const searchTV = document.querySelector("#searchTV");
const genreTV = document.querySelectorAll('input[name="genreTV"]');

const submitTVButton = document.querySelector("#sbt-tv");
const clearTVButton = document.querySelector("#clr-tv");

let tvFilters = {
    search: "",
    genre: ""
};


/* SOCIAL */
const searchInput = document.querySelector("#search");
const suggestionsBox = document.querySelector("#suggestions");


let debounceTimer;
let controller;

const profileModal = document.querySelector("#profile-modals");
const socialProfileContent = document.querySelector("#social-profile-content");

/* SECTION NAVIGATION */

const movieSectionButton = document.querySelector('#movie-selection');
const tvSectionButton = document.querySelector('#tv-selection');
const trendingSectionButton = document.querySelector('#trending-selection');
const watchlistSectionButton = document.querySelector('#watchlist-selection');
const profileSectionButton = document.querySelector('#profile-selection');
const socialSectionButton = document.querySelector('#social-selection');
const recommendationSectionButton = document.querySelector('#recommendations-selection');





const navButtons = document.querySelectorAll(".navButtons");

const movieSection = document.querySelector('#movies');
const tvSection = document.querySelector('#tv');
const trendingSection = document.querySelector('#trending');
const watchlistSection = document.querySelector('#watchlist');
const profileSection = document.querySelector('#profile');

const socialSection = document.querySelector('#social'); 



const recommendationSection = document.querySelector('#recommendations');

const recommendationSentSectionButton = document.querySelector('#recommend-sent');
const recommendationReceivedSectionButton = document.querySelector('#recommend-receive');

const recommendationSentSection = document.querySelector('#recommendations-sent');
const recommendationReceivedSection = document.querySelector('#recommendations-received');


const pageSections = document.querySelectorAll("main > section");


function showSection(section) {

    pageSections.forEach(function(pagesection) {
        pagesection.classList.remove("active");
    });

    section.classList.add("active");
}


function clicked(buttonClicked) {

    navButtons.forEach(function(navButton) {
        navButton.classList.remove("clicked");
    });

    buttonClicked.classList.add("clicked");
}

function syncLibraryButtons(tmdbId, mediaType, isInLibrary) {

    document.querySelectorAll(".library-button").forEach(button => {

        if (
            Number(button.dataset.id) === Number(tmdbId) &&
            button.dataset.type === mediaType
        ) {
            button.dataset.status = isInLibrary ? "REMOVE" : "ADD";

            button.textContent = isInLibrary
                ? "REMOVE FROM LIBRARY"
                : "ADD TO MY LIBRARY";
        }
    });
}
/* DISCOVER MOVIES SECTION */

let allMovies = [];
let currentMoviePage = 1;
let totalMoviePages = 1;
let isLoading = false;

async function load_movies(reset = false) {

    if (isLoading) return;

    if (reset) {
        allMovies = [];
        currentMoviePage = 1;
        totalMoviePages = 1;
        moviesContainer.innerHTML = "";
    }

    if (currentMoviePage > totalMoviePages) return;

    isLoading = true;
    loadMoreMovieButton.disabled = true;
    loadMoreMovieButton.textContent = "LOADING...";

    try {

        const params = new URLSearchParams({
            page: currentMoviePage,
            search: movieFilters.search,
            genre: movieFilters.genre
        });

        const response = await fetch(`/api/movies?${params.toString()}`);

        if (!response.ok) {
            throw new Error(`HTTP ERROR: ${response.status}`);
        }

        const data = await response.json();

        const newMovies = data.allMovies || [];

        allMovies.push(...newMovies);

        moviesContainer.innerHTML = "";

        if (allMovies.length === 0) {
            moviesContainer.textContent = "NO MOVIES FOUND";
        } else {
            render_data(allMovies, moviesContainer, data.mymovies || []);
        }

        totalMoviePages = Math.min(data.total_pages || 1, 500);
        currentMoviePage++;

    } catch (error) {

        console.error(error);

        if (allMovies.length === 0) {
            moviesContainer.textContent = "UNABLE TO LOAD MOVIES";
        }

    } finally {

        isLoading = false;

        if (currentMoviePage <= totalMoviePages) {
            loadMoreMovieButton.disabled = false;
            loadMoreMovieButton.textContent = "LOAD MORE";
        } else {
            loadMoreMovieButton.disabled = true;
            loadMoreMovieButton.textContent = "NO MORE MOVIES";
        }
    }
}


/* DISCOVER TV SECTION */

let allTV = [];
let currentTVPage = 1;
let totalTVPages = 1;
let isLoadingTV = false;



async function load_tv(reset = false) {

    if (isLoadingTV) return;

    if (reset) {
        allTV = [];
        currentTVPage = 1;
        totalTVPages = 1;
        tvContainer.innerHTML = "";
    }

    if (currentTVPage > totalTVPages) return;

    isLoadingTV = true;
    loadMoreTVButton.disabled = true;
    loadMoreTVButton.textContent = "LOADING...";


    try {

        const params = new URLSearchParams({
            page: currentTVPage,
            searchTV: tvFilters.search,
            genreTV: tvFilters.genre
        });

        const response = await fetch(`/api/TV?${params.toString()}`);        

        if (!response.ok) {
            throw new Error(`HTTP ERROR: ${response.status}`);
        }

        const data = await response.json();
        const mytvs = data.mytvs || [];
        const newTV = data.allTV || [];

        allTV.push(...newTV);

        tvContainer.innerHTML = "";

        render_data(allTV, tvContainer, mytvs);

        totalTVPages = Math.min(data.total_pages || 1, 500);
        currentTVPage++;

    } catch (error) {

        console.error(error);

        if (allTV.length === 0) {
            tvContainer.textContent = "Unable to load tv.";
        }

    } finally {

        isLoadingTV = false;

        if (currentTVPage <= totalTVPages) {
            loadMoreTVButton.disabled = false;
            loadMoreTVButton.textContent = "LOAD MORE";
        } else {
            loadMoreTVButton.disabled = true;
            loadMoreTVButton.textContent = "NO MORE TV";
        }
    }
}


/* TRENDING MOVIES AND TV */

let trendingTV = [];

async function load_Trendingtv() {

    trendingTV = [];
    trendingTVContainer.innerHTML = "";

    const duration = durationSelect.value;

    try {

        const response = await fetch(`/api/trending/tv?duration=${duration}`);

        if (!response.ok) {
            throw new Error(`HTTP ERROR: ${response.status}`);
        }

        const data = await response.json();
        const mytvs = data.mytvs || [];
        const newTV = data.trendingTV || [];

        trendingTV.push(...newTV);

        trendingTVContainer.innerHTML = "";

        render_data(trendingTV, trendingTVContainer, mytvs);

    } catch (error) {

        console.error(error);

        if (trendingTV.length === 0) {
            trendingTVContainer.textContent = "Unable to load.";
        }
    }
}


let trendingMovies = [];

async function load_Trendingmovies() {

    trendingMovies = [];
    trendingMoviesContainer.innerHTML = "";

    const duration = durationSelect.value;

    try {

        const response = await fetch(`/api/trending/movies?duration=${duration}`);

        if (!response.ok) {
            throw new Error(`HTTP ERROR: ${response.status}`);
        }

        const data = await response.json();
        const mymovies = data.mymovies || [];
        const newMovies = data.trendingMovies || [];

        trendingMovies.push(...newMovies);

        trendingMoviesContainer.innerHTML = "";

        render_data(trendingMovies, trendingMoviesContainer, mymovies);

    } catch (error) {

        console.error(error);

        if (trendingMovies.length === 0) {
            trendingMoviesContainer.textContent = "Unable to load.";
        }
    }
}


/* LIBRARY */

let allLibraryMovies = [];
let allLibraryTV = [];

async function load_library(media_type, reset) {

    if (reset) {

        if (media_type === "movie") {
            allLibraryMovies = [];
            libraryMoviesContainer.innerHTML = "";

        } else if (media_type === "tv") {
            allLibraryTV = [];
            libraryTVContainer.innerHTML = "";
        }
    }

    try {

        const response = await fetch(`/api/Library/${media_type}`);

        if (!response.ok) {
            throw new Error(`HTTP ERROR: ${response.status}`);
        }

        const data = await response.json();

        if (media_type === "movie") {

            const fetchMovies = data.libraryMovies || [];

            allLibraryMovies = fetchMovies;
            libraryMoviesContainer.innerHTML = "";

            if (allLibraryMovies.length === 0) {
                libraryMoviesContainer.textContent = "EMPTY !! ADD TO LIBRARY.";
            } else {
                render_librarydata(allLibraryMovies, libraryMoviesContainer, "movie");
            }

        } else if (media_type === "tv") {

            const fetchTV = data.libraryTV || [];

            allLibraryTV = fetchTV;
            libraryTVContainer.innerHTML = "";

            if (allLibraryTV.length === 0) {
                libraryTVContainer.textContent = "EMPTY !! ADD TO LIBRARY.";
            } else {
                render_librarydata(allLibraryTV, libraryTVContainer, "tv");
            }
        }

    } catch (error) {

        console.error(error);

        if (media_type === "movie") {
            libraryMoviesContainer.textContent = "Unable to load.";
        } else if (media_type === "tv") {
            libraryTVContainer.textContent = "Unable to load.";
        }
    }
}


/* RENDER LIBRARY */

function render_librarydata(items, container, media_type) {

    items.forEach(item => {

        const card = document.createElement("div");
        card.className = "card";
        card.id = `myLibrary-${item.tmdb_id}`;

        const title = document.createElement("h3");
        title.textContent = `TITLE: ${item.title}`;

        const poster = document.createElement("img");
        poster.src = item.poster_path;
        poster.loading = "lazy";
        poster.alt = item.title || "Movie poster";

        const releaseDate = document.createElement("h3");
        releaseDate.textContent = `DOR: ${item.release_date || "TBA"}`;

        const libraryButton = document.createElement("button");
        libraryButton.textContent = "REMOVE FROM LIBRARY";
        libraryButton.className = "library-button";

        const viewDetailsButton = document.createElement("button");
        viewDetailsButton.textContent = "VIEW DETAILS";
        viewDetailsButton.className = "view-details";

        libraryButton.dataset.id = item.tmdb_id;
        libraryButton.dataset.type = media_type;
        libraryButton.dataset.status = "REMOVE";

        viewDetailsButton.dataset.id = item.tmdb_id;
        viewDetailsButton.dataset.type = media_type;

        const statusSelect = document.createElement("select");
        statusSelect.className = "watch-status";
        statusSelect.dataset.id = item.tmdb_id;
        statusSelect.dataset.media_type = media_type;

        const statuses = [
            'CURRENTLY WATCHING',
            'DROPPED',
            'FINISHED',
            'WATCHLIST',
            'NEXT WATCH',
            'FAVORITE',
            'IN LIBRARY'
        ];

        statuses.forEach(status => {
            const option = document.createElement("option");
            option.value = status;
            option.textContent = status;
            statusSelect.append(option);
        });



        statusSelect.value = item.status || "IN LIBRARY";
        statusSelect.dataset.current_status = statusSelect.value.trim();

        const recommendButton = document.createElement("button");
        recommendButton.textContent = "RECOMMEND BUTTON";
        recommendButton.dataset.id = item.tmdb_id;
        recommendButton.dataset.media_type = media_type;
        recommendButton.className = "RecommendButton";        

        card.append(
            poster,
            title,
            releaseDate,
            libraryButton,
            viewDetailsButton,
            recommendButton,
            statusSelect
        );

        container.appendChild(card);
    });
}


/* ADD TO LIBRARY */

async function add_to_library(selected, media_type) {

    try {

        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

        const response = await fetch("/api/addToLibrary", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                "tmdb_id": selected.tmdb_id,
                "title": selected.title,
                "release_date": selected.release_date,
                "overview": selected.overview,
                "popularity": selected.popularity,
                "poster_path": selected.poster_path,
                "vote_average": selected.vote_average,
                "vote_count": selected.vote_count,
                "media_type": media_type
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP ERROR: ${response.status}`);
        }

        console.log(`ADDED TO LIBRARY ${selected.tmdb_id}`);

        await load_library("movie", true);
        await load_library("tv", true);

        return true;

    } catch (error) {
        console.error("ERROR", error);
        return false;
    }
}


/* REMOVE FROM LIBRARY */

async function remove_from_library(selected, media_type) {

    try {

        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

        const response = await fetch("/api/removefromLibrary", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                "tmdb_id": selected.tmdb_id,
                "media_type": media_type
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP ERROR: ${response.status}`);
        }

        console.log(`REMOVED FROM LIBRARY ${selected.tmdb_id}`);

        await load_library("movie", true);
        await load_library("tv", true);

        return true;

    } catch (error) {
        console.error("ERROR", error);
        return false;
    }
}


/* RENDER MOVIES AND TV */

function render_data(items, container, myLibrary) {

    items.forEach(item => {

        const card = document.createElement("div");
        card.className = "card";
        card.id = `${item.media_type}-${item.tmdb_id}`;

        const title = document.createElement("h3");
        title.textContent = `TITLE: ${item.title}`;

        const poster = document.createElement("img");
        poster.src = item.poster_path;
        poster.loading = "lazy";
        poster.alt = item.title || "Movie poster";

        const releaseDate = document.createElement("h3");
        releaseDate.textContent = `DOR: ${item.release_date}`;

        const exists = myLibrary.some(myitem =>
            myitem.tmdb_id === item.tmdb_id
        );

        const libraryButton = document.createElement("button");
        libraryButton.textContent = exists
            ? "REMOVE FROM LIBRARY"
            : "ADD TO MY LIBRARY";

        libraryButton.className = "library-button";

        const viewDetailsButton = document.createElement("button");
        viewDetailsButton.textContent = "VIEW DETAILS";
        viewDetailsButton.className = "view-details";

        libraryButton.dataset.id = item.tmdb_id;
        libraryButton.dataset.type = item.media_type;
        libraryButton.dataset.status = exists ? "REMOVE" : "ADD";

        viewDetailsButton.dataset.id = item.tmdb_id;
        viewDetailsButton.dataset.type = item.media_type;

        const recommendButton = document.createElement("button");
        recommendButton.textContent = "RECOMMEND BUTTON";
        recommendButton.dataset.id = item.tmdb_id;
        recommendButton.dataset.media_type = item.media_type;
        recommendButton.className = "RecommendButton";

        card.append(
            poster,
            title,
            releaseDate,
            libraryButton,
            viewDetailsButton,
            recommendButton
        );

        container.appendChild(card);
    });
}
/* GET RECOMMENDED */
let recommended_sent = [];
let recommended_got = [];

async function load_recommended() {
    try{
        const response = await fetch(`/api/getRecommendation`);
        const data = await response.json();
        if(!response.ok){
            throw new Error(data.error || `HTTP ERROR: ${response.status}`);
        }
        recommended_sent = data.sent;
        mymovies = data.mymovies;
        mytvs = data.mytvs;
        recommended_got = data.get;

        render_recommended(recommended_sent,recommended_got,mytvs,mymovies);


    }
    catch(error){
        console.log("Error: ",error)
    }
}

function render_recommended(recommended_sent,recommended_got,mytvs,mymovies){
    recommendedSentContainer.innerHTML = "";
    recommendedGetContainer.innerHTML = "";

    recommended_sent.forEach(item => {

        const card = document.createElement("div");
        card.className = "card";


        const title = document.createElement("h3");
        title.textContent = `TITLE: ${item.title}`;

        const poster = document.createElement("img");
        poster.src = item.poster_path;
        poster.loading = "lazy";
        poster.alt = item.title || "Movie poster";

        const releaseDate = document.createElement("h3");
        releaseDate.textContent = `DOR: ${item.release_date}`;

        const exists = item.media_type === "movie"
            ? mymovies.some(myitem => myitem.tmdb_id === item.tmdb_id)
            : mytvs.some(myitem => myitem.tmdb_id === item.tmdb_id);

        const libraryButton = document.createElement("button");
        libraryButton.textContent = exists
            ? "REMOVE FROM LIBRARY"
            : "ADD TO MY LIBRARY";

        libraryButton.className = "library-button";

        const viewDetailsButton = document.createElement("button");
        viewDetailsButton.textContent = "VIEW DETAILS";
        viewDetailsButton.className = "view-details";

        libraryButton.dataset.id = item.tmdb_id;
        libraryButton.dataset.type = item.media_type;
        libraryButton.dataset.status = exists ? "REMOVE" : "ADD";

        viewDetailsButton.dataset.id = item.tmdb_id;
        viewDetailsButton.dataset.type = item.media_type;

        const recommendButton = document.createElement("button");
        recommendButton.textContent = "RECOMMEND BUTTON";
        recommendButton.dataset.id = item.tmdb_id;
        recommendButton.dataset.media_type = item.media_type;
        recommendButton.className = "RecommendButton";

        const recommendedTo = document.createElement("h3");
        recommendedTo.textContent = `RECOMMENDED TO: ${item.receiver_username}`;
        recommendedTo.className = "recommended-to";        

        card.append(
            poster,
            title,
            releaseDate,
            libraryButton,
            viewDetailsButton,
            recommendedTo,
            recommendButton
        );

        recommendedSentContainer.appendChild(card);
    });    
    recommended_got.forEach(item => {

        const card = document.createElement("div");
        card.className = "card";


        const title = document.createElement("h3");
        title.textContent = `TITLE: ${item.title}`;

        const poster = document.createElement("img");
        poster.src = item.poster_path;
        poster.loading = "lazy";
        poster.alt = item.title || "Movie poster";

        const releaseDate = document.createElement("h3");
        releaseDate.textContent = `DOR: ${item.release_date}`;

        const exists = mymovies.some(myitem =>
            myitem.tmdb_id === item.tmdb_id
        ) || mytvs.some(myitem =>
            myitem.tmdb_id === item.tmdb_id
        );

        const libraryButton = document.createElement("button");
        libraryButton.textContent = exists
            ? "REMOVE FROM LIBRARY"
            : "ADD TO MY LIBRARY";

        libraryButton.className = "library-button";

        const viewDetailsButton = document.createElement("button");
        viewDetailsButton.textContent = "VIEW DETAILS";
        viewDetailsButton.className = "view-details";

        libraryButton.dataset.id = item.tmdb_id;
        libraryButton.dataset.type = item.media_type;
        libraryButton.dataset.status = exists ? "REMOVE" : "ADD";

        viewDetailsButton.dataset.id = item.tmdb_id;
        viewDetailsButton.dataset.type = item.media_type;

        const recommendButton = document.createElement("button");
        recommendButton.textContent = "RECOMMEND BUTTON";
        recommendButton.dataset.id = Number(item.tmdb_id);
        recommendButton.dataset.media_type = item.media_type;
        recommendButton.className = "RecommendButton";

        const recommendedBy = document.createElement("h3");
        recommendedBy.textContent = `RECOMMENDED BY: ${item.sender_username}`; 

        recommendedBy.className = "recommended-by";   

        card.append(
            poster,
            title,
            releaseDate,
            libraryButton,
            viewDetailsButton,
            recommendButton,
            recommendedBy
        );

        recommendedGetContainer.appendChild(card);
    });    
}

/* EVENT DELEGATION */

document.addEventListener("click", async function(event) {

    // MOVIES
    if (event.target === movieSectionButton) {

        showSection(movieSection);
        clicked(movieSectionButton);

        if (allMovies.length === 0) {
            await load_movies(true);
        }
    }

    // TV
    if (event.target === tvSectionButton) {

        showSection(tvSection);
        clicked(tvSectionButton);

        if (allTV.length === 0) {
            await load_tv(true);
        }
    }

    // PROFILE
    if (event.target === profileSectionButton) {

        showSection(profileSection);
        clicked(profileSectionButton);
    }



    // TRENDING
    if (event.target === trendingSectionButton) {

        showSection(trendingSection);
        clicked(trendingSectionButton);

        trendingMoviesContainer.classList.add("active");
        trendingTVContainer.classList.remove("active");

        trendingMoviesButton.classList.add("active");
        trendingTVButton.classList.remove("active");

        if (trendingMovies.length === 0) {
            await load_Trendingmovies();
        }
    }

    // MY LIBRARY
    if (event.target === watchlistSectionButton) {

        showSection(watchlistSection);
        clicked(watchlistSectionButton);

        libraryMoviesContainer.classList.add("active");
        libraryTVContainer.classList.remove("active");

        libraryMoviesButton.classList.add("active");
        libraryTVButton.classList.remove("active");

        if (allLibraryMovies.length === 0) {
            await load_library("movie", true);
        }
    }

    // TRENDING MOVIES TAB
    if (event.target === trendingMoviesButton) {

        trendingMoviesContainer.classList.add("active");
        trendingTVContainer.classList.remove("active");

        trendingMoviesButton.classList.add("active");
        trendingTVButton.classList.remove("active");

        if (trendingMovies.length === 0) {
            await load_Trendingmovies();
        }
    }

    // TRENDING TV TAB
    if (event.target === trendingTVButton) {

        trendingTVContainer.classList.add("active");
        trendingMoviesContainer.classList.remove("active");

        trendingTVButton.classList.add("active");
        trendingMoviesButton.classList.remove("active");

        if (trendingTV.length === 0) {
            await load_Trendingtv();
        }
    }

    // LIBRARY MOVIES TAB
    if (event.target === libraryMoviesButton) {

        libraryMoviesContainer.classList.add("active");
        libraryTVContainer.classList.remove("active");

        libraryMoviesButton.classList.add("active");
        libraryTVButton.classList.remove("active");

        await load_library("movie", true);
    }

    // LIBRARY TV TAB
    if (event.target === libraryTVButton) {

        libraryTVContainer.classList.add("active");
        libraryMoviesContainer.classList.remove("active");

        libraryTVButton.classList.add("active");
        libraryMoviesButton.classList.remove("active");

        await load_library("tv", true);
    }
    // social section
    if (event.target === socialSectionButton) {

        showSection(socialSection);
        clicked(socialSectionButton);

        socialSearchContainer.classList.add("active");
        socialRequestsContainer.classList.remove("active");

        socialSearchButton.classList.add("active");
        socialRequestsButton.classList.remove("active");
    }    
    //social search
    if (event.target === socialSearchButton) {

        socialSearchContainer.classList.add("active");
        socialRequestsContainer.classList.remove("active");

        socialSearchButton.classList.add("active");
        socialRequestsButton.classList.remove("active");
    }

    // social connection requests
    if (event.target === socialRequestsButton) {

        socialSearchContainer.classList.remove("active");
        socialRequestsContainer.classList.add("active");

        socialSearchButton.classList.remove("active");
        socialRequestsButton.classList.add("active");
        notificationsContainer.innerHTML = '';
        try{
            const response = await fetch('/api/viewNotifications');
            const html = await response.text();
            if(!response.ok){
                throw new Error( `HTTP ERROR: ${response.status}`);
            }
            notificationsContainer.innerHTML = html;
        }
        catch(error){
            console.log("ERROR: ",error);
            notificationsContainer.innerHTML = "ERROR LOADING ";
        }

    }
    // 
    if (event.target === recommendationSectionButton) {
        showSection(recommendationSection);
        clicked(recommendationSectionButton);

        recommendationSentSection.classList.add("active");
        recommendationReceivedSection.classList.remove("active");

        recommendationSentSectionButton.classList.add("active");
        recommendationReceivedSectionButton.classList.remove("active");
        await load_recommended();



    }
    if (event.target === recommendationSentSectionButton) {
        showSection(recommendationSection);
        clicked(recommendationSectionButton);

        recommendationSentSection.classList.add("active");
        recommendationReceivedSection.classList.remove("active");

        recommendationSentSectionButton.classList.add("active");
        recommendationReceivedSectionButton.classList.remove("active");
        await load_recommended();


    }
    if (event.target === recommendationReceivedSectionButton) {
        showSection(recommendationSection);
        clicked(recommendationSectionButton);

        recommendationSentSection.classList.remove("active");
        recommendationReceivedSection.classList.add("active");

        recommendationSentSectionButton.classList.remove("active");
        recommendationReceivedSectionButton.classList.add("active");
        await load_recommended();

    }    
    // VIEW DETAILS

    if (event.target.classList.contains("view-details")) {

        const itemId = Number(event.target.dataset.id);
        const mediaType = event.target.dataset.type;

        let selectedItem;

        if (mediaType === "movie") {

            selectedItem =
                allMovies.find(item => item.tmdb_id === itemId) ||
                allLibraryMovies.find(item => item.tmdb_id === itemId) ||
                trendingMovies.find(item => item.tmdb_id === itemId) ||
                recommended_sent.find(item =>
                    item.tmdb_id === itemId && item.media_type === "movie"
                ) ||
                recommended_got.find(item =>
                    item.tmdb_id === itemId && item.media_type === "movie"
                );

        } else if (mediaType === "tv") {

            selectedItem =
                allTV.find(item => item.tmdb_id === itemId) ||
                allLibraryTV.find(item => item.tmdb_id === itemId) ||
                trendingTV.find(item => item.tmdb_id === itemId) ||
                recommended_sent.find(item =>
                    item.tmdb_id === itemId && item.media_type === "tv"
                ) ||
                recommended_got.find(item =>
                    item.tmdb_id === itemId && item.media_type === "tv"
                );
        }

        if (!selectedItem) {
            console.error("Item not found:", itemId, mediaType);
            return;
        }

        modal.querySelector("#itemTitle").textContent = selectedItem.title;
        modal.querySelector("#poster").src = selectedItem.poster_path;
        modal.querySelector("#overview").textContent =
            selectedItem.overview || "No overview available.";

        modal.querySelector("#popularity").textContent =
            `POPULARITY: ${selectedItem.popularity ?? "N/A"}`;

        modal.querySelector("#vote_average").textContent =
            `VOTE AVERAGE: ${selectedItem.vote_average ?? "N/A"} | VOTES: ${selectedItem.vote_count ?? "N/A"}`;

        modal.classList.add("open");
    }

    // ADD / REMOVE LIBRARY
    if (event.target.classList.contains("library-button")) {

        const cardID = Number(event.target.dataset.id);
        const type = event.target.dataset.type;
        const button = event.target;

        let selected;
        let media_type;

        if (type === "movie" || type === "trendingmovie") {

            media_type = "movie";

            selected = allMovies.find(item => item.tmdb_id === cardID) ||
                trendingMovies.find(item => item.tmdb_id === cardID) ||
                allLibraryMovies.find(item => item.tmdb_id === cardID) ||
                recommended_sent.find(item =>
                    item.tmdb_id === cardID && item.media_type === "movie"
                )
                || recommended_got.find(item =>
                    item.tmdb_id === cardID && item.media_type === "movie"
                )                

        } else if (type === "tv" || type === "trendingtv") {

            media_type = "tv";

            selected = allTV.find(item => item.tmdb_id === cardID) ||
                trendingTV.find(item => item.tmdb_id === cardID) ||
                allLibraryTV.find(item => item.tmdb_id === cardID) ||
                recommended_sent.find(item =>
                    item.tmdb_id === cardID && item.media_type === "tv"
                )
                || recommended_got.find(item =>
                    item.tmdb_id === cardID && item.media_type === "tv"
                )                      
        }

        if (!selected) return;

        button.disabled = true;

        try {
            if (button.dataset.status === "ADD") {

                const success = await add_to_library(selected, media_type);

                if (success) {
                    syncLibraryButtons(cardID, media_type, true);
                }

            } else if (button.dataset.status === "REMOVE") {

                const success = await remove_from_library(selected, media_type);

                if (success) {
                    syncLibraryButtons(cardID, media_type, false);
                }
            }
        } finally {
            button.disabled = false;
        }        
    }
    if(event.target.classList.contains("RecommendButton")){
        const tmdb_id = Number(event.target.dataset.id);
        const type = event.target.dataset.media_type;
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        let selected;
        let media_type = "";
        if (type === "movie") {

            media_type = "movie";

            selected = allMovies.find(item => item.tmdb_id === tmdb_id) ||
                trendingMovies.find(item => item.tmdb_id === tmdb_id) ||
                allLibraryMovies.find(item => item.tmdb_id === tmdb_id) ||
                recommended_sent.find(item =>
                    item.tmdb_id === tmdb_id && item.media_type === "movie"
                )
                || recommended_got.find(item =>
                    item.tmdb_id === tmdb_id && item.media_type === "movie"
                )                

        } else if (type === "tv") {

            media_type = "tv";

            selected = allTV.find(item => item.tmdb_id === tmdb_id) ||
                trendingTV.find(item => item.tmdb_id === tmdb_id) ||
                allLibraryTV.find(item => item.tmdb_id === tmdb_id) ||
                recommended_sent.find(item =>
                    item.tmdb_id === tmdb_id && item.media_type === "tv"
                )
                || recommended_got.find(item =>
                    item.tmdb_id === tmdb_id && item.media_type === "tv"
                )
        }
        if (!selected) return;

        try{
            const response = await fetch(`/api/recommendationForm`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    "tmdb_id": selected.tmdb_id,
                    "title": selected.title,
                    "release_date": selected.release_date,
                    "overview": selected.overview,
                    "popularity": selected.popularity,
                    "poster_path": selected.poster_path,
                    "vote_average": selected.vote_average,
                    "vote_count": selected.vote_count,
                    "media_type": media_type
                })                
            });

            const html = await response.text();

            if (!response.ok) {
                throw new Error(`HTTP ERROR: ${response.status}`);

            }
            const container = document.querySelector("#recommend-form-container");

            container.innerHTML = html;
            document.querySelector("#recommend-modal").classList.add("open");
        }
        catch(error){
            console.log("ERROR: ",error);

        }

    }
    // CLOSE MODAL BUTTON
    if (event.target === closeModal) {
        modal.classList.remove("open");
    }

    // CLICK OUTSIDE MODAL
    if (event.target === modal) {
        modal.classList.remove("open");
    }

    // LOAD MORE MOVIES
    if (event.target === loadMoreMovieButton) {
        await load_movies(false);
    }

    // LOAD MORE TV
    if (event.target === loadMoreTVButton) {
        await load_tv(false);
    }

});

if (document.querySelector("#recommend-modal")) {
    document.querySelector("#recommend-modal").addEventListener("click", function(event) {

    if (
        event.target.id === "close-exit-form" ||
        event.target === this
    ) {
        this.classList.remove("open");
    }

    });
}

/* MOVIE SEARCH AND GENRE FILTERS */

if (submitMoviesButton && clearMoviesButton) {

    // SUBMIT
    submitMoviesButton.addEventListener("click", async function () {

        movieFilters.search = searchMovies.value.trim();

        const selectedGenres = [];

        genreMovies.forEach(genre => {
            if (genre.checked) {
                selectedGenres.push(genre.value);
            }
        });

        movieFilters.genre = selectedGenres.join("|");

        await load_movies(true);
    });


    // CLEAR
    clearMoviesButton.addEventListener("click", async function () {

        searchMovies.value = "";

        genreMovies.forEach(genre => {
            genre.checked = false;
        });

        movieFilters = {
            search: "",
            genre: ""
        };

        await load_movies(true);
    });
}

/*TV SEARCH AND GENRE FILTERS */
if (submitTVButton && clearTVButton) {

    // SUBMIT
    submitTVButton.addEventListener("click", async function () {

        tvFilters.search = searchTV.value.trim();

        const selectedGenres = [];

        genreTV.forEach(genre => {
            if (genre.checked) {
                selectedGenres.push(genre.value);
            }
        });

        tvFilters.genre = selectedGenres.join("|");

        await load_tv(true);
    });


    // CLEAR
    clearTVButton.addEventListener("click", async function () {

        searchTV.value = "";

        genreTV.forEach(genre => {
            genre.checked = false;
        });

        tvFilters = {
            search: "",
            genre: ""
        };

        await load_tv(true);
    });
}


/* TRENDING DURATION */

if (durationSelect) {

    durationSelect.addEventListener("change", async function() {

        if (trendingMoviesContainer.classList.contains("active")) {
            await load_Trendingmovies();
        } else {
            await load_Trendingtv();
        }

    });
}


libraryContainer.addEventListener('change', async function(event){
    if(event.target.classList.contains("watch-status")){
        const select = event.target;
        const tmdb_id = Number(event.target.dataset.id);
        const oldStatus = select.dataset.current_status ;
        const newStatus = select.value;
        const media_type = event.target.dataset.media_type;
        console.log(tmdb_id);
        console.log(oldStatus);
        console.log(newStatus);
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        try{
            const response = await fetch(`/api/updateStatus`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    "tmdb_id": tmdb_id,
                    "media_type": media_type,
                    "new_status": newStatus
                })
            })

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ERROR: ${response.status}`);

            } else {
                select.dataset.current_status = newStatus;
                select.value = newStatus;
                console.log("Status updated successfully!");
            }
        }
        catch(error){
            console.log("ERROR: ",error);
            select.value = oldStatus;
        }
        
    }

});

//social

searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);

    const query = searchInput.value.trim();

    if (controller) {
        controller.abort();
    }

    suggestionsBox.replaceChildren();

    if (query.length < 2) {
        return;
    }

    debounceTimer = setTimeout(() => {
        fetchSuggestions(query);
    }, 300);
});

async function fetchSuggestions(search) {
    controller = new AbortController();

    try {
        const response = await fetch(
            `/api/search?search=${encodeURIComponent(search)}`,
            { signal: controller.signal }
        );

        if (!response.ok) {
            throw new Error("Unable to fetch suggestions");
        }

        const data = await response.json();


        if (searchInput.value.trim() !== search) {
            return;
        }

        renderSuggestions(data.users || []);

    } catch (error) {
        if (error.name !== "AbortError") {
            console.error(error);
        }
    }
}

function renderSuggestions(users) {
    suggestionsBox.replaceChildren();

    if (users.length === 0) {
        const message = document.createElement("p");
        message.textContent = "No users found";
        suggestionsBox.appendChild(message);
        return;
    }

    users.forEach(user => {
   
        const card = document.createElement("div");
        card.className = "profilecard";
        card.id = `${user.user_id}`;

        const username = document.createElement("h3");
        username.textContent = `USERNAME: ${user.username}`;

        const fullname = document.createElement("h3");
        fullname.textContent = `FULLNAME: ${user.fullname}`  



        const viewProfileButton = document.createElement("button");
        viewProfileButton.textContent = "VIEW PROFILE";
        viewProfileButton.className = "view-profile";

        viewProfileButton.dataset.id = user.user_id;


        card.append(
            username,
            fullname,
            viewProfileButton
        );
        suggestionsBox.appendChild(card);
    });
}



socialSection.addEventListener("click", async function(event) {

    if (event.target.classList.contains("view-profile")) {

        const user_id = Number(event.target.dataset.id);

        try {

            const response = await fetch(`/api/viewProfile/${user_id}`);

            if (!response.ok) {
                throw new Error(`HTTP ERROR: ${response.status}`);
            }

            const html = await response.text();

            socialProfileContent.innerHTML = html;

            profileModal.classList.add("open");

        } catch (error) {

            console.error("Error loading profile:", error);
        }
    }

    if (event.target.classList.contains("connectionRequestButton")) {
        if (event.target.dataset.status !== "SEND CONNECTION REQUEST") {
            return;
        }        
        
        const receiver_id = Number(event.target.dataset.id);

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

            const response = await fetch(`/api/sendConnectionRequest`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    "receiver_id" : receiver_id
                })
            });
            const data = await response.json();    

            if (!response.ok) {
                throw new Error( data.error || `HTTP ERROR: ${response.status}`);

            }
            const connectionButton = document.querySelector('#connection-button');
            connectionButton.textContent = "PENDING";
            connectionButton.dataset.status = "PENDING";
            connectionButton.disabled = true;

        } catch (error) {

            console.error("Error:", error);
        }
    } 
});

if (notificationsContainer){
    notificationsContainer.addEventListener('click',async function(event){
        if (event.target.classList.contains("accept")){
            const notif_id = Number(event.target.dataset.id);

            try {
                const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

                const response = await fetch(`/api/acceptConnectionRequest`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        "notif_id" : notif_id
                    })
                });
                const data = await response.json();    

                if (!response.ok) {
                    throw new Error( data.error || `HTTP ERROR: ${response.status}`);

                }
                const declineButton = notificationsContainer.querySelector(`#decline-${notif_id}`);
                const acceptButton = notificationsContainer.querySelector(`#accept-${notif_id}`);
                acceptButton.textContent = "ACCEPTED";
                declineButton.disabled = true;                
                acceptButton.disabled = true;

            } catch (error) {
                console.error("Error:", error);
                const declineButton = notificationsContainer.querySelector(`#decline-${notif_id}`);
                const acceptButton = notificationsContainer.querySelector(`#accept-${notif_id}`);
                acceptButton.textContent = "ACCEPT";
                declineButton.disabled = false;                
                acceptButton.disabled = false;     
            }            

        }
        if (event.target.classList.contains("decline")){
            const notif_id = Number(event.target.dataset.id);

            try {
                const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

                const response = await fetch(`/api/declineConnectionRequest`, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        "notif_id" : notif_id
                    })
                });
                const data = await response.json();    

                if (!response.ok) {
                    throw new Error( data.error || `HTTP ERROR: ${response.status}`);

                }

                const declineButton = notificationsContainer.querySelector(`#decline-${notif_id}`);
                const acceptButton = notificationsContainer.querySelector(`#accept-${notif_id}`);
                declineButton.textContent = "DECLINED";
                declineButton.disabled = true;                
                acceptButton.disabled = true;


            } catch (error) {
                console.error("Error:", error);
                const declineButton = notificationsContainer.querySelector(`#decline-${notif_id}`);
                const acceptButton = notificationsContainer.querySelector(`#accept-${notif_id}`);
                declineButton.textContent = "DECLINE";
                declineButton.disabled = false;                
                acceptButton.disabled = false;                  
            }              
        }
    });
}



profileModal.addEventListener("click", function(event) {

    if (event.target.id === "close-profile-modal" ||
        event.target === profileModal) {

        profileModal.classList.remove("open");
    }

});
/* FLASH MESSAGES */

const flashMessages = document.querySelectorAll(".flash-message");

flashMessages.forEach(message => {

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

closeButtons.forEach(button => {

    button.addEventListener("click", () => {

        const message = button.parentElement;

        message.classList.add("hide");

        setTimeout(() => {
            message.remove();
        }, 500);

    });

});


/* INITIAL MOVIE LOAD */

if (moviesContainer) {
    load_movies(true);
}

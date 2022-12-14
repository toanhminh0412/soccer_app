// Renders games or groups based on hash in url
// #games: Display games, hide groups
// #groups: Display groups, hide games
const renderByHash = () => {
    const hash = window.location.hash
    const gameContainers = $('.game-containers');
    const groupContainersAsCaptain = $('.group-as-captain-containers');
    const groupContainersAsCoCaptain = $('.group-as-cocaptain-containers');
    const groupRequests = $('.group-requests');
    if (!hash || hash === '#games') {
        gameContainers.removeClass('d-none');
        groupContainersAsCaptain.addClass('d-none');
        groupContainersAsCoCaptain.addClass('d-none');
        groupRequests.addClass('d-none');
    } else if (hash === '#groups') {
        gameContainers.addClass('d-none');
        groupRequests.addClass('d-none');
        groupContainersAsCaptain.removeClass('d-none');
        groupContainersAsCoCaptain.removeClass('d-none');
    } else if (hash === '#requests') {
        gameContainers.addClass('d-none');
        groupContainersAsCaptain.addClass('d-none');
        groupContainersAsCoCaptain.addClass('d-none');
        groupRequests.removeClass('d-none');
    }
}

// Initilization function
const dashboardInit = () => {
    // Set min time of a game being created to be the current time
    var tzoffset = (new Date()).getTimezoneOffset() * 60000; //offset in milliseconds
    let currentDatetime = new Date(Date.now() - tzoffset).toISOString().slice(0, -8); //yyyy-MM-ddThh:mm
    document.querySelector("#game-form-date").value = currentDatetime;
    document.querySelector("#game-form-date").min = currentDatetime;

    renderByHash();
    $(window).on('hashchange', function() {
        renderByHash();
    })
}

dashboardInit();
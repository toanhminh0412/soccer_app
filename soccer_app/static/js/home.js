// Initilization function
const init = () => {
    console.log('home.js is hooked');
    // Set min time of a game being created to be the current time
    var tzoffset = (new Date()).getTimezoneOffset() * 60000; //offset in milliseconds
    let currentDatetime = new Date(Date.now() - tzoffset).toISOString().slice(0, -8); //yyyy-MM-ddThh:mm
    document.querySelector("#game-form-date").value = currentDatetime;
    document.querySelector("#game-form-date").min = currentDatetime;
}

init();
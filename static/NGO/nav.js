function updateClock(){
  const now = new Date();

  document.getElementById("clock").innerHTML =
  now.toLocaleTimeString();
}

setInterval(updateClock,1000);
updateClock();

// ===== SIDEBAR =====

const menu = document.getElementById("menu");
const sidebar = document.getElementById("sidebar");
const main = document.querySelector(".main");

// Toggle Sidebar

menu.onclick = (e) => {

    e.stopPropagation();

    sidebar.classList.toggle("closed");
    main.classList.toggle("full");

};

// Close Sidebar Outside Click

document.addEventListener("click",(e)=>{

    const insideSidebar = sidebar.contains(e.target);
    const isMenu = menu.contains(e.target);

    if(!insideSidebar && !isMenu){

        sidebar.classList.add("closed");
        main.classList.add("full");

    }

});

// Prevent Sidebar Close

sidebar.onclick = (e)=>{
    e.stopPropagation();
};
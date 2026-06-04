const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const overlay = document.getElementById('overlay');
const closeBtn = document.getElementById('closeBtn');
const links = document.querySelectorAll('.mobile-links a, .nav-links a');

function openMenu() {
  mobileMenu.classList.add('open');
  overlay.classList.add('show');
}

function closeMenu() {
  mobileMenu.classList.remove('open');
  overlay.classList.remove('show');
}

hamburger.addEventListener('click', openMenu);
closeBtn.addEventListener('click', closeMenu);
overlay.addEventListener('click', closeMenu);

links.forEach(link => {
  link.addEventListener('click', () => {
    links.forEach(l => l.classList.remove('active'));
    link.classList.add('active');
    closeMenu();
  });
});

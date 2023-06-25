const darkmodeCookie = 'darkmode=true';
const cookiePath = 'path=/';

let btn = document.querySelectorAll('#darkModeToggle')[0];

if(btn){
    btn.addEventListener('click', function(){
        toggleButton(this)
    });

    function toggleButton (btn) {
        let allNodes = btn.children;
    
        for (j = 0; j < allNodes.length; j++) {
            let node = allNodes[j];
            let isActive;
    
            if (node.classList.contains('btn-circle')) {
                if (!node.classList.contains('active')) {
                    node.classList.add('active');
                    isActive = true;
                } else {
                    node.classList.remove('active');
                    isActive = false;
                }
    
                if (isActive && !btn.classList.contains('btn-holder-active')) {
                    btn.classList.add('btn-holder-active');
                    setDarkModeCookie(true);
                } else if(btn.classList.contains('btn-holder-active')) {
                    btn.classList.remove('btn-holder-active');
                    setDarkModeCookie(false);
                }
            }
    
            if (node.classList.contains('checkbox')) {
                if (isActive) {
                    node.checked = true;
                } else {
                    node.checked = false;
                }
            }
        }
    }
    function setDarkModeCookie(set){
        let bootstrap = document.getElementById('bootstrap')
        let darkmodeBootstrap = document.getElementById('bootstrapDarkMode')
        let darkmodeCss = document.getElementById('darkModeOverride')
        if(set){
            document.cookie = `${darkmodeCookie};${cookiePath}`;
            bootstrap.disabled = true;
            darkmodeBootstrap.disabled = false;
            darkmodeCss.disabled = false;
        }
        else
        {
            document.cookie = `${darkmodeCookie};${cookiePath}; expires=Thu, 01 Jan 1970 00:00:00 UTC;`;
            darkmodeBootstrap.disabled = true;
            darkmodeCss.disabled = true;
            bootstrap.disabled = false;
        }
    }
    
    function checkBrowserDarkMode(){
        if(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches && document.cookie.search(darkmodeCookie) === -1)
            toggleButton(btn);
    
        if(window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches && document.cookie.search(darkmodeCookie) === 0)
            toggleButton(btn);
    }
    
    checkBrowserDarkMode();
}
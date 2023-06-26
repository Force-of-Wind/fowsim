var darkModeButton = $('#darkModeToggle');
darkModeButton.on('click', toggleButton);

function readThemeCookie() {
    let value = $.cookie('theme');
    let previousSystemPreference = $.cookie('browserPreferredTheme');
    let preferredTheme = getBrowserPreferredTheme();

    // If the cookie is undefined, then default it to the browser's preferred theme.
    // If the browser has no preference, the default is light.
    if (!value || previousSystemPreference != preferredTheme) {
        if (preferredTheme == 'dark') {
            value = 'dark';
        }
        else {
            value = 'light';
        }
        setThemeCookie(value);
    }

    return value;
}

function setThemeCookie(theme) {
    $.cookie('theme', theme, { path: '/' });
    $.cookie('browserPreferredTheme', getBrowserPreferredTheme(), { path: '/' });
}

function getBrowserPreferredTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)
        return 'dark';

    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches)
        return 'light';

    return 'none';
}

function toggleButton() {
    let currentTheme = readThemeCookie();
    if (currentTheme == 'dark') {
        setThemeCookie('light');
    }
    else {
        setThemeCookie('dark');
    }
    checkAndApplyTheme();
}

function setButtonState(selected) {
    if (selected) {
        darkModeButton.addClass('btn-holder-active');
        darkModeButton.children('.btn-circle').eq(0).addClass('active');
        darkModeButton.children('.checkbox').eq(0).checked = true;
    }
    else {
        darkModeButton.removeClass('btn-holder-active');
        darkModeButton.children('.btn-circle').eq(0).removeClass('active');
        darkModeButton.children('.checkbox').eq(0).checked = false;
    }
}

function setSiteTheme(theme) {
    if (theme == 'dark') {
        $('#bootstrap').prop('disabled', true);
        $('#bootstrapDarkMode').prop('disabled', false);
        $('#darkModeOverride').prop('disabled', false);
        setButtonState(true);
    }
    else {
        $('#bootstrapDarkMode').prop('disabled', true);
        $('#darkModeOverride').prop('disabled', true);
        $('#bootstrap').prop('disabled', false);
        setButtonState(false);
    }
}

function checkAndApplyTheme() {
    let theme = readThemeCookie();
    setSiteTheme(theme);
}

checkAndApplyTheme();

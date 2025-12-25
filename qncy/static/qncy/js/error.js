document.addEventListener('htmx:responseError', e => {
    alert(e.detail.xhr.responseText)
});

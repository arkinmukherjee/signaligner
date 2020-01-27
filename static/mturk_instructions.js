// Step 1 - NY Times article

function clickPrev(fromPage, toPage) {
    var logElement = parent.document.getElementById('modal-log-prev');
    logElement.innerText = fromPage;
    logElement.click();
    window.location.href = toPage;
}

function clickNext(fromPage, toPage) {
    var logElement = parent.document.getElementById('modal-log-next');
    logElement.innerText = fromPage;
    logElement.click();

    if (fromPage.includes("article") && parent.document.getElementById('modal-log-article').innerText === "") {
        alert("Please read the NY Times article link first");
    } else {
        window.location.href = toPage;
    }
}

function clickArticle() {
    var logElement = parent.document.getElementById('modal-log-article')
    logElement.innerText = "clicked";
    logElement.click();
}

// Step 2 - Ground truth screenshot examples

function modulo(x,y) {
    return ((x % y) + y) % y;
}

function changeSlide(n) {

    slideIdx =  modulo((slideIdx + n), images.length);

    var curIdx;

    for (curIdx = 0; curIdx < images.length; curIdx++) {
        if (curIdx === slideIdx) {
            images[curIdx].setAttribute("style","display:inline-block");
            caption_labels[curIdx].setAttribute("style","display:inline-block");
            subcaption_labels[curIdx].setAttribute("style", "display:inline-block")
        } else {
            images[curIdx].setAttribute("style","display:none");
            caption_labels[curIdx].setAttribute("style","display:none");
            subcaption_labels[curIdx].setAttribute("style", "display:none")
        }
    }
}

function clickSlideshowButton() {
    var logElement = parent.parent.document.getElementById('modal-log-slideshow');
    var page = parent.document.getElementById('pagename').innerText;
    logElement.innerText = page;
    logElement.click();
}

function closeHelp() {
    parent.document.getElementById('modal-log-close').click();
}

function advanceDataset() {
    parent.document.getElementById('modal-advance-dataset').click();
}
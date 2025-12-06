// Fetch AI suggestion from backend
function getSuggestion() {
    // Trying to find parent div for student question
    let parent = document.getElementById("qaContentViewId")
    let elem = null
    if (parent) {
        // Finding student question
        elem = parent.getElementsByClassName("render-html-content overflow-hidden latex_process")[0]
    }
    // If we found the question, then we can make the request
    if (elem && elem.innerText) {
            fetch("http://127.0.0.1:5000/suggest", {
                method: "POST",
                body: JSON.stringify({"question": elem.innerText}),
                headers: {"Content-Type": "application/json"}
            }).then(r => {
                if (r.ok) {
                    r.json().then(data => {
                        // Display the suggestion once we have the data
                        displaySuggestion(data)
                    })
                }
            }).catch(err => {
                displaySuggestion({"suggested_answer": "ERROR: could not get suggestion"})
            })

    } else {
        // Try again in a second
        console.log("Question not loaded")
        setTimeout(getSuggestion, 1000)
    }
}

// Defining Suggestion HTML
let suggestElem = document.createElement("article")
suggestElem.className = "answer px-2 mx-2 pt-2 pb-3"
suggestElem.style.backgroundColor = "color-mix(in srgb, #FEE4FF 50%, var(--background))"
suggestElem.innerHTML = `
<header class="pt-1 d-flex gap-2 align-items-center">
    <svg class="flex-shrink-0 ml-1" width="21px" height="24px" aria-hidden="true" focusable="false" viewBox="0 0 14 16" preserveAspectRatio="none">
        <rect fill="#d242fa" x="0" y="0" width="14" height="16" rx="2" ></rect>
        <path d="M2 5 6.5 5 6.5 3 6 3 6 2 8 2 8 3 7.5 3 7.5 5 12 5 12 12 2 12 2 5M10.5 10.5 10.5 6.5 3.5 6.5 3.5 10.5ZM5 7 6 7 6 10 5 10 5 7ZM8 7 9 7 9 10 8 10 8 7Z" fill="#FFFFFF"></path>
    </svg>
    <span>AI's Suggestion</span>
</header>
<div class="content pr-0 pl-4 ml-2 mt-2 container-fluid">
    <div class="g-0 row">
        <div class="col">
            <div class="pt-0 pb-1 history-selection">
                <div id="AI_EXTENSION_render" data-id="renderHtmlId" class="render-html-content overflow-hidden latex_process">
                </div>
            </div>
        </div>
    </div>
</div>
`

// Defining divider for answers
let divider = document.createElement("hr")
divider.className = "my-0 mx-2"

// Insert Suggestion Element
function insertSuggestionElement() {
    // Trying to find instructor's answer
    let instructorAnswer = document.querySelector('[data-id="i_answer"]')
    // If we found the answer, the page has loaded
    if (instructorAnswer) {
        // Insert element below the answer
        instructorAnswer.insertAdjacentElement('afterend', suggestElem)
        instructorAnswer.insertAdjacentElement('afterend', divider)
    } else {
        // Try again in a second
        console.log("Page still loading")
        setTimeout(insertSuggestionElement, 1000)
    }
}

// Display suggestion in new element
function displaySuggestion(data) {
    // Trying to find suggestion element
    let elem = document.getElementById("AI_EXTENSION_render")
    // If we found the element, we can insert our suggestion
    if (elem) {
        // Insert suggestion data
        let suggestion = data["suggested_answer"]
        elem.innerHTML = "<p>" + suggestion + "</p>"
    } else {
        // Try again in half a second (this should be very rare)
        console.log("Suggestion element still loading (!!!)")
        setTimeout(() => displaySuggestion(data), 500)
    }
}

insertSuggestionElement()
getSuggestion()
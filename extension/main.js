function printQuestion() {
    let elem = document.getElementById("mhdw2m7665933u_render")
    if (elem && elem.innerText) {
        console.log(elem.innerText)
            fetch("http://127.0.0.1:5000/suggest", {
                method: "POST",
                body: JSON.stringify({"question": elem.innerText}),
                headers: {"Content-Type": "application/json"}
            }).then(r => {
                if (!r.ok) {
                    console.log(r)
                } else {
                    r.json().then(data => {
                        console.log(data["suggested_answer"])
                    })
                }
            }).catch(err => {
                console.log(err)
            })

    } else {
        console.log("Question not loaded")
        setTimeout(printQuestion, 500)
    }
}
printQuestion()
const input = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const chat = document.getElementById("chat");
const clearButton = document.getElementById("clearButton");


// ============================================================
// ADD MESSAGE TO CHAT
// ============================================================

function addMessage(message, type) {

    const messageDiv = document.createElement("div");

    messageDiv.className = `message ${type}`;

    const content = document.createElement("div");

    content.className = "message-content";

    content.textContent = message;

    messageDiv.appendChild(content);

    chat.appendChild(messageDiv);

    chat.scrollTop = chat.scrollHeight;
}


// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {

    const message = input.value.trim();

    if (!message) {
        return;
    }


    // Show user's message
    addMessage(message, "user");

    input.value = "";

    sendButton.disabled = true;


    // Show thinking message
    addMessage("Thinking...", "ai");


    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });


        const data = await response.json();


        // Remove "Thinking..."
        const messages = document.querySelectorAll(".message");

        messages[messages.length - 1].remove();


        // Show AI answer
        if (data.answer) {

            addMessage(data.answer, "ai");


            // ------------------------------------------------
            // SHOW SOURCES
            // ------------------------------------------------

            if (data.sources && data.sources.length > 0) {

                const sourceDiv =
                    document.createElement("div");

                sourceDiv.className = "sources";


                const sourceTitle =
                    document.createElement("strong");

                sourceTitle.textContent =
                    "Sources:";

                sourceDiv.appendChild(sourceTitle);


                data.sources.forEach(function(source) {

                    const sourceItem =
                        document.createElement("div");

                    sourceItem.className =
                        "source-item";


                    if (source.page) {

                        sourceItem.textContent =
                            `${source.source} - Page ${source.page}`;

                    } else {

                        sourceItem.textContent =
                            source.source;

                    }


                    sourceDiv.appendChild(sourceItem);

                });


                chat.appendChild(sourceDiv);

                chat.scrollTop = chat.scrollHeight;

            }

        } else {

            addMessage(

                data.error ||
                "Something went wrong.",

                "ai"

            );

        }


    } catch (error) {

        // Remove "Thinking..."
        const messages =
            document.querySelectorAll(".message");

        messages[messages.length - 1].remove();


        addMessage(

            "Unable to connect to the server.",

            "ai"

        );


        console.error(error);

    }


    sendButton.disabled = false;

    input.focus();

}


// ============================================================
// SEND BUTTON
// ============================================================

sendButton.addEventListener(

    "click",

    sendMessage

);


// ============================================================
// ENTER KEY
// ============================================================

input.addEventListener(

    "keydown",

    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }

);


// ============================================================
// SUGGESTION BUTTON
// ============================================================

function askSuggestion(button) {

    input.value = button.innerText;

    sendMessage();

}


// ============================================================
// CLEAR CHAT
// ============================================================

clearButton.addEventListener(

    "click",

    async function() {

        try {

            await fetch(

                "/clear",

                {
                    method: "POST"
                }

            );

        } catch (error) {

            console.error(error);

        }


        // Remove existing chat
        chat.innerHTML = "";


        // Create welcome message
        const welcome =
            document.createElement("div");

        welcome.className = "welcome";


        welcome.innerHTML = `

            <div class="welcome-icon">
                ✦
            </div>

            <h2>
                How can I help you?
            </h2>

            <p>
                Ask me anything about the documents
                loaded into the knowledge base.
            </p>

        `;


        chat.appendChild(welcome);

        input.focus();

    }

);


// ============================================================
// FILE UPLOAD
// ============================================================

const uploadForm =
    document.getElementById("uploadForm");

const fileInput =
    document.getElementById("fileInput");

const uploadStatus =
    document.getElementById("uploadStatus");


// Make sure upload elements exist
if (uploadForm && fileInput && uploadStatus) {

    uploadForm.addEventListener(

        "submit",

        async function(event) {

            event.preventDefault();


            // ------------------------------------------------
            // CHECK FILE
            // ------------------------------------------------

            if (!fileInput.files.length) {

                uploadStatus.textContent =
                    "Please select a file.";

                return;

            }


            // ------------------------------------------------
            // CREATE FORM DATA
            // ------------------------------------------------

            const formData =
                new FormData();


            formData.append(

                "file",

                fileInput.files[0]

            );


            // ------------------------------------------------
            // SHOW STATUS
            // ------------------------------------------------

            uploadStatus.textContent =
                "Uploading and processing...";


            try {

                // ------------------------------------------------
                // SEND FILE TO FLASK
                // ------------------------------------------------

                const response =
                    await fetch(

                        "/upload",

                        {

                            method: "POST",

                            body: formData

                        }

                    );


                const data =
                    await response.json();


                // ------------------------------------------------
                // ERROR
                // ------------------------------------------------

                if (!response.ok) {

                    uploadStatus.textContent =
                        data.error ||
                        "Upload failed.";

                    return;

                }


                // ------------------------------------------------
                // SUCCESS
                // ------------------------------------------------

                uploadStatus.textContent =

                    data.message +
                    " " +
                    data.chunks +
                    " chunks created.";


                // Clear file input
                fileInput.value = "";


                // ------------------------------------------------
                // RELOAD PAGE
                // ------------------------------------------------
                // This updates the document list/sidebar.

                setTimeout(function() {

                    location.reload();

                }, 1000);


            } catch (error) {

                uploadStatus.textContent =
                    "Upload failed.";

                console.error(error);

            }

        }

    );

}
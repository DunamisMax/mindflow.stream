document.addEventListener("DOMContentLoaded", () => {
  fetchNotes(1); // Fetch the first page of notes on load
  attachFormSubmitListener();
});

let lastPostTime = 0; // Define lastPostTime as a global variable

function attachFormSubmitListener() {
  const form = document.getElementById("note-form");
  if (form) {
    form.addEventListener("submit", addNote);
  }
}

function addNote(event) {
  event.preventDefault();

  const currentTime = Date.now();
  const timeSinceLastPost = (currentTime - lastPostTime) / 1000; // Convert milliseconds to seconds

  if (timeSinceLastPost < 10) {
    const remainingTime = 10 - timeSinceLastPost;
    notifyUser(
      `Please wait ${remainingTime.toFixed(
        1
      )} more seconds before posting again.`,
      true
    );
    return;
  }

  lastPostTime = currentTime;

  const noteText = document.querySelector('[name="comment"]').value;
  if (!noteText.trim()) {
    notifyUser("Please enter a valid comment.", true);
    return;
  }

  const jsonData = JSON.stringify({ text: noteText });
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");

  fetch("/comments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken,
    },
    body: jsonData,
  })
    .then(responseHandler)
    .then(() => {
      fetchNotes(1); // Refresh to the first page to show the new note
      notifyUser("Comment added successfully!");
      document.getElementById("note-form").reset();
    })
    .catch((error) => {
      console.error("Error:", error);
      notifyUser("Error adding comment. Please try again.", true);
    });
}

function fetchNotes(page) {
  const notesContainer = document.getElementById("notes-container");
  notesContainer.innerHTML = '<div class="loading">Loading notes...</div>';

  fetch(`/comments?page=${page}`)
    .then(handleFetchResponse)
    .then((data) => {
      displayNotes(data);
      createPaginationControls(data.total_pages, page);
    })
    .catch(handleFetchError);
}

function displayNotes(data) {
  const notesContainer = document.getElementById("notes-container");
  notesContainer.innerHTML = ""; // Clear previous content

  data.notes.forEach((note) => {
    createAndAppendNoteElement(note, notesContainer);
  });
}

function createPaginationControls(totalPages, currentPage) {
  const paginationContainer =
    document.getElementById("pagination") || document.createElement("div");
  paginationContainer.innerHTML = ""; // Reset pagination controls
  paginationContainer.id = "pagination";

  for (let page = 1; page <= totalPages; page++) {
    const pageLink = document.createElement("button");
    pageLink.textContent = page;
    pageLink.className = "pagination-link";
    if (page === currentPage) {
      pageLink.classList.add("active");
    }

    pageLink.addEventListener("click", () => fetchNotes(page));
    paginationContainer.appendChild(pageLink);
  }

  document.body.appendChild(paginationContainer); // Append or update pagination in the document
}

function addNote(event) {
  event.preventDefault();

  const currentTime = Date.now();
  const timeSinceLastPost = (currentTime - lastPostTime) / 1000;

  if (timeSinceLastPost < 5) {
    // Reduced to 5 seconds limit
    const remainingTime = 5 - timeSinceLastPost;
    notifyUser(
      `Please wait ${remainingTime.toFixed(
        1
      )} more seconds before posting again.`,
      true
    );
    return;
  }

  lastPostTime = currentTime;

  const noteText = document.querySelector('[name="comment"]').value;
  if (!noteText.trim()) {
    notifyUser("Please enter a valid comment.", true);
    return;
  }

  const jsonData = JSON.stringify({ text: noteText });
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");

  fetch("/comments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken,
    },
    body: jsonData,
  })
    .then(responseHandler)
    .then(() => {
      fetchNotes(1); // Reload the first page to show the newly added note
      notifyUser("Comment added successfully!");
      document.getElementById("note-form").reset();
    })
    .catch((error) => {
      console.error("Error adding comment:", error);
      notifyUser("Error adding comment. Please try again.", true);
    });
}

function responseHandler(response) {
  if (!response.ok) {
    throw new Error("Network response was not ok.");
  }
  return response.json();
}

function handleFetchResponse(response) {
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  return response.json();
}

function createAndAppendNoteElement(note, container) {
  const noteElement = document.createElement("div");
  noteElement.className = "note";
  noteElement.innerHTML = `<p>${note.text}</p><small>Posted on: ${new Date(
    note.created_at
  ).toLocaleString()}</small>`;
  container.appendChild(noteElement);
}

function handleFetchError(error) {
  console.error("Error loading notes:", error);
  const notesContainer = document.getElementById("notes-container");
  notesContainer.innerHTML =
    '<div class="placeholder">Error loading notes. Please try again later.</div>';
}

function notifyUser(message, isError = false) {
  const notification = document.getElementById("notification");
  notification.textContent = message;
  notification.className = `notification ${isError ? "error" : "success"}`;
  setTimeout(() => {
    notification.className = "notification";
    notification.textContent = "";
  }, 5000);
}

document.getElementById("trackForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    let username = document.getElementById("username").value.trim();
    if (!username) return alert("Enter a valid Instagram username!");

    let response = await fetch("/track", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username })
    });

    let result = await response.json();
    alert(result.message);
    document.getElementById("username").value = "";
    loadUsers();
});

async function loadUsers() {
    let response = await fetch("/following");
    let data = await response.json();

    let userList = document.getElementById("userList");
    userList.innerHTML = "";

    data.forEach(([username, timestamp]) => {
        let li = document.createElement("li");
        li.className = "list-group-item";
        li.innerHTML = `<b>${username}</b> <span class="text-muted">(${timestamp})</span>`;
        userList.appendChild(li);
    });
}

loadUsers(); // Load tracked users on page load

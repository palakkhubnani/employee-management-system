const form = document.getElementById("employee-form");
const tableBody = document.getElementById("employee-table-body");

const databaseId = document.getElementById("database-id");
const employeeId = document.getElementById("employee-id");
const nameInput = document.getElementById("name");
const department = document.getElementById("department");
const position = document.getElementById("position");
const salary = document.getElementById("salary");
const contact = document.getElementById("contact");
const email = document.getElementById("email");

const searchInput = document.getElementById("search");
const searchButton = document.getElementById("search-button");
const showAllButton = document.getElementById("show-all-button");

const formTitle = document.getElementById("form-title");
const submitButton = document.getElementById("submit-button");
const cancelButton = document.getElementById("cancel-button");


async function loadEmployees(search = "") {
    let url = "/api/employees";

    if (search.trim() !== "") {
        url += `?search=${encodeURIComponent(search.trim())}`;
    }

    try {
        const response = await fetch(url);
        const employees = await response.json();

        tableBody.innerHTML = "";

        if (employees.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align:center;">
                        No employees found.
                    </td>
                </tr>
            `;
            return;
        }

        employees.forEach(employee => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${employee.id}</td>
                <td>${employee.employee_id}</td>
                <td>${employee.name}</td>
                <td>${employee.department}</td>
                <td>${employee.position}</td>
                <td>₹${Number(employee.salary).toFixed(2)}</td>
                <td>${employee.contact}</td>
                <td>${employee.email}</td>
                <td>
                    <button
                        class="edit-button"
                        onclick="editEmployee(${employee.id})"
                    >
                        Edit
                    </button>

                    <button
                        class="delete-button"
                        onclick="deleteEmployee(${employee.id})"
                    >
                        Delete
                    </button>
                </td>
            `;

            tableBody.appendChild(row);
        });

    } catch (error) {
        alert("Unable to load employees.");
        console.error(error);
    }
}


form.addEventListener("submit", async function(event) {
    event.preventDefault();

    const employeeData = {
        employee_id: employeeId.value.trim(),
        name: nameInput.value.trim(),
        department: department.value.trim(),
        position: position.value.trim(),
        salary: salary.value,
        contact: contact.value.trim(),
        email: email.value.trim()
    };

    const id = databaseId.value;

    try {
        let response;

        if (id) {
            response = await fetch(`/api/employees/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(employeeData)
            });
        } else {
            response = await fetch("/api/employees", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(employeeData)
            });
        }

        const result = await response.json();

        if (!response.ok) {
            alert(result.error);
            return;
        }

        alert(result.message);

        resetForm();
        loadEmployees();

    } catch (error) {
        alert("Something went wrong.");
        console.error(error);
    }
});


async function editEmployee(id) {
    try {
        const response = await fetch("/api/employees");
        const employees = await response.json();

        const employee = employees.find(emp => emp.id === id);

        if (!employee) {
            alert("Employee not found.");
            return;
        }

        databaseId.value = employee.id;
        employeeId.value = employee.employee_id;
        nameInput.value = employee.name;
        department.value = employee.department;
        position.value = employee.position;
        salary.value = employee.salary;
        contact.value = employee.contact;
        email.value = employee.email;

        formTitle.textContent = "Update Employee";
        submitButton.textContent = "Update Employee";
        cancelButton.style.display = "inline-block";

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    } catch (error) {
        alert("Unable to load employee details.");
        console.error(error);
    }
}


async function deleteEmployee(id) {
    const confirmDelete = confirm(
        "Are you sure you want to delete this employee?"
    );

    if (!confirmDelete) {
        return;
    }

    try {
        const response = await fetch(`/api/employees/${id}`, {
            method: "DELETE"
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.error);
            return;
        }

        alert(result.message);

        loadEmployees();

    } catch (error) {
        alert("Unable to delete employee.");
        console.error(error);
    }
}


function resetForm() {
    form.reset();

    databaseId.value = "";

    formTitle.textContent = "Add Employee";
    submitButton.textContent = "Add Employee";
    cancelButton.style.display = "none";
}


cancelButton.addEventListener("click", function() {
    resetForm();
});


searchButton.addEventListener("click", function() {
    loadEmployees(searchInput.value);
});


showAllButton.addEventListener("click", function() {
    searchInput.value = "";
    loadEmployees();
});


searchInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        loadEmployees(searchInput.value);
    }
});


loadEmployees();
const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("csvFile");
const status = document.getElementById("status");

uploadBtn.addEventListener("click", async () => {

    if (fileInput.files.length === 0) {
        status.innerHTML = "❌ Please select a CSV file.";
        status.style.color = "red";
        return;
    }

    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("loadingSpinner").style.display = "block";
    status.innerHTML = "Uploading...";
    status.style.color = "blue";

uploadBtn.disabled = true;

    const response = await fetch("/ingest", {
        method: "POST",
        body: formData
    });

    const result = await response.json();
    document.getElementById("summaryCards").style.display = "flex";
    document.getElementById("fileName").innerText = file.name;
    document.getElementById("rowCount").innerText = result.rows;
    document.getElementById("columnCount").innerText = result.columns.length;

    const preview = document.getElementById("preview");

preview.innerHTML = "";

if(result.preview){

    let table = "<table border='1' cellpadding='8'>";

    table += "<tr>";

    result.columns.forEach(col=>{
        table += `<th>${col}</th>`;
    });

    table += "</tr>";

    result.preview.forEach(row=>{

        table += "<tr>";

        result.columns.forEach(col=>{

            table += `<td>${row[col]}</td>`;

        });

        table += "</tr>";

    });

    table += "</table>";

   preview.innerHTML = `
   <div class="table-responsive mt-3">
   ${table}
   </div>
   `;

}

    document.getElementById("loadingSpinner").style.display = "none";
    uploadBtn.disabled = false;

    status.innerHTML = "✅ " + result.message;
    status.style.color = "green";
});

const askBtn = document.getElementById("askBtn");
const answer = document.getElementById("answer");

askBtn.addEventListener("click", async ()=>{

    const question = document.getElementById("question").value;

    const response = await fetch("/chat",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            question:question
        })
    });

    const result = await response.json();

    document.getElementById("answerCard").style.display = "block";
    answer.innerHTML = result.answer;

});
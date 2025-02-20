async function processFile() {
    let fileInput = document.getElementById("fileUpload");
    let dataType = document.getElementById("dataType").value;

    if (!fileInput.files.length) {
        alert("Please upload a file!");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("dataType", dataType);

    let response = await fetch("http://127.0.0.1:5000/process", {
        method: "POST",
        body: formData
    });

    let result = await response.json();

    if (result.error) {
        alert(result.error);
        return;
    }

    let outputDiv = document.getElementById("output");
    outputDiv.innerHTML = "<table border='1'><tr>" + result.columns.map(col => `<th>${col}</th>`).join("") + "</tr>";
    result.data.forEach(row => {
        outputDiv.innerHTML += "<tr>" + result.columns.map(col => `<td>${row[col] || ''}</td>`).join("") + "</tr>";
    });
    outputDiv.innerHTML += "</table>";

    document.getElementById("downloadCSV").style.display = "inline-block";
    document.getElementById("downloadCSV").onclick = () => downloadFile(result.csv, "data.csv");

    document.getElementById("downloadExcel").style.display = "inline-block";
    document.getElementById("downloadExcel").onclick = () => downloadFile(result.excel, "data.xlsx");
}

function downloadFile(data, filename) {
    let blob = new Blob([data], { type: "application/octet-stream" });
    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

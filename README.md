<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proyecto PDF</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto">
    <link rel="stylesheet" href="css/estilos.css">
</head>
<body>
    <h1>Procesamiento de PDF</h1>
    <input type="file" id="pdfFileInput" accept=".pdf">
    <br>
    <br>
    <label for="saldo"> Saldo Minimo:</label>
    <input type="number" id="saldo" name="saldo" placeholder="Ingrese el saldo minimo">
    <br>
    <p>
    <label for="banco" >Banco:</label>
    <select id="banco" name="banco">
        <option value="general">Banco General</option>
        <option value="banitsmo">Banitsmo</option>
        <option value="scotia">ScotiaBank</option>
        <option value="davi">Banco Davidenda</option>
    </select>
    <button id="processButton">Procesar PDF</button>
    </p>
    <div id="resultContainer"></div>

    <script>
        document.getElementById("processButton").addEventListener("click", async function() {
            const fileInput = document.getElementById("pdfFileInput");
            const file = fileInput.files[0];
            const saldoInput = document.getElementById("saldo");
            const saldo = saldoInput.value;
            
            if (file) {
                try {
                    const formData = new FormData();
                    formData.append("file", file);
                    formData.append("saldo", saldo);

                    const response = await fetch("http://localhost:5000/tabulate_pdf", {
                        method: "POST",
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error(`Error en la llamada a la API: ${response.status} ${response.statusText}`);
                    }

                    const result = await response.json();
                    const resultContainer = document.getElementById("resultContainer");
                    resultContainer.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
                } catch (error) {
                    const resultContainer = document.getElementById("resultContainer");
                    resultContainer.innerHTML = `Error: ${error.message}`;
                }
            } else {
                console.log("Por favor, selecciona un archivo PDF.");
            }
        });
    </script>
</body>
</html>

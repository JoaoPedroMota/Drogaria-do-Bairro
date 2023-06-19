var canvasElement = document.createElementById("grafico");

var config = {
    type: "bar",
    data: {
        labels: ["Freguesias", "Cidades", "Países", "Continentes", "Resto do Mundo"],
        datasets: [
            {
            label: "Impacto Local",
            
            backgroundColor: [
                "rgba(255, 155, 64, 0.2)", // laranja
                "rgba(255, 99, 132, 0.2)", // vermelho
                "rgba(54, 162, 235, 0.2)", // azul
                "rgba(75, 192, 192, 0.2)", // verde
                "rgba(153, 102, 255, 0.2)", // roxo
            ],
            borderColor: 
                [                
                "rgba(255, 155, 64, 0.2)", // laranja
                "rgba(255, 99, 132, 0.2)", // vermelho
                "rgba(54, 162, 235, 0.2)", // azul
                "rgba(75, 192, 192, 0.2)", // verde
                "rgba(153, 102, 255, 0.2)", // roxo
                ],
            borderWidth: 1,
            }
        ],
    },
    };

var graficoImpactoLocal = new Chart(canvasElement, config);

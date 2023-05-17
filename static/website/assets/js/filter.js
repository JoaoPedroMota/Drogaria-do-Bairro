function atualizarPreco(input, preco) {
  var valor = input.value;
  var novoPreco = valor * preco;
  var precoElement = input.parentNode.querySelector('.preco');
  precoElement.innerText = novoPreco.toFixed(2) + "€";
}

function alterarParaMaximo(input){
  let numero = parseFloat(input.value)

  if (numero > input.max){
    numero = parseFloat(input.max);
  }
  input.value = isNaN(numero) ? '' : numero;
}



function atualizarNumero(input) {
  // Remove espaços em branco
  input.value = input.value.trim();

  // Remove caracteres não numéricos, exceto ponto e vírgula
  input.value = input.value.replace(/[^0-9.,]/g, '');

  // Substitui a vírgula por ponto
  input.value = input.value.replace(',', '.');

  // Converte para número
  let numero = parseFloat(input.value);


  if (numero > input.max) {
    numero = parseFloat(input.max);
  }

  // Arredonda para o número inteiro mais próximo
  numero = Math.round(numero);

  // Define o valor do campo como o número arredondado
  input.value = isNaN(numero) ? '' : numero;
}


// Seleciona o elemento h4
const descricao = document.querySelector('h3');

// Adiciona um ouvinte de eventos ao elemento h4
descricao.addEventListener('click', function() {
    // Seleciona a div com mais informações
    const maisInfo = document.querySelector('.mais-informacao');
    
    // Se a div estiver oculta, mostra; senão, oculta
    if (maisInfo.style.display === 'none') {
        maisInfo.style.display = 'block';
    } else {
        maisInfo.style.display = 'none';
    }
});

// Seleciona o elemento h4
const descricaoToggle = document.querySelector('.descricao-toggle');

// Adiciona um ouvinte de eventos ao elemento h4
descricaoToggle.addEventListener('click', function() {
    // Seleciona a div com mais informações
    const maisInfo = document.querySelector('.mais-informacao');

    // Alterna a classe expandido no elemento h4
    descricaoToggle.classList.toggle('expandido');

    // Se a div estiver oculta, mostra; senão, oculta
    if (maisInfo.style.display === 'none') {
        maisInfo.style.display = 'block';
    } else {
        maisInfo.style.display = 'none';
    }
});
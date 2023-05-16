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
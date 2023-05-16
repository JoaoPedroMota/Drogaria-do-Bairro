function atualizarPreco(input, preco) {
  var valor = input.value;
  var novoPreco = valor * preco;
  var precoElement = input.parentNode.querySelector('.preco');
  precoElement.innerText = novoPreco.toFixed(2) + "€";
}
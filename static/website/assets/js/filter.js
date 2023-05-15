const searchBox = document.getElementById('searchBox-1');
searchBox.addEventListener('input', filterProducts);

function filterProducts() {
  const searchTerm = searchBox.value.toLowerCase();

  const productItems = document.querySelectorAll('.single-product-item');

  productItems.forEach((productItem) => {
    const productNameElement = productItem.querySelector('h3');
    const productName = productNameElement.textContent.toLowerCase();

    if (productName.includes(searchTerm)) {
      productItem.style.display = 'block';
    } else {
      productItem.style.display = 'none';
    }
  });

  const productLists = document.querySelector('.product-lists');
  const visibleProductItems = productLists.querySelectorAll('.single-product-item[style="display: block;"]');
  
  if (visibleProductItems.length > 0) {
    productLists.style.display = 'flex';
  } else {
    productLists.style.display = 'none';
  }
}
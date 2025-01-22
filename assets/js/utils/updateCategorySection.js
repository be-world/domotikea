import { filterProductsByCategories } from "./filterProductsByCategories.js";

export async function updateCategorySection({
  sectionId,
  categoryTitle,
  categorySubtitle,
  categories,
  mode,
}) {
  const section = document.getElementById(sectionId);
  if (!section) {
    console.error(`Section with ID '${sectionId}' not found.`);
    return;
  }

  section.innerHTML = `
        <div class="container">
            <div class="row">
                <div class="col-lg-6">
                    <div class="section-heading">
                        <h2 id="${sectionId}">${categoryTitle}</h2>
                        <span>${categorySubtitle}</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="container">
            <div id="${sectionId}-product-list" class="row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xxl-4 g-4"></div>
        </div>
    `;

  const filteredProducts = await filterProductsByCategories(categories, mode);
  const productContainer = document.getElementById(`${sectionId}-product-list`);
  productContainer.innerHTML = "";

  filteredProducts.forEach((product) => {
    const productElement = document.createElement("div");
    productElement.classList.add("col");
    productElement.innerHTML = `
            <div class="item">
                <img src="${
                  product.gallery.find((photo) => photo.main)?.urlS3 ||
                  product.gallery[0]?.urlS3 ||
                  ""
                }" alt="${product.name}" />
                <div class="down-content">
                    <h4>${product.name}</h4>
                    <span>${product.price.toLocaleString()}</span>
                    <a href="single-product.html?id=${
                      product.id
                    }">Ver detalles</a>
                </div>
            </div>
        `;
    productContainer.appendChild(productElement);
  });
}

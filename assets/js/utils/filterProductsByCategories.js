export async function filterProductsByCategories(categories, mode = "union") {
  try {
    const response = await fetch(
      `data/products.json?t=${new Date().getTime()}`
    );
    const data = await response.json();
    const products = Object.values(data);

    return products.filter((product) => {
      const productCategories = product.categories || [];

      if (mode === "intersection") {
        return categories.every((category) =>
          productCategories.includes(category)
        );
      } else {
        return categories.some((category) =>
          productCategories.includes(category)
        );
      }
    });
  } catch (error) {
    console.error("Error filtering products:", error);
    return [];
  }
}

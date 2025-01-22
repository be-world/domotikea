export var CATEGORIES = {
  kitchen: "kitchen",
  smart_home: "smart_home",
  cleaning: "cleaning",
  illumination: "illumination",
  wellness: "wellness",
  house_tools: "house_tools",
  gifts: "gifts",
  top_seller: "top_seller",
};

export var CATEGORIES_DATA = {
  [CATEGORIES.kitchen]: {
    categoryTitle: "Cocina",
    categorySubtitle: "Que rico, yummy!",
    categories: ["kitchen"],
  },
  [CATEGORIES.smart_home]: {
    categoryTitle: "Domotica",
    categorySubtitle: "Domotica",
    categories: ["smart_home"],
  },
  [CATEGORIES.cleaning]: {
    categoryTitle: "Aseo",
    categorySubtitle: "Aseo",
    categories: ["cleaning"],
  },
  [CATEGORIES.illumination]: {
    categoryTitle: "Iluminacion",
    categorySubtitle: "Iluminacion",
    categories: ["illumination"],
  },
  [CATEGORIES.wellness]: {
    categoryTitle: "Bienestar",
    categorySubtitle: "Bienestar",
    categories: ["wellness"],
  },
  [CATEGORIES.house_tools]: {
    categoryTitle: "Herramientas",
    categorySubtitle: "Herramientas",
    categories: ["house_tools"],
  },
  [CATEGORIES.gifts]: {
    categoryTitle: "Regalos",
    categorySubtitle: "Regalos",
    categories: ["gifts"],
  },
  [CATEGORIES.top_seller]: {
    categoryTitle: "Lo mas vendido",
    categorySubtitle: "Lo mas vendido",
    categories: ["top_seller"],
  },
  all_products: {
    categoryTitle: "Todos los productos",
    categorySubtitle: "Todos los productos",
    categories: Object.values(CATEGORIES),
  },
};

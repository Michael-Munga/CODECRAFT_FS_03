import ProductsCard from "@/components/project-components/ProductCard";

const sampleProducts = [
  {
    name: "Retro Leather Jacket",
    description: "Classic brown leather jacket.",
    price: "$120",
    image:
      "https://i.pinimg.com/1200x/0b/81/5e/0b815e775d917bd15b5bc21b3ea5840b.jpg",
  },
  {
    name: "Vintage Denim Skirt",
    description: "High-waist blue denim skirt.",
    price: "$45",
    image:
      "https://i.pinimg.com/1200x/21/3c/ea/213cea7b7b7860b746d979d07ff05d90.jpg",
  },
  {
    name: "Retro Sunglasses",
    description: "Round frame sunglasses from the 80s.",
    price: "$25",
    image:
      "https://i.pinimg.com/1200x/0f/2b/58/0f2b58cb5ab3a1352d3335b81b2440a3.jpg",
  },
  {
    name: "Classic Wool Coat",
    description: "Elegant wool coat for winter fashion.",
    price: "$150",
    image:
      "https://i.pinimg.com/1200x/8a/a9/53/8aa953379a4cac21f3c2fe975eeab236.jpg",
  },
  {
    name: "Vintage Plaid Shirt",
    description: "Comfortable cotton plaid shirt.",
    price: "$35",
    image:
      "https://i.pinimg.com/1200x/2b/c8/51/2bc85157bd24da514b908a7ef801f19e.jpg",
  },
  {
    name: "Retro Sneakers",
    description: "Classic white sneakers from the 90s.",
    price: "$60",
    image:
      "https://i.pinimg.com/1200x/6c/20/fe/6c20fe13bd22e3681dfb5c4632b658bf.jpg",
  },
  {
    name: "Vintage Fedora Hat",
    description: "Stylish fedora hat for a retro look.",
    price: "$30",
    image:
      "https://i.pinimg.com/1200x/ba/d5/b7/bad5b794d6b9b98153ebe227d8cbef53.jpg",
  },
  {
    name: "Retro Leather Boots",
    description: "High-quality brown leather boots.",
    price: "$110",
    image:
      "https://i.pinimg.com/1200x/3b/b1/de/3bb1dea3e867be2ebf6db18be806af5c.jpg",
  },
  {
    name: "Vintage Knit Sweater",
    description: "Soft cozy sweater for autumn days.",
    price: "$55",
    image:
      "https://i.pinimg.com/1200x/08/6f/22/086f22b4b78bca51a24e2509e1bd4c84.jpg",
  },
  {
    name: "Retro Backpack",
    description: "Canvas backpack with classic design.",
    price: "$40",
    image:
      "https://i.pinimg.com/736x/1f/8a/f6/1f8af6439f73a647a236850160aba7e4.jpg",
  },
  {
    name: "Vintage Belt",
    description: "Leather belt with brass buckle.",
    price: "$20",
    image:
      "https://i.pinimg.com/1200x/06/af/d1/06afd1b2780a786034e277131561e117.jpg",
  },
  {
    name: "Retro Watch",
    description: "Classic analog watch with leather strap.",
    price: "$80",
    image:
      "https://i.pinimg.com/1200x/d7/89/c2/d789c2fc78b6503fde52069e7eed22c6.jpg",
  },
];

// Shuffle products 
const randomProducts = sampleProducts.sort(() => 0.5 - Math.random());

export default function ProductsPage() {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-stone-900">
        Vintage Products
      </h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {randomProducts.map((product) => (
          <ProductsCard key={product.name} product={product} />
        ))}
      </div>
    </div>
  );
}

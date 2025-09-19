import ProductsCard from "@/components/project-components/ProductCard";
import sampleProducts from "@/Data/Products";
import useCart from "@/hooks/useCart";
// Shuffle products 
const randomProducts = sampleProducts.sort(() => 0.5 - Math.random());

export default function ProductsPage() {

   const { addToCart } = useCart(); 
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-5xl font-bold mb-6 text-amber-900 smokum">
        Vintage Products
      </h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {randomProducts.map((product) => (
          <ProductsCard
            key={product.name}
            product={product}
            addToCart={addToCart}
          />
        ))}
      </div>
    </div>
  );
}

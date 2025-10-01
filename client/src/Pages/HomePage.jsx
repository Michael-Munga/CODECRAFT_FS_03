import React from "react";
import TasteCardGrid from "@/components/project-components/TasteCardGrid";
import api from "@/services/api";
import ProductCard from "@/components/project-components/ProductCard";
import { useState, useEffect } from "react";
import useCart from "@/hooks/useCart";

export default function HomePage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { addToCart } = useCart();
  const bestSellers = products.slice(0, 4);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await api.get("/products");
        setProducts(res.data);
      } catch (err) {
        console.error(err);
        setError("Failed to load products.");
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) {
    return <p className="text-center text-lg">Loading products...</p>;
  }

  if (error) {
    return <p className="text-center text-red-600">{error}</p>;
  }

  return (
    <div className="flex flex-col items-center min-h-screen p-6">
      {/* Text content */}
      <div className="text-center">
        <h1 className="text-6xl font-bold text-amber-800 vint">
          Welcome to The Vintage Closet
        </h1>
        <h1 className="text-6xl font-bold text-rose-950 smokum">
          One Brand Unlimited Quality
        </h1>
        <p className="mt-2 text-3xl felipa">
          Step into timeless fashion and explore curated outfits, exclusive
          drops, and retro finds.
        </p>
      </div>

      {/* <div className="mt-6 flex justify-center w-full">
        <div className="h-20 w-2/3 bg-gradient-to-r from-amber-700 via-rose-700 to-stone-800 rounded-4xl flex items-center justify-center">
          <h1 className="text-4xl rocker text-white">A Taste Of Quality</h1>
        </div>
      </div> */}

      <TasteCardGrid />
      {/* Best Seller section */}
      <div className="mt-20 flex justify-center w-full">
        <h1 className="text-6xl font-bold text-rose-950 smokum">Best Seller</h1>
      </div>

      {/* Best Seller products */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 w-full max-w-7xl">
        {bestSellers.map((product) => (
          <ProductCard
            key={product.name}
            product={product}
            addToCart={addToCart}
          />
        ))}
      </div>
    </div>
  );
}

import { ShoppingCart } from "lucide-react";
import { Link } from "react-router-dom";
import useCart from "@/hooks/useCart";

export default function CartPage() {
  const { cart, increaseQty, decreaseQty } = useCart();
  const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {cart.length === 0 ? (
        // Empty cart state
        <div className="flex flex-col items-center justify-center py-20 text-stone-600">
          <ShoppingCart size={48} className="text-amber-600 mb-4" />
          <p className="text-lg font-medium oswald mb-4">Your cart is empty</p>
          <Link
            to="/products"
            className="bg-amber-700 hover:bg-amber-600 text-white px-6 py-2 rounded-lg font-medium shadow transition-colors"
          >
            Continue Shopping
          </Link>
        </div>
      ) : (
        // When cart has items
        <div className="space-y-6">
          {cart.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between border-b pb-4"
            >
              {/* Product Info (Left) */}
              <div className="flex items-center gap-4 flex-1">
                <img
                  src={item.image}
                  alt={item.name}
                  className="w-20 h-20 object-cover rounded-lg"
                />
                <div>
                  <h2 className="font-semibold text-lg">{item.name}</h2>
                  <p className="text-stone-600">${item.price}</p>
                </div>
              </div>

              {/* Quantity Controls (Center) */}
              <div className="flex items-center gap-3 flex-1 justify-center">
                <button
                  onClick={() => decreaseQty(item.id)}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                >
                  −
                </button>
                <span className="text-lg font-medium">{item.qty}</span>
                <button
                  onClick={() => increaseQty(item.id)}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                >
                  +
                </button>
              </div>

              {/* Subtotal*/}
              <div className="flex-1 text-right">
                <p className="font-semibold text-stone-800">
                  ${item.qty * item.price}
                </p>
              </div>
            </div>
          ))}

          {/* Total & Checkout */}
          <div className="flex flex-col items-end mt-6 space-y-4">
            <div className="flex justify-between w-full text-xl font-bold">
              <span>Total:</span>
              <span>${total}</span>
            </div>
            <button className="bg-amber-700 hover:bg-amber-600 text-white px-6 py-3 rounded-lg font-medium shadow transition-colors">
              Proceed to Checkout
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

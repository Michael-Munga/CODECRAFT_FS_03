import { createContext, useState, useEffect } from "react";
import api from "@/services/api";
import { toast } from "sonner";

export const CartContext = createContext();

export function CartProvider({ children }) {
  const [cart, setCart] = useState([]);

  // Load cart from API on mount
  useEffect(() => {
    const fetchCart = async () => {
      try {
        const res = await api.get("/cart");
        const items = res.data.items.map((item) => ({
          id: item.id,
          productId: item.product_id,
          name: item.product_name,
          price: item.product_price,
          qty: item.quantity,
          image: item.product_image,
        }));
        setCart(items);
      } catch (err) {
        console.warn("Failed to fetch cart:", err);
      }

    };
    fetchCart();
  }, []);

  // Add a product to the cart
  const addToCart = async (product) => {
    try {
      const res = await api.post("/cart", {
        product_id: product.id,
        quantity: 1,
      });

      const item = res.data;

      setCart((prev) => {
        const exists = prev.find((i) => i.productId === item.product_id);

        if (exists) {
          const updated = prev.map((i) =>
            i.productId === item.product_id ? { ...i, qty: item.quantity } : i
          );

          // success toast
          toast.success(`${item.product_name} quantity updated in your cart.`, {
            style: {
              background: "white",
              color: "#d97706",
              borderRadius: "12px",
              fontFamily: "Oswald, sans-serif",
            },
            duration: 3000,
          });

          return updated;
        } else {
          // add new cart item
          const newItem = {
            id: item.id,
            productId: item.product_id,
            name: item.product_name,
            price: item.product_price,
            qty: item.quantity,
            image: item.product_image,
          };

          // success toast
          toast.success(`${item.product_name} added to cart.`, {
            style: {
              background: "white",
              color: "#d97706",
              borderRadius: "12px",
              fontFamily: "Oswald, sans-serif",
            },
            duration: 3000,
          });

          return [...prev, newItem];
        }
      });
    } catch (err) {
      console.error("Add to cart failed:", err);
      toast.error(
        err.response?.data?.message ||
          err.response?.data?.error ||
          "Failed to add to cart",
        {
          style: {
            background: "white",
            color: "#d97706",
            borderRadius: "12px",
            fontFamily: "Oswald, sans-serif",
          },
          duration: 4000,
        }
      );
    }
  };

  // Increase quantity --> CartItem ID
  const increaseQty = async (cartItemId) => {
    try {
      const item = cart.find((i) => i.id === cartItemId);
      if (!item) return;

      const res = await api.patch(`/cart/item/${cartItemId}`, {
        quantity: item.qty + 1,
      });

      // update local cart
      setCart((prev) =>
        prev.map((i) =>
          i.id === cartItemId ? { ...i, qty: res.data.quantity } : i
        )
      );

      toast.success("Quantity updated.", {
        style: {
          background: "white",
          color: "#d97706",
          borderRadius: "12px",
          fontFamily: "Oswald, sans-serif",
        },
        duration: 2200,
      });
    } catch (err) {
      console.error("Increase qty failed:", err);
      toast.error(
        err.response?.data?.message || "Failed to update quantity. Try again.",
        {
          style: {
            background: "white",
            color: "#d97706",
            borderRadius: "12px",
            fontFamily: "Oswald, sans-serif",
          },
          duration: 3500,
        }
      );
    }
  };

  // Decrease quantity --> CartItem ID
  const decreaseQty = async (cartItemId) => {
    try {
      const item = cart.find((i) => i.id === cartItemId);
      if (!item) return;

      if (item.qty <= 1) {
        toast.error("Minimum quantity is 1. Remove the item to delete it.", {
          style: {
            background: "white",
            color: "#d97706",
            borderRadius: "12px",
            fontFamily: "Oswald, sans-serif",
          },
          duration: 3000,
        });
        return;
      }

      const res = await api.patch(`/cart/item/${cartItemId}`, {
        quantity: item.qty - 1,
      });

      setCart((prev) =>
        prev.map((i) =>
          i.id === cartItemId ? { ...i, qty: res.data.quantity } : i
        )
      );

      toast.success("Quantity updated.", {
        style: {
          background: "white",
          color: "#d97706",
          borderRadius: "12px",
          fontFamily: "Oswald, sans-serif",
        },
        duration: 2200,
      });
    } catch (err) {
      console.error("Decrease qty failed:", err);
      toast.error(
        err.response?.data?.message || "Failed to update quantity. Try again.",
        {
          style: {
            background: "white",
            color: "#d97706",
            borderRadius: "12px",
            fontFamily: "Oswald, sans-serif",
          },
          duration: 3500,
        }
      );
    }
  };

  // Remove a product from the cart --> CartItem ID
  const removeFromCart = async (cartItemId) => {
    try {
      await api.delete(`/cart/item/${cartItemId}`);

      setCart((prev) => prev.filter((i) => i.id !== cartItemId));

      toast.success("Item removed from cart.", {
        style: {
          background: "white",
          color: "#d97706",
          borderRadius: "12px",
          fontFamily: "Oswald, sans-serif",
        },
        duration: 2500,
      });
    } catch (err) {
      console.error("Remove from cart failed:", err);
      toast.error(
        err.response?.data?.message || "Failed to remove item from cart.",
        {
          style: {
            background: "white",
            color: "#d97706",
            borderRadius: "12px",
            fontFamily: "Oswald, sans-serif",
          },
          duration: 3500,
        }
      );
    }
  };

  return (
    <CartContext.Provider
      value={{ cart, addToCart, increaseQty, decreaseQty, removeFromCart }}
    >
      {children}
    </CartContext.Provider>
  );
}

import React, { useEffect, useState } from "react";
import {
  ShoppingCart,
  Package,
  Users,
  DollarSign,
  TrendingUp,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "@/services/api";
import { toast } from "sonner";

export default function AdminMainContent() {
  const navigate = useNavigate();
  const [productCount, setProductCount] = useState(0);

  useEffect(() => {
    async function fetchProductCount() {
      try {
        const res = await api.get("/admin/products");
        setProductCount(res.data.length);
      } catch (err) {
        console.error(err);
        toast.error("Failed to load product count");
      }
    }
    fetchProductCount();
  }, []);

  const stats = [
    {
      title: "Total Sales",
      value: "$12,456",
      subtitle: "+20.1% from last month",
      icon: DollarSign,
    },
    {
      title: "Orders",
      value: "145",
      subtitle: "+12 new orders",
      icon: ShoppingCart,
    },
    {
      title: "Products",
      value: productCount.toString(),
      subtitle: "Total active products",
      icon: Package,
      route: "/admin/products",
    },
    {
      title: "Customers",
      value: "432",
      subtitle: "+18 this week",
      icon: Users,
    },
  ];

  const orders = [
    {
      name: "Emma Wilson",
      item: "Vintage Denim Jacket",
      id: "ORD-105",
      price: "$89.99",
      status: "completed",
    },
    {
      name: "Michael Chen",
      item: "Retro Leather Boots",
      id: "ORD-104",
      price: "$156.50",
      status: "processing",
    },
    {
      name: "Sarah Johnson",
      item: "Classic Wool Coat",
      id: "ORD-103",
      price: "$245.00",
      status: "completed",
    },
    {
      name: "David Brown",
      item: "Vintage Band Tee",
      id: "ORD-102",
      price: "$45.99",
      status: "pending",
    },
  ];

  const products = [
    {
      rank: 1,
      name: "Vintage Leather Jacket",
      sales: "45 sales",
      price: "$4,050",
      growth: "+12%",
    },
    {
      rank: 2,
      name: "Retro Sunglasses",
      sales: "38 sales",
      price: "$1,520",
      growth: "+8%",
    },
    {
      rank: 3,
      name: "Classic Denim Jeans",
      sales: "32 sales",
      price: "$2,880",
      growth: "+15%",
    },
    {
      rank: 4,
      name: "Vintage Handbag",
      sales: "28 sales",
      price: "$3,360",
      growth: "+5%",
    },
  ];

  return (
    <main className="bg-[#f5f0eb] min-h-screen px-8 py-6 text-[#3b3b3b]">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold">Dashboard</h1>
        <p className="text-sm text-[#7a6b5b]">
          Welcome to your vintage shop admin panel
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, idx) => (
          <div
            key={idx}
            onClick={() => stat.route && navigate(stat.route)}
            className="bg-[#fffaf5] rounded-lg border border-[#e2d7c6] p-5 shadow-sm"
          >
            <div className="flex justify-between items-center mb-2">
              <span className="text-[#7a6b5b] font-medium">{stat.title}</span>
              <stat.icon className="w-5 h-5 text-[#b08b58]" />
            </div>
            <h2 className="text-2xl font-semibold">{stat.value}</h2>
            <p className="text-xs text-[#7a6b5b]">{stat.subtitle}</p>
          </div>
        ))}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recent Orders */}
        <div className="bg-[#fffaf5] rounded-lg border border-[#e2d7c6] p-5 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Recent Orders</h3>

          <div className="divide-y divide-[#efe4d3] text-sm">
            {orders.map((order, idx) => (
              <div key={idx} className="flex justify-between items-center py-3">
                <div>
                  <p className="font-medium">{order.name}</p>
                  <p className="text-[#7a6b5b]">{order.item}</p>
                  <p className="text-xs text-[#9b8b7a]">{order.id}</p>
                </div>
                <div className="text-right">
                  <p className="font-medium">{order.price}</p>
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      order.status === "completed"
                        ? "bg-green-100 text-green-700"
                        : order.status === "processing"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {order.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Popular Products */}
        <div className="bg-[#fffaf5] rounded-lg border border-[#e2d7c6] p-5 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Popular Products</h3>

          <div className="divide-y divide-[#efe4d3] text-sm">
            {products.map((product, idx) => (
              <div key={idx} className="flex justify-between items-center py-3">
                <div className="flex items-center gap-3">
                  <span className="text-[#b08b58] font-semibold">
                    #{product.rank}
                  </span>
                  <div>
                    <p className="font-medium">{product.name}</p>
                    <p className="text-xs text-[#7a6b5b]">{product.sales}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium">{product.price}</p>
                  <p className="text-xs text-green-700 flex items-center justify-end gap-1">
                    <TrendingUp className="w-3 h-3" />
                    {product.growth}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}

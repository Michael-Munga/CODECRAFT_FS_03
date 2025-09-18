import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ShoppingCart } from "lucide-react";

export default function ProductCard({ product }) {
  return (
    <Card className="bg-white  border-amber-200 rounded-xl hover:shadow-lg hover:scale-[1.015] transition-all duration-300 ease-in-out">
      {/* Product Image */}
      <div className=" px-1.5  h-64 overflow-hidden rounded-lg">
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Header with title and description */}
      <CardHeader className="p-4">
        <CardTitle className="text-lg font-semibold text-stone-900">
          {product.name}
        </CardTitle>
        <CardDescription className="text-sm text-stone-600 mt-1">
          {product.description}
        </CardDescription>
      </CardHeader>

      {/* Card Content */}
      <CardContent className="p-4">
        <p className="text-md font-bold text-stone-800">{product.price}</p>
      </CardContent>

      {/* Footer with Add to Cart button */}
      <CardFooter className="p-4">
        <CardAction className="w-full">
          <button className="w-full flex items-center justify-center gap-2 bg-amber-700 hover:bg-amber-600 text-white py-2 px-4 rounded-lg transition-colors">
            <ShoppingCart className="h-5 w-5" />
            Add to Cart
          </button>
        </CardAction>
      </CardFooter>
    </Card>
  );
}

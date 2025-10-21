import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import api from "@/services/api";

export default function EditProductDialog({ product, onUpdate }) {
  const [open, setOpen] = useState(false);
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    name: product.name,
    price: product.price,
    stock: product.stock,
    image_url: product.image_url || "",
    description: product.description || "",
    category_id: product.category?.id || "",
  });
  useEffect(() => {
    if (open) {
      fetchCategories();
    }
  }, [open]);

  const fetchCategories = async () => {
    try {
      const res = await api.get("/admin/categories");
      setCategories(res.data);
    } catch (err) {
      console.error(err);
      toast.error("Failed to load categories.");
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    if (formData.price < 0 || formData.stock < 0) {
      toast.error("Price and stock must be positive numbers.");
      return;
    }

    try {
      const res = await api.put(`/admin/products/${product.id}`, formData);
      toast.success("Product updated successfully!");
      onUpdate(product.id, res.data.product);
      setOpen(false);
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.error || "Failed to update product.");
    }
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setOpen(true)}
        className="flex items-center gap-1 text-blue-600"
      >
        Edit
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Product</DialogTitle>
          </DialogHeader>

          <div className="grid gap-4 py-2">
            <div>
              <Label>Name</Label>
              <Input
                name="name"
                value={formData.name}
                onChange={handleChange}
              />
            </div>

            <div>
              <Label>Category</Label>
              <select
                name="category_id"
                value={formData.category_id}
                onChange={handleChange}
                className="border rounded-md p-2 w-full"
              >
                <option value="">Select a category</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label>Price</Label>
              <Input
                name="price"
                type="number"
                min="0"
                step="0.01"
                value={formData.price}
                onChange={handleChange}
              />
            </div>

            <div>
              <Label>Stock</Label>
              <Input
                name="stock"
                type="number"
                min="0"
                step="1"
                value={formData.stock}
                onChange={handleChange}
              />
            </div>

            <div>
              <Label>Image URL</Label>
              <Input
                name="image_url"
                value={formData.image_url}
                onChange={handleChange}
              />
              {formData.image_url && (
                <img
                  src={formData.image_url}
                  alt="Preview"
                  className="w-24 h-24 object-cover rounded-md mt-2 border"
                />
              )}
            </div>

            <div>
              <Label>Description</Label>
              <Input
                name="description"
                value={formData.description}
                onChange={handleChange}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

import { useEffect, useState } from "react";
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { ChevronDownIcon, ChevronUpIcon, Pencil, Trash } from "lucide-react";
import { toast } from "sonner";
import api from "@/services/api";
import { cn } from "@/lib/utils";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import ConfirmDialog from "@/components/common/ConfirmDialog";

export default function AdminProducts() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sorting, setSorting] = useState([]);

  useEffect(() => {
    async function fetchProducts() {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get("/admin/products");
        setData(res.data);
      } catch (err) {
        console.error(err);
        setError(err.response?.data?.message || "Failed to load products.");
        toast.error("Error fetching products.");
      } finally {
        setLoading(false);
      }
    }
    fetchProducts();
  }, []);

  const handleDelete = async (id) => {
    try {
      await api.delete(`/admin/products/${id}`);
      toast.success("Product deleted successfully!");
      setData((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.message || "Failed to delete product.");
    }
  };

  const columns = [
    {
      header: "Image",
      accessorKey: "image_url",
      cell: ({ row }) => {
        const imageUrl = row.getValue("image_url") || "/placeholder.png";
        return (
          <Dialog>
            <DialogTrigger asChild>
              <img
                src={imageUrl}
                alt={row.original.name}
                className="w-14 h-14 object-cover rounded-md border cursor-pointer hover:opacity-80 transition"
              />
            </DialogTrigger>
            <DialogContent className="max-w-xl p-4 bg-white rounded-xl shadow-lg">
              <img
                src={imageUrl}
                alt={row.original.name}
                className="w-full h-auto rounded-lg object-contain"
              />
              <p className="text-center text-gray-700 mt-2">
                {row.original.name}
              </p>
            </DialogContent>
          </Dialog>
        );
      },
    },
    {
      header: "Name",
      accessorKey: "name",
      cell: ({ row }) => (
        <div className="font-medium truncate">{row.getValue("name")}</div>
      ),
    },
    {
      header: "Category",
      accessorKey: "category.name",
      cell: ({ row }) => (
        <span>{row.original.category?.name || "Uncategorized"}</span>
      ),
    },
    {
      header: "Price",
      accessorKey: "price",
      cell: ({ row }) => {
        const price = parseFloat(row.getValue("price"));
        return (
          <span>
            {new Intl.NumberFormat("en-US", {
              style: "currency",
              currency: "USD",
            }).format(price)}
          </span>
        );
      },
    },
    {
      header: "Stock",
      accessorKey: "stock",
      cell: ({ row }) => {
        const stock = row.getValue("stock");
        return (
          <span
            className={cn(
              "font-medium",
              stock < 5
                ? "text-red-500"
                : stock < 10
                ? "text-yellow-600"
                : "text-green-700"
            )}
          >
            {stock}
          </span>
        );
      },
    },
    {
      header: "Created",
      accessorKey: "created_at",
      cell: ({ row }) => {
        const date = new Date(row.getValue("created_at"));
        return <span>{date.toLocaleDateString()}</span>;
      },
    },
    {
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex gap-3">
          <button
            onClick={() => toast.info("Edit coming soon...")}
            className="text-blue-600 hover:underline flex items-center gap-1"
          >
            <Pencil size={14} /> Edit
          </button>

          <ConfirmDialog
            title="Delete Product"
            message="Are you sure you want to delete this product? This action cannot be undone."
            onConfirm={() => handleDelete(row.original.id)}
          />
        </div>
      ),
    },
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: { sorting },
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Loading products...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-red-600">
        <p className="font-medium mb-2">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="text-blue-600 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 bg-[#fdfaf7] rounded-xl border border-[#e8ddcf] shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold text-[#3b3b3b]">Products</h1>
        <button
          onClick={() => toast.info("Add product form coming soon...")}
          className="bg-[#b08b58] text-white px-4 py-2 rounded-md hover:bg-[#9c7b4f] transition"
        >
          + Add Product
        </button>
      </div>

      <Table className="table-fixed">
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id} className="bg-muted/50">
              {headerGroup.headers.map((header) => (
                <TableHead
                  key={header.id}
                  className="relative h-10 border-t select-none"
                >
                  <div
                    className={cn(
                      header.column.getCanSort() &&
                        "flex h-full cursor-pointer items-center justify-between gap-2"
                    )}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <span>
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                    </span>
                    {{
                      asc: <ChevronUpIcon className="opacity-60" size={16} />,
                      desc: (
                        <ChevronDownIcon className="opacity-60" size={16} />
                      ),
                    }[header.column.getIsSorted()] ?? null}
                  </div>
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>

        <TableBody>
          {table.getRowModel().rows.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id} className="truncate">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell
                colSpan={columns.length}
                className="h-24 text-center text-gray-500"
              >
                No products found.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}

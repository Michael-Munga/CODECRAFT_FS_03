import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

export default function ConfirmDialog({ onConfirm, title, message }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        variant="destructive"
        size="sm"
        onClick={() => setOpen(true)}
        className="flex items-center gap-1 text-sm"
      >
        Delete
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{title || "Confirm Delete"}</DialogTitle>
          </DialogHeader>

          <p className="text-gray-600">
            {message || "Are you sure you want to delete this item?"}
          </p>

          <DialogFooter className="mt-4 flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                onConfirm();
                setOpen(false);
              }}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

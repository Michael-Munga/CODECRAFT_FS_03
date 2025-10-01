import { motion } from "framer-motion";
import React from "react";

const newArrivals = [
  {
    title: "Hoodies",
    img: "https://i.pinimg.com/1200x/c0/ef/70/c0ef7067d94118e5520134cf40da63da.jpg",
  },
  {
    title: "Sneakers",
    img: "https://i.pinimg.com/1200x/15/a0/d2/15a0d2d8832b97d700de1e95aa73ec83.jpg",
  },
  {
    title: "Hand Bags",
    img: "https://i.pinimg.com/736x/46/15/7b/46157bbf9c9f657b5f9c5f00b8655f0c.jpg",
  },
  {
    title: "Jackets",
    img: "https://i.pinimg.com/1200x/5b/61/5b/5b615ba45b918f582f041e7725b87ebc.jpg",
  },
];

export default function NewArrivals() {
  return (
    <div className="w-full px-6 py-10">
      <h2 className="mb-6 text-center text-6xl font-bold text-rose-950 smokum">
        New Arrivals
      </h2>

      <div className="flex justify-center">
        <div className="flex gap-8 flex-wrap justify-center">
          {newArrivals.map((item, index) => (
            <motion.div
              key={index}
              className="relative flex-shrink-0 w-72 h-[28rem] rounded-2xl shadow-lg overflow-hidden cursor-pointer"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              whileHover={{ scale: 1.05 }}
            >
              <motion.img
                src={item.img}
                alt={item.title}
                className="w-full h-full object-cover"
                whileHover={{ scale: 1.1 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
              />

              {/* Title Overlay */}
              <div className="absolute bottom-0 left-0 w-full bg-black/60 py-3 text-center">
                <h3 className="text-xl font-semibold text-white">
                  {item.title}
                </h3>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

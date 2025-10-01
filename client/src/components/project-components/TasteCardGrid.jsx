import { motion, AnimatePresence } from "framer-motion";
import React, { useState } from "react";

const categories = [
  {
    title: "Denim",
    img: "https://i.pinimg.com/1200x/3e/52/aa/3e52aac346c7c338d1a81f74f337c78a.jpg",
  },
  {
    title: "Outerwear",
    img: "https://i.pinimg.com/1200x/64/e8/ad/64e8adde471eafbce7b29d425cc596a5.jpg",
  },
  {
    title: "Formalwear",
    img: "https://i.pinimg.com/1200x/b4/b1/6e/b4b16eceba4463d24aaf85f881917fc4.jpg",
  },
  {
    title: "Casualwear",
    img: "https://i.pinimg.com/736x/6d/5f/eb/6d5febaa9daf4b70792472241620046e.jpg",
  },
  {
    title: "Accessories",
    img: "https://i.pinimg.com/736x/aa/f3/71/aaf371af4b70443607a3f05e1aea58a2.jpg",
  },
  {
    title: "Footwear",
    img: "https://i.pinimg.com/736x/d0/18/0b/d0180b3943da684196e36ff3fac86702.jpg",
  },
  {
    title: "Sportswear",
    img: "https://i.pinimg.com/1200x/89/c7/0f/89c70fe9000580bf03854889f0ccf021.jpg",
  },
  {
    title: "Party Wear",
    img: "https://i.pinimg.com/1200x/ca/d2/21/cad221bc6f76bd880f4acaa03d537c41.jpg",
  },
];

export default function TasteCardGrid() {
  const [activeCard, setActiveCard] = useState(0);

  return (
    <div className="flex w-full items-center justify-center overflow-x-auto px-4 py-8">
      <div className="flex gap-2">
        {categories.map((cat, index) => (
          <motion.div
            key={index}
            className="relative cursor-pointer overflow-hidden rounded-2xl"
            initial={{ width: "4rem", height: "20rem" }}
            animate={{
              width: activeCard === index ? "20rem" : "4rem",
              height: "20rem",
            }}
            transition={{ duration: 0.35, ease: "easeInOut" }}
            onHoverStart={() => setActiveCard(index)}
            onClick={() => setActiveCard(index)}
          >
            {/* Gradient Overlay */}
            <AnimatePresence>
              {activeCard === index && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"
                />
              )}
            </AnimatePresence>

            {/* Title */}
            <AnimatePresence>
              {activeCard === index && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  transition={{ duration: 0.4 }}
                  className="absolute bottom-4 left-0 w-full text-center"
                >
                  <h2 className="text-xl font-bold text-white drop-shadow-lg">
                    {cat.title}
                  </h2>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Image */}
            <img
              src={cat.img}
              alt={cat.title}
              className="h-full w-full object-cover"
            />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

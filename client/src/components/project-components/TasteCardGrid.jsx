import React from "react";

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
  return (
    <div className="mt-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 w-full px-2">
      {categories.map((cat, title) => (
        <div
          key={title}
          className="relative rounded-lg overflow-hidden shadow-md group hover:scale-105 transition-transform"
        >
          <img
            src={cat.img}
            alt={cat.title}
            className="w-full h-80 object-cover"
          />

          <div className="absolute bottom-0 w-full bg-gradient-to-t from-black/70 to-transparent p-2">
            <h2 className="text-lg font-semibold text-white text-center">
              {cat.title}
            </h2>
          </div>
        </div>
      ))}
    </div>
  );
}

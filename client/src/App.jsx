import React from "react";
import Navbar from "./components/project-components/Navbar";
import Approutes from "./Routes/Approutes";
import Footer from "./components/project-components/Footer";

export default function App() {
  return (
    <div>
      <Navbar />
      <Approutes />
      <Footer/>
    </div>
  );
}

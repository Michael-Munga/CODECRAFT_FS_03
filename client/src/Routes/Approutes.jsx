import React from 'react'
import { Route, Routes } from 'react-router-dom'
import LoginPage from '@/Pages/LoginPage'

export default function Approutes() {
  return (
    <div>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </div>
  );
}

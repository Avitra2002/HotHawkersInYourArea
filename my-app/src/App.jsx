import React from 'react'
import { Route, createBrowserRouter, createRoutesFromElements, RouterProvider } from "react-router-dom"
import MainLayout from './layouts/MainLayout'
import HomePage from './pages/HomePage'
import HeatmapPage from './pages/HeatmapPage'
import HawkersPage from './pages/HawkersPage'
import HawkerPage from './pages/HawkerPage'
import PreferencesPage from './pages/PreferencesPage'
import SignUpPage from './pages/SignUpPage'
import NotFoundPage from './pages/NotFoundPage'
import { PreferencesProvider } from './Contexts/PreferencesContext'
import { SignUpPageProvider } from './contexts/SignUpPageContext'

const router = createBrowserRouter(
  createRoutesFromElements(
  <>
    <Route path="/" element={<MainLayout />}>
      <Route index element={<HomePage />} />
      <Route path="/heatmap" element={<HeatmapPage />} />
      <Route path="/hawkers" element={<HawkersPage />} />
      <Route path="/preferences" element={<PreferencesPage />} />
      <Route path="/hawkers/:id" element={<HawkerPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Route>

    <Route path='/login' element={<SignUpPage />} />
  </>
  )
)

const App = () => {
  return (
    <SignUpPageProvider>
      <PreferencesProvider>
        <RouterProvider router={router} />
      </PreferencesProvider>
    </SignUpPageProvider>
  );
};
export default App
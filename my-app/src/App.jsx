import React from 'react'
import { useState } from 'react'
import { Route, createBrowserRouter, createRoutesFromElements, RouterProvider } from "react-router-dom"
import MainLayout from './layouts/MainLayout'
import HomePage from './pages/HomePage'
import HawkersPage from './pages/HawkersPage'
import NotFoundPage from './pages/NotFoundPage'
import HawkerPage, {hawkerLoader} from './pages/HawkerPage'
import PreferencesPage from './pages/PreferencesPage'
import SignUpPage from './pages/SignUpPage'
import { PreferencesProvider } from './Contexts/PreferencesContext'

const router = createBrowserRouter(
  createRoutesFromElements(
  <>
    <Route path="/" element={<MainLayout />}>
      <Route index element={<HomePage />} />
      <Route path="/hawkers" element={<HawkersPage />} />
      <Route path="/preferences" element={<PreferencesPage />} />
      <Route path="/hawkers/:id" element={<HawkerPage />} loader={hawkerLoader}/>
      <Route path="*" element={<NotFoundPage />} />
      <Route path='/login' element={<SignUpPage />} />
    </Route>
  </>
  )
)

const App = () => {
  return (
    <PreferencesProvider>
      <RouterProvider router={router} />
    </PreferencesProvider>
  );
};
export default App
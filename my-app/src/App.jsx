import React from 'react'
import { Route, createBrowserRouter, createRoutesFromElements, RouterProvider } from "react-router-dom"
import MainLayout from './layouts/MainLayout'
import HomePage from './pages/HomePage'
import HawkersPage from './pages/HawkersPage'
import NotFoundPage from './pages/NotFoundPage'
import HawkerPage, {hawkerLoader} from './pages/HawkerPage'
import PreferencesPage from './pages/PreferencesPage'

const router = createBrowserRouter(
  createRoutesFromElements(
  <Route path="/" element={<MainLayout />}>
    <Route index element={<HomePage />} />
    <Route path="/hawkers" element={<HawkersPage />} />
    <Route path="/preferences" element={<PreferencesPage />} />
    <Route path="/hawkers/:id" element={<HawkerPage />} loader={hawkerLoader}/>
    <Route path="*" element={<NotFoundPage />} />
  </Route>
  )
)

const App = () => {
  return <RouterProvider router={router} />
}

export default App
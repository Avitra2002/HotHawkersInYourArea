import React from 'react'
import Hero from "../components/Hero"
import StatusBar from '../components/StatusBar'
import Widget from "../components/Widget"
import HawkerListings from "../components/HawkerListings"
import ViewAllHawkers from "../components/ViewAllStores"
import { PreferencesProvider } from '../Contexts/PreferencesContext'

const HomePage = () => {
  return (
    <>
      <Hero />
      <StatusBar />
      <PreferencesProvider>
        <Widget />
      </PreferencesProvider>
      <HawkerListings isHome = {true}/>
      <ViewAllHawkers />
    </>
  )
}

export default HomePage
import React from 'react'
import Hero from "../components/Hero"
import StatusBar from '../components/StatusBar'
import Widget from "../components/Widget"
import HawkerListings from "../components/HawkerListings"
import ViewAllHawkers from "../components/ViewAllStores"

const HomePage = () => {
  return (
    <>
      <Hero />
      <StatusBar />
      <Widget />
      <HawkerListings isHome = {true}/>
      <ViewAllHawkers />
    </>
  )
}

export default HomePage
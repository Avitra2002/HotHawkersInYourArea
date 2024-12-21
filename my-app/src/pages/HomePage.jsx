import React from 'react'
import Hero from "../components/Hero"
import StatusBar from '../components/StatusBar'
import Widget from "../components/Widget"
import HawkerListings from "../components/HawkerListings"
import ViewAllHawkers from "../components/ViewAllStores"
import PredictionWidget from '../components/PredictionWidget';

const HomePage = () => {
  return (
    <>
      <Hero />
      <StatusBar />
      <PredictionWidget />
      <Widget />
      <HawkerListings isHome = {true}/>
      <ViewAllHawkers />
    </>
  )
}

export default HomePage
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
      <div className="h-full min-h-[600px] w-full flex items-center justify-center bg-gray-50 py-8">
        <div className="px-4 w-full md:px-8 lg:px-0">
          <div className="w-full mx-auto max-w-sm sm:max-w-md md:max-w-2xl lg:max-w-4xl">
            <PredictionWidget />
          </div>
        </div>
      </div>
      <Widget />
      <HawkerListings isHome = {true}/>
      <ViewAllHawkers />
    </>
  )
}

export default HomePage